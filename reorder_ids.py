import sqlite3

db_path = r"c:\Users\PC\pet-shop-website\pet_shop.db"

def reorder_ids():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tạm thời vô hiệu hóa khóa ngoại để đảm bảo an toàn
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Lấy tất cả ID sản phẩm theo thứ tự tăng dần
    cursor.execute("SELECT id FROM products ORDER BY id ASC")
    rows = cursor.fetchall()
    
    # Gán lại ID bắt đầu từ 1
    new_id = 1
    for row in rows:
        old_id = row[0]
        if old_id != new_id:
            cursor.execute("UPDATE products SET id = ? WHERE id = ?", (new_id, old_id))
        new_id += 1
        

    conn.commit()
    conn.close()
    print("Database product IDs reordered successfully from 1!")

if __name__ == "__main__":
    reorder_ids()
