import streamlit as st
import uuid
import sys
import os

# Thêm thư mục cha vào đường dẫn để có thể import các module của ứng dụng
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from st_app.utils import inject_custom_css, t, get_cart_count

st.set_page_config(page_title="Pet Shop Premium", page_icon="🐾", layout="wide")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# CSS và biểu tượng liên hệ
inject_custom_css()

# Banner chào mừng khổ lớn dạng nổi có hiệu ứng hoạt hình
if st.session_state.get("user_id"):
    st.markdown(f"""
    <style>
    .welcome-top-banner {{
        position: fixed;
        top: 60px;
        left: 50vw;
        transform: translateX(-10vw);
        background: linear-gradient(135deg, #00C853, #64DD17);
        color: white;
        padding: 20px 50px;
        border-radius: 50px;
        font-size: 28px;
        font-weight: bold;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        z-index: 10000;
        text-align: center;
        animation: slideDownFadeOut 4s forwards;
        pointer-events: none;
    }}
    @keyframes slideDownFadeOut {{
        0%   {{ top: -100px; opacity: 0; }}
        10%  {{ top: 60px; opacity: 1; }}
        80%  {{ top: 60px; opacity: 1; }}
        100% {{ top: -100px; opacity: 0; visibility: hidden; }}
    }}
    </style>
    <div class="welcome-top-banner">✨ Chào mừng trở lại, {st.session_state.username}! ✨</div>
    """, unsafe_allow_html=True)

home_page = st.Page("views/home.py", title=t("Trang chủ"), icon="🏠", default=True)
shop_page = st.Page("views/shop.py", title=t("Cửa hàng"), icon="🛍️")
cart_title = f"{t('Giỏ hàng')} ({get_cart_count()})"
cart_page = st.Page("views/cart.py", title=cart_title, icon="🛒")
wishlist_page = st.Page("views/wishlist.py", title=t("Danh sách yêu thích"), icon="❤️")
checkout_page = st.Page("views/checkout.py", title=t("Thanh toán"), icon="💳")
admin_page = st.Page("views/admin.py", title=t("admin"), icon="⚙️")
profile_page = st.Page("views/profile.py", title=t("Tài khoản"), icon="👤")

login_page = st.Page("views/login.py", title=t("Đăng nhập/Đăng ký"), icon="🔐")

pg = st.navigation(
    [home_page, shop_page, cart_page, wishlist_page, checkout_page, admin_page, profile_page, login_page], 
    position="hidden"
)

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=400", width="stretch")
    
    if pg != admin_page:
        # Điều hướng thanh bên (Sidebar) tùy chỉnh (Bỏ qua cấu hình Admin)
        st.markdown(f"**{t('main_menu')}**")
        st.page_link(home_page, label=t("Trang chủ"), icon="🏠")
        st.page_link(shop_page, label=t("Cửa hàng"), icon="🛍️")
        st.page_link(cart_page, label=cart_title, icon="🛒")
        st.page_link(wishlist_page, label=t("Danh sách yêu thích"), icon="❤️")
        
        st.markdown(f"**{t('Tài khoản')}**")
        st.page_link(checkout_page, label=t("Thanh toán"), icon="💳")
        
        st.divider()
        if st.session_state.get("user_id"):
            st.page_link(profile_page, label=f"{t('profile')} ({st.session_state.username})")
            if st.button(t("logout"), width="stretch"):
                del st.session_state.user_id
                del st.session_state.username
                st.rerun()
        else:
            st.page_link(login_page, label=t("login_signup"), icon="🔐")



pg.run()
