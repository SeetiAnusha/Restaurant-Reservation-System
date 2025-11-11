import sqlite3

conn = sqlite3.connect('data/restaurants.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT restaurant_id, date, time, seats_available 
    FROM availability 
    WHERE date = '2025-11-10'
    ORDER BY restaurant_id, time 
    LIMIT 20
''')

print("Restaurant ID | Date       | Time  | Seats")
print("-" * 50)
for row in cursor.fetchall():
    print(f"{row[0]:<13} | {row[1]:<10} | {row[2]:<5} | {row[3]}")

conn.close()
