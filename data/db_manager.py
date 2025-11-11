"""
Database Manager
Handles all database operations with connection pooling
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "data/restaurants.db"):
        self.db_path = db_path
        self._initialize_users_table()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_users_table(self):
        """Create users table if it doesn't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    full_name TEXT,
                    phone TEXT,
                    google_id TEXT UNIQUE,
                    auth_provider TEXT DEFAULT 'local',
                    profile_picture TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add user_id column to reservations if it doesn't exist
            cursor.execute("PRAGMA table_info(reservations)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'user_id' not in columns:
                cursor.execute('ALTER TABLE reservations ADD COLUMN user_id INTEGER')
            
            conn.commit()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = "", phone: str = "") -> Dict:
        """Create a new user account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                password_hash = self._hash_password(password)
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, phone)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, full_name, phone))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "username": username,
                    "message": "Account created successfully!"
                }
            except sqlite3.IntegrityError as e:
                if 'username' in str(e):
                    return {"success": False, "error": "Username already exists"}
                elif 'email' in str(e):
                    return {"success": False, "error": "Email already registered"}
                else:
                    return {"success": False, "error": "Registration failed"}
    
    def authenticate_user(self, username: str, password: str) -> Dict:
        """Authenticate user login"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            cursor.execute('''
                SELECT id, username, email, full_name, phone
                FROM users
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "success": True,
                    "user": {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "full_name": row[3],
                        "phone": row[4]
                    }
                }
            else:
                return {"success": False, "error": "Invalid username or password"}
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user details by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, full_name, phone, profile_picture, auth_provider
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_or_get_google_user(self, google_id: str, email: str, full_name: str, 
                                   profile_picture: str = None) -> Dict:
        """Create or get user from Google OAuth"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists with this Google ID
            cursor.execute('SELECT id, username, email, full_name, phone, profile_picture FROM users WHERE google_id = ?', (google_id,))
            row = cursor.fetchone()
            
            if row:
                # User exists, return their info
                return {
                    "success": True,
                    "user": {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "full_name": row[3],
                        "phone": row[4],
                        "profile_picture": row[5],
                        "auth_provider": "google"
                    }
                }
            
            # Check if email already exists (user might have registered with password)
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            existing = cursor.fetchone()
            
            if existing:
                # Link Google account to existing user
                cursor.execute('''
                    UPDATE users 
                    SET google_id = ?, profile_picture = ?, auth_provider = 'google'
                    WHERE email = ?
                ''', (google_id, profile_picture, email))
                conn.commit()
                
                cursor.execute('SELECT id, username, email, full_name, phone, profile_picture FROM users WHERE email = ?', (email,))
                row = cursor.fetchone()
                
                return {
                    "success": True,
                    "user": {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "full_name": row[3],
                        "phone": row[4],
                        "profile_picture": row[5],
                        "auth_provider": "google"
                    },
                    "message": "Google account linked to existing account"
                }
            
            # Create new user
            username = email.split('@')[0]  # Use email prefix as username
            
            # Make username unique if needed
            base_username = username
            counter = 1
            while True:
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, google_id, auth_provider, profile_picture)
                    VALUES (?, ?, NULL, ?, ?, 'google', ?)
                ''', (username, email, full_name, google_id, profile_picture))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "username": username,
                        "email": email,
                        "full_name": full_name,
                        "phone": None,
                        "profile_picture": profile_picture,
                        "auth_provider": "google"
                    },
                    "message": "Account created with Google"
                }
            except Exception as e:
                return {"success": False, "error": f"Failed to create user: {str(e)}"}
    
    def get_restaurants(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get restaurants with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM restaurants WHERE 1=1"
            params = []
            
            if filters:
                if 'cuisine' in filters:
                    query += " AND cuisine = ?"
                    params.append(filters['cuisine'])
                
                if 'location' in filters:
                    query += " AND location LIKE ?"
                    params.append(f"%{filters['location']}%")
                
                if 'min_rating' in filters:
                    query += " AND rating >= ?"
                    params.append(filters['min_rating'])
                
                if 'price_range' in filters:
                    query += " AND price_range = ?"
                    params.append(filters['price_range'])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_restaurant_by_id(self, restaurant_id: int) -> Optional[Dict]:
        """Get a specific restaurant by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants WHERE id = ?", (restaurant_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def check_availability(self, restaurant_id: int, date: str, time: str, party_size: int) -> Dict:
        """Check if restaurant has availability for given parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT seats_available FROM availability
                WHERE restaurant_id = ? AND date = ? AND time = ?
            ''', (restaurant_id, date, time))
            
            row = cursor.fetchone()
            
            if not row:
                return {"available": False, "reason": "No slots for this time"}
            
            seats_available = row[0]
            
            if seats_available >= party_size:
                return {
                    "available": True,
                    "seats_available": seats_available,
                    "restaurant_id": restaurant_id,
                    "date": date,
                    "time": time
                }
            else:
                return {
                    "available": False,
                    "reason": f"Only {seats_available} seats available, need {party_size}",
                    "seats_available": seats_available
                }
    
    def create_reservation(self, restaurant_id: int, user_name: str, date: str, 
                          time: str, party_size: int, user_id: Optional[int] = None,
                          user_email: Optional[str] = None,
                          special_requests: Optional[str] = None) -> Dict:
        """Create a new reservation with concurrent booking prevention"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # CRITICAL: Use transaction with immediate lock to prevent race conditions
            cursor.execute("BEGIN IMMEDIATE")
            
            try:
                # Check availability with lock (prevents double booking)
                cursor.execute('''
                    SELECT seats_available FROM availability
                    WHERE restaurant_id = ? AND date = ? AND time = ?
                ''', (restaurant_id, date, time))
                
                row = cursor.fetchone()
                
                if not row:
                    conn.rollback()
                    return {"success": False, "error": "No availability slots for this time"}
                
                seats_available = row[0]
                
                # Check if enough seats (with lock held)
                if seats_available < party_size:
                    conn.rollback()
                    return {
                        "success": False, 
                        "error": f"Only {seats_available} seats available, need {party_size}"
                    }
                
                # Create reservation
                cursor.execute('''
                    INSERT INTO reservations 
                    (restaurant_id, user_id, user_name, user_email, date, time, party_size, status, special_requests)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed', ?)
                ''', (restaurant_id, user_id, user_name, user_email, date, time, party_size, special_requests))
                
                reservation_id = cursor.lastrowid
                
                # Update availability atomically
                cursor.execute('''
                    UPDATE availability 
                    SET seats_available = seats_available - ?
                    WHERE restaurant_id = ? AND date = ? AND time = ?
                ''', (party_size, restaurant_id, date, time))
                
                # Commit transaction (releases lock)
                    # Commit transaction (releases lock)
                conn.commit()
                
                # Get restaurant details
                restaurant = self.get_restaurant_by_id(restaurant_id)
                
                return {
                    "success": True,
                    "reservation_id": reservation_id,
                    "confirmation_code": f"GF-{reservation_id:04d}",
                    "restaurant_name": restaurant['name'],
                    "date": date,
                    "time": time,
                    "party_size": party_size
                }
                
            except Exception as e:
                conn.rollback()
                return {
                    "success": False,
                    "error": f"Booking failed: {str(e)}"
                }
    
    def cancel_reservation(self, reservation_id: int) -> Dict:
        """Cancel a reservation and restore availability"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get reservation details
            cursor.execute('''
                SELECT restaurant_id, date, time, party_size, status
                FROM reservations WHERE id = ?
            ''', (reservation_id,))
            
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Reservation not found"}
            
            restaurant_id, date, time, party_size, status = row
            
            if status == 'cancelled':
                return {"success": False, "error": "Reservation already cancelled"}
            
            # Update reservation status
            cursor.execute('''
                UPDATE reservations SET status = 'cancelled'
                WHERE id = ?
            ''', (reservation_id,))
            
            # Restore availability
            cursor.execute('''
                UPDATE availability 
                SET seats_available = seats_available + ?
                WHERE restaurant_id = ? AND date = ? AND time = ?
            ''', (party_size, restaurant_id, date, time))
            
            conn.commit()
            
            return {
                "success": True,
                "reservation_id": reservation_id,
                "message": "Reservation cancelled successfully"
            }
    
    def get_user_reservations(self, user_name: str = None, user_id: int = None) -> List[Dict]:
        """Get all reservations for a user (by name or ID)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT r.*, rest.name as restaurant_name, rest.location
                    FROM reservations r
                    JOIN restaurants rest ON r.restaurant_id = rest.id
                    WHERE r.user_id = ? AND r.status = 'confirmed'
                    ORDER BY r.date, r.time
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT r.*, rest.name as restaurant_name, rest.location
                    FROM reservations r
                    JOIN restaurants rest ON r.restaurant_id = rest.id
                    WHERE r.user_name = ? AND r.status = 'confirmed'
                    ORDER BY r.date, r.time
                ''', (user_name,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_available_times(self, restaurant_id: int, date: str, party_size: int) -> List[str]:
        """Get all available time slots for a restaurant on a given date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT time, seats_available FROM availability
                WHERE restaurant_id = ? AND date = ? AND seats_available >= ?
                ORDER BY time
            ''', (restaurant_id, date, party_size))
            
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    
    def get_analytics(self) -> Dict:
        """Get booking analytics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total reservations
            cursor.execute("SELECT COUNT(*) FROM reservations WHERE status = 'confirmed'")
            total_reservations = cursor.fetchone()[0]
            
            # Popular cuisines
            cursor.execute('''
                SELECT rest.cuisine, COUNT(*) as count
                FROM reservations r
                JOIN restaurants rest ON r.restaurant_id = rest.id
                WHERE r.status = 'confirmed'
                GROUP BY rest.cuisine
                ORDER BY count DESC
                LIMIT 5
            ''')
            popular_cuisines = [{"cuisine": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Busiest times
            cursor.execute('''
                SELECT time, COUNT(*) as count
                FROM reservations
                WHERE status = 'confirmed'
                GROUP BY time
                ORDER BY count DESC
                LIMIT 5
            ''')
            busiest_times = [{"time": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            return {
                "total_reservations": total_reservations,
                "popular_cuisines": popular_cuisines,
                "busiest_times": busiest_times
            }
