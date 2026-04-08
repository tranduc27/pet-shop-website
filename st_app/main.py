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

home_page = st.Page("views/home.py", title=t("home"), icon="🏠", default=True)
shop_page = st.Page("views/shop.py", title=t("shop"), icon="🛍️")
cart_title = f"{t('cart')} ({get_cart_count()})"
cart_page = st.Page("views/cart.py", title=cart_title, icon="🛒")
wishlist_page = st.Page("views/wishlist.py", title=t("wishlist"), icon="❤️")
checkout_page = st.Page("views/checkout.py", title=t("checkout"), icon="💳")
admin_page = st.Page("views/admin.py", title=t("admin"), icon="⚙️")

pg = st.navigation(
    [home_page, shop_page, cart_page, wishlist_page, checkout_page, admin_page], 
    position="hidden"
)

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=400", use_container_width=True)
    
    # Custom Sidebar Navigation (Omitting Admin)
    st.markdown(f"**Main**")
    st.page_link(home_page, label=t("home"), icon="🏠")
    st.page_link(shop_page, label=t("shop"), icon="🛍️")
    st.page_link(cart_page, label=cart_title, icon="🛒")
    st.page_link(wishlist_page, label=t("wishlist"), icon="❤️")
    
    st.markdown(f"**Account**")
    st.page_link(checkout_page, label=t("checkout"), icon="💳")
    
    st.divider()
    lang_choice = st.selectbox("🌐 Language", ["English", "Vietnamese", "Arabic"], index=["English", "Vietnamese", "Arabic"].index(st.session_state.lang))
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

pg.run()
