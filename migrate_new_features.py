import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "pet_shop.db")

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add delivery_date to orders if it doesn't exist
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN delivery_date DATETIME")
        print("Successfully added delivery_date to orders table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column delivery_date already exists in orders.")
        else:
            print(f"Error adding delivery_date: {e}")

    # Add pet_type to products if it doesn't exist
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN pet_type VARCHAR(50) DEFAULT 'Chung'")
        print("Successfully added pet_type to products table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column pet_type already exists in products.")
        else:
            print(f"Error adding pet_type: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
