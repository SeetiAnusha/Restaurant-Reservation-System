"""
Create proper database with 50 GoodFoods restaurants in Bangalore
"""

import sqlite3
from datetime import datetime, timedelta
import random
import json

conn = sqlite3.connect('data/restaurants.db')
cursor = conn.cursor()

print("="*70)
print("CREATING PROPER DATABASE")
print("="*70)

# Step 1: Clear existing data
print("\n1. Clearing existing data...")
cursor.execute('DELETE FROM availability')
cursor.execute('DELETE FROM reservations WHERE restaurant_id > 0')
cursor.execute('DELETE FROM restaurants')
conn.commit()
print("   ✅ Cleared")

# Step 2: Create 50 GoodFoods restaurants
print("\n2. Creating 50 GoodFoods restaurants...")

cuisines = ['Italian', 'Chinese', 'Thai', 'Indian', 'Mexican', 'Japanese', 'French', 
            'American', 'Korean', 'Mediterranean']
locations = ['Koramangala', 'Indiranagar', 'Whitefield', 'JP Nagar', 'HSR Layout',
             'Jayanagar', 'MG Road', 'Electronic City', 'Marathahalli', 'BTM Layout']

features_options = [
    ['Outdoor Seating', 'Bar', 'Live Music'],
    ['Private Dining', 'Vegan Options', 'Gluten-Free Options'],
    ['Kid-Friendly', 'Wheelchair Accessible', 'Parking Available'],
    ['Romantic', 'Brunch', 'Late Night'],
    ['Wine Bar', 'Craft Cocktails', 'Pet-Friendly']
]

for i in range(1, 51):
    cuisine = cuisines[i % len(cuisines)]
    location = locations[i % len(locations)]
    
    name = f"GoodFoods - {cuisine} - {location}"
    rating = round(random.uniform(3.5, 5.0), 1)
    price_range = random.choice(['$', '$$', '$$$', '$$$$'])
    capacity = random.choice([30, 50, 80, 100, 120, 150, 200])
    features = random.choice(features_options)
    
    cursor.execute('''
        INSERT INTO restaurants (id, name, cuisine, location, rating, price_range, capacity, special_features, description, opening_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        i,
        name,
        cuisine,
        f"{location}, Bangalore",
        rating,
        price_range,
        capacity,
        json.dumps(features),
        f"A delightful {cuisine} restaurant in {location}, Bangalore offering authentic cuisine and warm hospitality.",
        "11:00 AM - 10:00 PM"
    ))

conn.commit()
print(f"   ✅ Created 50 restaurants (IDs 1-50)")

# Step 3: Create availability
print("\n3. Creating availability...")

# Dates: today + 30 days
today = datetime.now().date()
dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]

# Time slots: 11 AM to 10 PM
time_slots = []
for hour in range(11, 22):
    time_slots.append(f"{hour:02d}:00")
    time_slots.append(f"{hour:02d}:30")
time_slots.append("22:00")

print(f"   Date range: {dates[0]} to {dates[-1]}")
print(f"   Time slots: {len(time_slots)} per day")

# Get all restaurants
cursor.execute('SELECT id, capacity FROM restaurants')
restaurants = cursor.fetchall()

inserted = 0
for restaurant_id, capacity in restaurants:
    for date in dates:
        for time in time_slots:
            seats = int(capacity * random.uniform(0.80, 0.95))
            cursor.execute('''
                INSERT INTO availability (restaurant_id, date, time, seats_available)
                VALUES (?, ?, ?, ?)
            ''', (restaurant_id, date, time, seats))
            inserted += 1

conn.commit()
print(f"   ✅ Created {inserted:,} availability rows")

# Verify
cursor.execute('SELECT COUNT(*) FROM restaurants')
total_restaurants = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM availability')
total_avail = cursor.fetchone()[0]

cursor.execute('SELECT id, name, location, rating FROM restaurants LIMIT 10')
print("\n" + "="*70)
print("SAMPLE RESTAURANTS:")
print("="*70)
for row in cursor.fetchall():
    print(f"ID: {row[0]}, {row[1]}, {row[2]}, Rating: {row[3]}")

print("\n" + "="*70)
print("FINAL STATE:")
print("="*70)
print(f"Restaurants: {total_restaurants} (IDs 1-50)")
print(f"Availability rows: {total_avail:,}")
print(f"Date range: {dates[0]} to {dates[-1]}")
print("="*70)

conn.close()

print("\n✅ Database created successfully!")
