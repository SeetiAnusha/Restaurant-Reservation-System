"""
Restaurant Data Generator
Creates realistic synthetic data for 100 restaurant locations
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Configuration
NUM_RESTAURANTS = 100
DAYS_AHEAD = 30

# Data pools for realistic variety
CUISINES = [
    "Italian", "Chinese", "Japanese", "Mexican", "Indian", 
    "Thai", "French", "American", "Mediterranean", "Korean",
    "Vietnamese", "Greek", "Spanish", "Brazilian", "Lebanese"
]

CITIES = [
    "New York, NY", "Los Angeles, CA", "Chicago, IL", 
    "Houston, TX", "Phoenix, AZ", "Philadelphia, PA",
    "San Antonio, TX", "San Diego, CA", "Dallas, TX", "Austin, TX",
    "Koramangala, Bangalore", "Indiranagar, Bangalore", "Whitefield, Bangalore",
    "HSR Layout, Bangalore", "Jayanagar, Bangalore", "MG Road, Bangalore",
    "Electronic City, Bangalore", "Marathahalli, Bangalore", "BTM Layout, Bangalore",
    "JP Nagar, Bangalore", "Malleshwaram, Bangalore", "Rajajinagar, Bangalore",
    "Yelahanka, Bangalore", "Bannerghatta Road, Bangalore", "Sarjapur Road, Bangalore"
]

PRICE_RANGES = ["$", "$$", "$$$", "$$$$"]

FEATURES = [
    "Outdoor Seating", "Kid-Friendly", "Romantic", "Live Music",
    "Private Dining", "Bar", "Vegan Options", "Gluten-Free Options",
    "Wheelchair Accessible", "Parking Available", "Pet-Friendly",
    "Late Night", "Brunch", "Wine Bar", "Craft Cocktails"
]

RESTAURANT_NAMES = [
    "Bella Notte", "Golden Dragon", "Sakura Garden", "El Mariachi",
    "Spice Palace", "Bangkok Bistro", "Le Petit Café", "The Steakhouse",
    "Olive Grove", "Seoul Kitchen", "Pho House", "Taverna Blue",
    "Casa Barcelona", "Churrasco Grill", "Cedar & Spice"
]

def create_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect('data/restaurants.db')
    cursor = conn.cursor()
    
    # Restaurants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            opening_hours TEXT NOT NULL,
            rating REAL NOT NULL,
            price_range TEXT NOT NULL,
            special_features TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Reservations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            user_email TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            party_size INTEGER NOT NULL,
            status TEXT DEFAULT 'confirmed',
            special_requests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
        )
    ''')
    
    # Availability slots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            seats_available INTEGER NOT NULL,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (id),
            UNIQUE(restaurant_id, date, time)
        )
    ''')
    
    conn.commit()
    return conn

def generate_opening_hours():
    """Generate realistic opening hours"""
    weekday_open = random.choice(["10:00", "11:00", "11:30"])
    weekday_close = random.choice(["21:00", "22:00", "23:00"])
    weekend_open = random.choice(["09:00", "10:00", "11:00"])
    weekend_close = random.choice(["22:00", "23:00", "00:00"])
    
    hours = {
        "Monday": f"{weekday_open}-{weekday_close}",
        "Tuesday": f"{weekday_open}-{weekday_close}",
        "Wednesday": f"{weekday_open}-{weekday_close}",
        "Thursday": f"{weekday_open}-{weekday_close}",
        "Friday": f"{weekday_open}-{weekend_close}",
        "Saturday": f"{weekend_open}-{weekend_close}",
        "Sunday": f"{weekend_open}-{weekday_close}"
    }
    
    # Some restaurants closed on Monday
    if random.random() < 0.2:
        hours["Monday"] = "Closed"
    
    return json.dumps(hours)

def generate_availability_slots(restaurant_id, capacity, conn):
    """Generate availability slots for next 30 days"""
    cursor = conn.cursor()
    
    # Time slots (11am to 10pm, every 30 minutes)
    time_slots = []
    for hour in range(11, 22):
        time_slots.append(f"{hour:02d}:00")
        time_slots.append(f"{hour:02d}:30")
    
    for day_offset in range(DAYS_AHEAD):
        date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        day_of_week = (datetime.now() + timedelta(days=day_offset)).weekday()
        
        # Weekend multiplier (busier on Fri/Sat/Sun)
        is_weekend = day_of_week >= 4
        base_occupancy = 0.7 if is_weekend else 0.5
        
        for time_slot in time_slots:
            hour = int(time_slot.split(':')[0])
            
            # Peak dinner hours (6-9pm) are busier
            if 18 <= hour <= 21:
                occupancy_rate = base_occupancy + random.uniform(0.1, 0.3)
            else:
                occupancy_rate = base_occupancy + random.uniform(-0.2, 0.1)
            
            occupancy_rate = max(0.1, min(0.95, occupancy_rate))
            
            # Calculate available seats
            booked_seats = int(capacity * occupancy_rate)
            available_seats = capacity - booked_seats
            
            cursor.execute('''
                INSERT INTO availability (restaurant_id, date, time, seats_available)
                VALUES (?, ?, ?, ?)
            ''', (restaurant_id, date, time_slot, available_seats))
    
    conn.commit()

def generate_restaurants(conn):
    """Generate restaurant data"""
    cursor = conn.cursor()
    
    used_names = set()
    
    for i in range(NUM_RESTAURANTS):
        # Generate unique name
        base_name = random.choice(RESTAURANT_NAMES)
        suffix = random.choice(["", " Downtown", " Midtown", " Uptown", " West", " East"])
        name = base_name + suffix
        
        # Ensure uniqueness
        counter = 1
        while name in used_names:
            name = f"{base_name} {counter}"
            counter += 1
        used_names.add(name)
        
        # Generate restaurant attributes
        location = random.choice(CITIES)
        cuisine = random.choice(CUISINES)
        capacity = random.choice([30, 40, 50, 60, 80, 100, 120, 150, 200])
        opening_hours = generate_opening_hours()
        rating = round(random.uniform(3.5, 5.0), 1)
        price_range = random.choice(PRICE_RANGES)
        
        # Select 3-5 special features
        num_features = random.randint(3, 5)
        special_features = json.dumps(random.sample(FEATURES, num_features))
        
        description = f"A delightful {cuisine} restaurant in {location} offering authentic cuisine and warm hospitality."
        
        # Insert restaurant
        cursor.execute('''
            INSERT INTO restaurants 
            (name, location, cuisine, capacity, opening_hours, rating, price_range, special_features, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, location, cuisine, capacity, opening_hours, rating, price_range, special_features, description))
        
        restaurant_id = cursor.lastrowid
        
        # Generate availability slots
        generate_availability_slots(restaurant_id, capacity, conn)
        
        if (i + 1) % 10 == 0:
            print(f"Generated {i + 1}/{NUM_RESTAURANTS} restaurants...")
    
    conn.commit()
    print(f"\n✅ Successfully generated {NUM_RESTAURANTS} restaurants with availability data!")

def add_sample_reservations(conn):
    """Add some sample reservations for testing"""
    cursor = conn.cursor()
    
    sample_reservations = [
        (1, "John Doe", "john@example.com", "2024-11-15", "19:00", 4, "confirmed", "Window seat preferred"),
        (2, "Jane Smith", "jane@example.com", "2024-11-16", "20:00", 2, "confirmed", None),
        (3, "Bob Johnson", "bob@example.com", "2024-11-17", "18:30", 6, "confirmed", "Birthday celebration"),
    ]
    
    for reservation in sample_reservations:
        cursor.execute('''
            INSERT INTO reservations 
            (restaurant_id, user_name, user_email, date, time, party_size, status, special_requests)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', reservation)
        
        # Update availability
        cursor.execute('''
            UPDATE availability 
            SET seats_available = seats_available - ?
            WHERE restaurant_id = ? AND date = ? AND time = ?
        ''', (reservation[5], reservation[0], reservation[3], reservation[4]))
    
    conn.commit()
    print(f"✅ Added {len(sample_reservations)} sample reservations")

def main():
    """Main execution"""
    print("🏗️  Creating database schema...")
    conn = create_database()
    
    # Clear old restaurant and availability data
    print("🧹 Clearing old data...")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM availability")
    cursor.execute("DELETE FROM reservations WHERE restaurant_id NOT IN (SELECT id FROM restaurants WHERE name LIKE 'GoodFoods%')")
    cursor.execute("DELETE FROM restaurants")
    conn.commit()
    print("✅ Old data cleared")
    
    print("🎲 Generating restaurant data...")
    generate_restaurants(conn)
    
    print("📝 Adding sample reservations...")
    add_sample_reservations(conn)
    
    # Display summary
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    restaurant_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM availability")
    slot_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reservations")
    reservation_count = cursor.fetchone()[0]
    
    print("\n" + "="*50)
    print("📊 DATABASE SUMMARY")
    print("="*50)
    print(f"Restaurants: {restaurant_count}")
    print(f"Availability Slots: {slot_count}")
    print(f"Sample Reservations: {reservation_count}")
    print("="*50)
    
    conn.close()
    print("\n✨ Data generation complete! Database ready at: data/restaurants.db")

if __name__ == "__main__":
    main()
