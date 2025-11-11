"""
Fix database: Keep only first 50 restaurants and update availability to start from today
"""

import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('data/restaurants.db')
cursor = conn.cursor()

print("="*70)
print("FIXING DATABASE")
print("="*70)

# Step 1: Delete all restaurants except first 50
print("\n1. Cleaning restaurants...")
cursor.execute('SELECT MIN(id) FROM restaurants')
min_id = cursor.fetchone()[0]
keep_until = min_id + 49  # Keep 50 restaurants

print(f"   Keeping restaurant IDs: {min_id} to {keep_until}")

cursor.execute('DELETE FROM restaurants WHERE id > ?', (keep_until,))
deleted_restaurants = cursor.rowcount
print(f"   Deleted {deleted_restaurants} restaurants")

# Step 2: Delete availability for deleted restaurants
cursor.execute('DELETE FROM availability WHERE restaurant_id > ?', (keep_until,))
deleted_avail = cursor.rowcount
print(f"   Deleted {deleted_avail:,} availability rows")

# Step 3: Delete reservations for deleted restaurants
cursor.execute('DELETE FROM reservations WHERE restaurant_id > ?', (keep_until,))
deleted_res = cursor.rowcount
print(f"   Deleted {deleted_res} reservations")

conn.commit()

# Step 4: Regenerate availability for today + 30 days
print("\n2. Regenerating availability...")

# Delete all existing availability
cursor.execute('DELETE FROM availability')
print(f"   Cleared all availability")

# Get remaining restaurants
cursor.execute('SELECT id, capacity FROM restaurants')
restaurants = cursor.fetchall()
print(f"   Found {len(restaurants)} restaurants")

# Generate dates (today + 30 days)
today = datetime.now().date()
dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
print(f"   Date range: {dates[0]} to {dates[-1]}")

# Time slots (11 AM to 10 PM, every 30 minutes)
time_slots = []
for hour in range(11, 22):  # 11 AM to 9 PM
    time_slots.append(f"{hour:02d}:00")
    time_slots.append(f"{hour:02d}:30")
time_slots.append("22:00")  # 10 PM
print(f"   Time slots per day: {len(time_slots)}")

# Insert availability
inserted = 0
for restaurant_id, capacity in restaurants:
    for date in dates:
        for time in time_slots:
            # 80-95% of capacity available
            seats = int(capacity * random.uniform(0.80, 0.95))
            cursor.execute('''
                INSERT INTO availability (restaurant_id, date, time, seats_available)
                VALUES (?, ?, ?, ?)
            ''', (restaurant_id, date, time, seats))
            inserted += 1

conn.commit()
print(f"   Inserted {inserted:,} availability rows")

# Verify
cursor.execute('SELECT COUNT(*) FROM restaurants')
total_restaurants = cursor.fetchone()[0]

cursor.execute('SELECT MIN(id), MAX(id) FROM restaurants')
id_range = cursor.fetchone()

cursor.execute('SELECT COUNT(*) FROM availability')
total_avail = cursor.fetchone()[0]

cursor.execute('SELECT MIN(date), MAX(date) FROM availability')
date_range = cursor.fetchone()

print("\n" + "="*70)
print("FINAL STATE:")
print("="*70)
print(f"Restaurants: {total_restaurants}")
print(f"Restaurant ID range: {id_range[0]} to {id_range[1]}")
print(f"Availability rows: {total_avail:,}")
print(f"Date range: {date_range[0]} to {date_range[1]}")
print(f"Today: {datetime.now().strftime('%Y-%m-%d')}")
print("="*70)

conn.close()

print("\n✅ Database fixed successfully!")
