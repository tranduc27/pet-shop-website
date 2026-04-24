import streamlit as st
from app.database import SessionLocal
from app.models.wishlist import Wishlist
from app.models.product import Product
from st_app.utils import t

st.title(f"❤️ {t('Danh sách yêu thích')}")

db = SessionLocal()
try:
    if not st.session_state.get('user_id'):
        st.warning("⚠️ Vui lòng đăng nhập")
        st.stop()
        
    items = db.query(Wishlist).filter_by(user_id=st.session_state.user_id).all()
    
    if not items:
        st.info("Danh sách yêu thích đang trống.")
    else:
        cols = st.columns(4)
        for i, item in enumerate(items):
            product = db.query(Product).filter_by(id=item.product_id).first()
            if not product: continue
            
            with cols[i % 4]:
                img_url = product.image_url if product.image_url else f"https://picsum.photos/seed/{product.id}/400/400"
                if not img_url.startswith("http"):
                     img_url = f"https://picsum.photos/seed/{product.id}/400/400"
                st.image(img_url)
                st.write(f"**{product.name}**")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Xem chi tiết", key=f"wl_view_{item.id}", type="primary", use_container_width=True):
                        st.session_state.selected_product_id = product.id
                        st.switch_page("views/shop.py")
                with c2:
                    if st.button("Xóa", key=f"wl_rem_{item.id}", use_container_width=True):
                        db.delete(item)
                        db.commit()
                        st.rerun()
finally:
    db.close()
