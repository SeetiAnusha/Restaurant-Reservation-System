"""
Reduce database to only 50 restaurants
"""

import sqlite3

conn = sqlite3.connect('data/restaurants.db')
cursor = conn.cursor()

print("="*70)
print("REDUCING DATABASE TO 50 RESTAURANTS")
print("="*70)

# Check current count
cursor.execute('SELECT COUNT(*) FROM restaurants')
current_count = cursor.fetchone()[0]
print(f"\nCurrent restaurants: {current_count}")

cursor.execute('SELECT COUNT(*) FROM availability')
current_avail = cursor.fetchone()[0]
print(f"Current availability rows: {current_avail:,}")

# Get first 50 restaurant IDs
cursor.execute('SELECT id FROM restaurants ORDER BY id LIMIT 50')
keep_ids = [row[0] for row in cursor.fetchall()]

print(f"\nKeeping restaurant IDs: {keep_ids[0]} to {keep_ids[-1]}")

# Delete restaurants not in the first 50
cursor.execute('DELETE FROM restaurants WHERE id > 50')
deleted_restaurants = cursor.rowcount
print(f"Deleted {deleted_restaurants} restaurants")

# Delete availability for restaurants not in first 50
cursor.execute('DELETE FROM availability WHERE restaurant_id > 50')
deleted_availability = cursor.rowcount
print(f"Deleted {deleted_availability:,} availability rows")

# Delete reservations for restaurants not in first 50
cursor.execute('DELETE FROM reservations WHERE restaurant_id > 50')
deleted_reservations = cursor.rowcount
print(f"Deleted {deleted_reservations} reservations")

conn.commit()

# Check new counts
cursor.execute('SELECT COUNT(*) FROM restaurants')
new_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM availability')
new_avail = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM reservations')
new_reservations = cursor.fetchone()[0]

print("\n" + "="*70)
print("AFTER REDUCTION:")
print("="*70)
print(f"Restaurants: {new_count}")
print(f"Availability rows: {new_avail:,}")
print(f"Reservations: {new_reservations}")
print("="*70)

conn.close()

print("\n✅ Database reduced to 50 restaurants successfully!")
