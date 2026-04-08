import streamlit as st
import uuid
import sys
import os

# Add parent dir to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from st_app.utils import inject_custom_css, t, get_cart_count

st.set_page_config(page_title="Pet Shop Premium", page_icon="🐾", layout="wide")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'lang' not in st.session_state:
    st.session_state.lang = 'English'

# CSS and Contact Icons
inject_custom_css()

# Big floating animated welcome banner
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
    <div class="welcome-top-banner">✨ Welcome back, {st.session_state.username}! ✨</div>
    """, unsafe_allow_html=True)

home_page = st.Page("views/home.py", title=t("home"), icon="🏠", default=True)
shop_page = st.Page("views/shop.py", title=t("shop"), icon="🛍️")
cart_title = f"{t('cart')} ({get_cart_count()})"
cart_page = st.Page("views/cart.py", title=cart_title, icon="🛒")
wishlist_page = st.Page("views/wishlist.py", title=t("wishlist"), icon="❤️")
checkout_page = st.Page("views/checkout.py", title=t("checkout"), icon="💳")
admin_page = st.Page("views/admin.py", title=t("admin"), icon="⚙️")

login_page = st.Page("views/login.py", title="Login / Sign Up", icon="🔐")

pg = st.navigation(
    [home_page, shop_page, cart_page, wishlist_page, checkout_page, admin_page, login_page], 
    position="hidden"
)

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=400", width="stretch")
    
    # Custom Sidebar Navigation (Omitting Admin)
    st.markdown(f"**Main**")
    st.page_link(home_page, label=t("home"), icon="🏠")
    st.page_link(shop_page, label=t("shop"), icon="🛍️")
    st.page_link(cart_page, label=cart_title, icon="🛒")
    st.page_link(wishlist_page, label=t("wishlist"), icon="❤️")
    
    st.markdown(f"**Account**")
    st.page_link(checkout_page, label=t("checkout"), icon="💳")
    
    st.divider()
    if st.session_state.get("user_id"):
        st.markdown(f"👤 **{st.session_state.username}**")
        if st.button("Logout", width="stretch"):
            del st.session_state.user_id
            del st.session_state.username
            st.rerun()
    else:
        st.page_link(login_page, label="Login / Sign Up", icon="🔐")

    st.divider()
    lang_choice = st.selectbox("🌐 Language", ["English", "Vietnamese", "Arabic"], index=["English", "Vietnamese", "Arabic"].index(st.session_state.lang))
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

pg.run()
