import sqlite3
conn = sqlite3.connect('pet_shop.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE orders ADD COLUMN confirmed_by VARCHAR(100);")
    cursor.execute("ALTER TABLE orders ADD COLUMN confirmed_at DATETIME;")
    conn.commit()
    print("Columns added successfully.")
except sqlite3.OperationalError as e:
    print(f"Error: {e}")
conn.close()
