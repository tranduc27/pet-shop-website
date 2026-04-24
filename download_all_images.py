import sqlite3
import urllib.request
import os

db_path = r"c:\Users\PC\pet-shop-website\pet_shop.db"
img_dir = r"c:\Users\PC\pet-shop-website\app\static\images"
os.makedirs(img_dir, exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Lấy tất cả các URL hình ảnh khác null
cursor.execute("SELECT image_url FROM products WHERE image_url IS NOT NULL")
rows = cursor.fetchall()

count = 0
for row in rows:
    image_url = row[0]
    # định dạng URL hình ảnh: /static/images/filename.jpg
    if not image_url.startswith("/static/images/"):
        continue
        
    filename = image_url.split("/")[-1]
    file_path = os.path.join(img_dir, filename)
    
    # Kiểm tra xem đã tải xuống chưa
    if os.path.exists(file_path):
        continue
        
    url = f"https://picsum.photos/seed/{filename}/400/400"
    try:
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {filename}")
        count += 1
    except Exception as e:
        print(f"Error for {filename}: {e}")

print(f"Done! Downloaded {count} missing images.")
conn.close()
