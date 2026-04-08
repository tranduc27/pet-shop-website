import streamlit as st
from app.database import SessionLocal
from app.models.cart import Cart
import uuid

# Translations
translations = {
    'English': {
        'home': 'Home',
        'shop': 'Shop',
        'cart': 'Cart',
        'wishlist': 'Wishlist',
        'checkout': 'Checkout',
        'admin': 'Admin Panel',
        'add_to_cart': 'Add to Cart',
        'today_sales': "Today's Sales",
        'price': 'Price',
        'size': 'Size',
        'quantity': 'Quantity',
        'empty_cart': 'Your cart is empty',
        'total': 'Total',
        'submit_order': 'Submit Order',
        'guest_checkout': 'Guest Checkout',
        'admin_manage': 'Manage Products',
        'contact_us': 'Contact Us',
        'customer_testimonials': 'Customer Reviews',
        'no_reviews': 'No shop reviews yet. Be the first!',
        'leave_review': 'Leave a Review for Pet Shop',
        'view_detail': 'View Detail'
    },
    'Vietnamese': {
        'home': 'Trang chủ',
        'shop': 'Cửa hàng',
        'cart': 'Giỏ hàng',
        'wishlist': 'Yêu thích',
        'checkout': 'Thanh toán',
        'admin': 'Quản lý',
        'add_to_cart': 'Thêm vào giỏ',
        'today_sales': 'Khuyến mãi hôm nay',
        'price': 'Giá',
        'size': 'Kích thước',
        'quantity': 'Số lượng',
        'empty_cart': 'Giỏ hàng trống',
        'total': 'Tổng tiền',
        'submit_order': 'Đặt hàng',
        'guest_checkout': 'Thanh toán khách',
        'admin_manage': 'Quản lý Sản phẩm',
        'contact_us': 'Liên hệ với chúng tôi',
        'customer_testimonials': 'Đánh giá từ Khách hàng',
        'no_reviews': 'Chưa có đánh giá nào. Hãy là người đầu tiên!',
        'leave_review': 'Viết Đánh giá cho Pet Shop',
        'view_detail': 'Xem chi tiết'
    }
}

def t(key):
    lang = st.session_state.get('lang', 'English')
    return translations.get(lang, translations['English']).get(key, key)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cart_count():
    db = SessionLocal()
    try:
        session_id = st.session_state.get('session_id')
        user_id = st.session_state.get('user_id')
        
        query = db.query(Cart)
        if user_id:
            query = query.filter(Cart.user_id == user_id)
        else:
            query = query.filter(Cart.session_id == session_id)
            
        items = query.all()
        return sum([item.quantity for item in items])
    finally:
        db.close()

def inject_custom_css():
    st.markdown("""
    <style>
    /* Styling to make the app feel premium */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Product Cards */
    .product-card {
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        background-color: var(--background-color);
        border: 1px solid var(--secondary-background-color);
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.2);
    }
    .product-image {
        width: 100%;
        max-height: 200px;
        object-fit: cover;
        border-radius: 10px;
    }
    .discount-badge {
        background-color: #ff4757;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
        position: absolute;
        top: 10px;
        right: 10px;
    }
    
    /* Floating Contact Icons */
    .floating-icons {
        position: fixed;
        bottom: 20px;
        right: 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        z-index: 9999;
    }
    .contact-btn {
        width: 50px;
        height: 50px;
        border-radius: 25px;
        background-color: #3b5998;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
        border-bottom: none !important;
        font-size: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .floating-icons a {
        text-decoration: none !important;
        border-bottom: none !important;
    }
    .contact-btn:hover {
        transform: scale(1.1);
    }
    .btn-zalo { background-color: #0068FF !important; }
    .btn-mess { background-color: #0084FF !important; }
    .btn-sms { background-color: #4CAF50 !important; }
    
    /* Hide all hamburger menu items EXCEPT the first one (Theme toggler) */
    ul[data-testid="main-menu-list"] > li:not(:first-child) {
        display: none !important;
    }
    ul[data-testid="main-menu-list"] > div {
        display: none !important; /* hide dividers if any */
    }
    </style>
    
    <div class="floating-icons">
        <a href="https://www.facebook.com/ductrann.27/" class="contact-btn btn-mess" title="Messenger" target="_blank" rel="noopener noreferrer">💬</a>
        <a href="https://zalo.me/0375318910" class="contact-btn btn-zalo" title="Zalo" target="_blank" rel="noopener noreferrer">Z</a>
    </div>
    """, unsafe_allow_html=True)
