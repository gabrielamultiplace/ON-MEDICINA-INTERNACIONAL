import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Get prescription table schema
cursor.execute("PRAGMA table_info(cannabis_prescriptions)")
columns = cursor.fetchall()

print("Prescription table columns:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Get one prescription
cursor.execute("SELECT * FROM cannabis_prescriptions LIMIT 1")
row = cursor.fetchone()
if row:
    print("\nFirst prescription record:")
    for i, col in enumerate(columns):
        print(f"  {col[1]}: {row[i]}")
        
conn.close()
