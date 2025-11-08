"""
Database Manager
Handles all database operations with connection pooling
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "data/restaurants.db"):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
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
                          time: str, party_size: int, user_email: Optional[str] = None,
                          special_requests: Optional[str] = None) -> Dict:
        """Create a new reservation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check availability first
            availability = self.check_availability(restaurant_id, date, time, party_size)
            if not availability["available"]:
                return {"success": False, "error": availability["reason"]}
            
            # Create reservation
            cursor.execute('''
                INSERT INTO reservations 
                (restaurant_id, user_name, user_email, date, time, party_size, status, special_requests)
                VALUES (?, ?, ?, ?, ?, ?, 'confirmed', ?)
            ''', (restaurant_id, user_name, user_email, date, time, party_size, special_requests))
            
            reservation_id = cursor.lastrowid
            
            # Update availability
            cursor.execute('''
                UPDATE availability 
                SET seats_available = seats_available - ?
                WHERE restaurant_id = ? AND date = ? AND time = ?
            ''', (party_size, restaurant_id, date, time))
            
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
    
    def get_user_reservations(self, user_name: str) -> List[Dict]:
        """Get all reservations for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
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
