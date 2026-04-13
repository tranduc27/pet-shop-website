import sqlite3

def migrate():
    conn = sqlite3.connect("pet_shop.db")
    cursor = conn.cursor()
    
    # hàm hỗ trợ để kiểm tra xem cột có tồn tại không
    def column_exists(table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        return column in columns
        
    try:
        # Các thay đổi của Sản phẩm
        if not column_exists("products", "size"):
            cursor.execute("ALTER TABLE products ADD COLUMN size VARCHAR(50) DEFAULT NULL")
            print("Added size to products")
        if not column_exists("products", "discount_percent"):
            cursor.execute("ALTER TABLE products ADD COLUMN discount_percent FLOAT DEFAULT 0.0")
            print("Added discount_percent to products")
        if not column_exists("products", "is_today_sale"):
            cursor.execute("ALTER TABLE products ADD COLUMN is_today_sale BOOLEAN DEFAULT 0")
            print("Added is_today_sale to products")
            
        # Các thay đổi của Giỏ hàng    
        if not column_exists("cart", "session_id"):
            cursor.execute("ALTER TABLE cart ADD COLUMN session_id VARCHAR(100) DEFAULT NULL")
            print("Added session_id to cart")

        # Các thay đổi của Đơn hàng
        if not column_exists("orders", "session_id"):
            cursor.execute("ALTER TABLE orders ADD COLUMN session_id VARCHAR(100) DEFAULT NULL")
            print("Added session_id to orders")
        if not column_exists("orders", "guest_name"):
            cursor.execute("ALTER TABLE orders ADD COLUMN guest_name VARCHAR(100) DEFAULT NULL")
            print("Added guest_name to orders")
        if not column_exists("orders", "guest_phone"):
            cursor.execute("ALTER TABLE orders ADD COLUMN guest_phone VARCHAR(20) DEFAULT NULL")
            print("Added guest_phone to orders")
        if not column_exists("orders", "guest_address"):
            cursor.execute("ALTER TABLE orders ADD COLUMN guest_address TEXT DEFAULT NULL")
            print("Added guest_address to orders")
        
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
