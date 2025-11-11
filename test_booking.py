from data.db_manager import DatabaseManager

db = DatabaseManager()

# Get a Korean restaurant in Bangalore
import sqlite3
conn = sqlite3.connect('data/restaurants.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, name FROM restaurants 
    WHERE cuisine = 'Korean' AND location LIKE '%Bangalore%' 
    LIMIT 1
""")
rest = cursor.fetchone()
rest_id, rest_name = rest

print(f"Testing booking for: {rest_name} (ID: {rest_id})")
print(f"Date: 2025-11-11")
print(f"Time: 20:00")
print(f"Party size: 4")

# Check availability first
cursor.execute("""
    SELECT seats_available FROM availability
    WHERE restaurant_id = ? AND date = ? AND time = ?
""", (rest_id, '2025-11-11', '20:00'))

avail = cursor.fetchone()
print(f"\nSeats available: {avail[0] if avail else 'NO SLOT FOUND'}")

conn.close()

# Try to book
result = db.create_reservation(
    restaurant_id=rest_id,
    user_name="Test User",
    user_id=1,
    date="2025-11-11",
    time="20:00",
    party_size=4
)

print(f"\nBooking result:")
print(f"Success: {result.get('success')}")
if result.get('success'):
    print(f"Confirmation: {result.get('confirmation_code')}")
else:
    print(f"Error: {result.get('error')}")
