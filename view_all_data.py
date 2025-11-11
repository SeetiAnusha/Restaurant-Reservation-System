"""
Complete Database Viewer
Shows ALL data: Users, Restaurants, Reservations, Availability
Run: python view_all_data.py
"""

import sqlite3
import os
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = "data/restaurants.db"

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def print_section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

# ============================================================================
# USERS
# ============================================================================
print_section("👥 USERS")

cursor.execute("SELECT id, username, email, full_name, phone, created_at FROM users")
users = cursor.fetchall()

if users:
    print(f"\n{'ID':<5} {'Username':<15} {'Email':<30} {'Full Name':<20} {'Phone':<15} {'Created'}")
    print("-" * 110)
    for user in users:
        user_id, username, email, full_name, phone, created = user
        print(f"{user_id:<5} {username:<15} {email:<30} {full_name or 'N/A':<20} {phone or 'N/A':<15} {created}")
    print(f"\n📊 Total: {len(users)} users")
else:
    print("⚠️  No users yet")

# ============================================================================
# RESTAURANTS
# ============================================================================
print_section("🍽️  RESTAURANTS (First 20)")

cursor.execute("""
    SELECT id, name, cuisine, location, rating, price_range, capacity
    FROM restaurants
    LIMIT 20
""")
restaurants = cursor.fetchall()

print(f"\n{'ID':<5} {'Name':<40} {'Cuisine':<15} {'Location':<25} {'Rating':<8} {'Price':<7} {'Capacity'}")
print("-" * 130)
for r in restaurants:
    print(f"{r[0]:<5} {r[1]:<40} {r[2]:<15} {r[3]:<25} {r[4]:<8} {r[5]:<7} {r[6]}")

cursor.execute("SELECT COUNT(*) FROM restaurants")
print(f"\n📊 Total: {cursor.fetchone()[0]} restaurants")

# ============================================================================
# RESERVATIONS
# ============================================================================
print_section("📅 RESERVATIONS")

cursor.execute("""
    SELECT 
        r.id,
        r.user_name,
        rest.name,
        r.date,
        r.time,
        r.party_size,
        r.status
    FROM reservations r
    JOIN restaurants rest ON r.restaurant_id = rest.id
    ORDER BY r.date DESC, r.time DESC
    LIMIT 20
""")
reservations = cursor.fetchall()

if reservations:
    print(f"\n{'ID':<5} {'User':<20} {'Restaurant':<40} {'Date':<12} {'Time':<8} {'Party':<7} {'Status'}")
    print("-" * 120)
    for res in reservations:
        print(f"{res[0]:<5} {res[1]:<20} {res[2]:<40} {res[3]:<12} {res[4]:<8} {res[5]:<7} {res[6]}")
    
    cursor.execute("SELECT COUNT(*) FROM reservations WHERE status='confirmed'")
    confirmed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reservations WHERE status='cancelled'")
    cancelled = cursor.fetchone()[0]
    
    print(f"\n📊 Total: {len(reservations)} shown | Confirmed: {confirmed} | Cancelled: {cancelled}")
else:
    print("⚠️  No reservations yet")

# ============================================================================
# AVAILABILITY
# ============================================================================
print_section("⏰ AVAILABILITY (Sample)")

cursor.execute("""
    SELECT 
        rest.name,
        a.date,
        a.time,
        a.seats_available
    FROM availability a
    JOIN restaurants rest ON a.restaurant_id = rest.id
    WHERE a.seats_available > 0
    ORDER BY a.date, a.time
    LIMIT 15
""")
availability = cursor.fetchall()

if availability:
    print(f"\n{'Restaurant':<40} {'Date':<12} {'Time':<8} {'Seats Available'}")
    print("-" * 80)
    for av in availability:
        print(f"{av[0]:<40} {av[1]:<12} {av[2]:<8} {av[3]}")
    
    cursor.execute("SELECT COUNT(*) FROM availability")
    total_rows = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(seats_available) FROM availability")
    total_seats = cursor.fetchone()[0]
    print(f"\n📊 Total: {total_rows:,} time slot rows (Total seats: {total_seats:,})")
else:
    print("⚠️  No availability data")

# ============================================================================
# STATISTICS
# ============================================================================
print_section("📈 STATISTICS")

# Cuisines
cursor.execute("""
    SELECT cuisine, COUNT(*) as count
    FROM restaurants
    GROUP BY cuisine
    ORDER BY count DESC
    LIMIT 10
""")
print("\n🍕 Top Cuisines:")
for cuisine in cursor.fetchall():
    print(f"  {cuisine[0]:<20} {cuisine[1]:>3} restaurants")

# Locations
cursor.execute("""
    SELECT location, COUNT(*) as count
    FROM restaurants
    GROUP BY location
    ORDER BY count DESC
    LIMIT 10
""")
print("\n📍 Top Locations:")
for loc in cursor.fetchall():
    print(f"  {loc[0]:<30} {loc[1]:>3} restaurants")

# Popular restaurants (by reservations)
cursor.execute("""
    SELECT 
        rest.name,
        COUNT(r.id) as reservation_count
    FROM restaurants rest
    LEFT JOIN reservations r ON rest.id = r.restaurant_id
    GROUP BY rest.id
    HAVING reservation_count > 0
    ORDER BY reservation_count DESC
    LIMIT 10
""")
popular = cursor.fetchall()
if popular:
    print("\n🏆 Most Booked Restaurants:")
    for rest in popular:
        print(f"  {rest[0]:<40} {rest[1]:>3} bookings")

conn.close()

print("\n" + "=" * 100)
print("✅ Database viewed successfully!")
print("=" * 100)

print("\n💡 Commands:")
print("  python view_users.py          - View only users")
print("  python view_all_data.py       - View everything (this script)")
print("  python data/generator.py      - Regenerate sample data")

