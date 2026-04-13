import streamlit as st
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.product import Product
from st_app.utils import t

st.title(f"🛒 {t('cart')}")

db = SessionLocal()
try:
    if not st.session_state.get('user_id'):
        st.warning("⚠️ Please login from the shop page to view your cart.")
        st.stop()
        
    user_id = st.session_state.user_id
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    
    if not cart_items:
        st.info(t('empty_cart'))
        if st.button("Browse Shop", type="primary"):
            st.switch_page("views/shop.py")
    else:
        total = 0
        for item in cart_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product: continue
            
            c0, c1, c2, c3, c4 = st.columns([0.5, 1, 2, 1, 1])
            with c0:
                is_selected = st.checkbox("", value=st.session_state.get(f"sel_{item.id}", True), key=f"sel_{item.id}")
            with c1:
                img_url = product.image_url if product.image_url else f"https://picsum.photos/seed/{product.id}/100/100"
                if not img_url.startswith("http"):
                    img_url = f"https://picsum.photos/seed/{product.id}/100/100"
                st.image(img_url, width="stretch")
            with c2:
                st.write(f"**{product.name}**")
                st.write(f"{product.price:,.0f} VNĐ")
            with c3:
                new_qty = st.number_input(t('quantity'), min_value=1, value=item.quantity, key=f"qty_{item.id}")
                if new_qty != item.quantity:
                    item.quantity = new_qty
                    db.commit()
                    st.rerun()
            with c4:
                st.write(f"**{product.price * item.quantity:,.0f} VNĐ**")
                if st.button("🗑️ Remove", key=f"rem_{item.id}"):
                    db.delete(item)
                    db.commit()
                    st.rerun()
            
            if is_selected:
                total += product.price * item.quantity
            st.divider()
            
        st.markdown(f"### {t('total')}: {total:,.0f} VNĐ")
        if st.button(t('checkout'), type="primary", width="stretch"):
            selected_ids = [item.id for item in cart_items if st.session_state.get(f"sel_{item.id}", True)]
            if not selected_ids:
                st.error("Vui lòng chọn ít nhất một sản phẩm để thanh toán.")
            else:
                stock_error = False
                selected_items = [item for item in cart_items if item.id in selected_ids]
                for item in selected_items:
                    prod = db.query(Product).filter_by(id=item.product_id).first()
                    if prod and prod.stock is not None:
                        if prod.stock <= 0:
                            st.error(f"Sản phẩm '{prod.name}' đã hết hàng. Vui lòng bỏ chọn hoặc xóa khỏi giỏ hàng để tiếp tục.")
                            stock_error = True
                            break
                        elif prod.stock < item.quantity:
                            st.error(f"Sản phẩm '{prod.name}' hiện chỉ còn {prod.stock} sản phẩm. Không đủ đáp ứng, vui lòng sửa lại số lượng.")
                            stock_error = True
                            break
                
                if not stock_error:
                    st.session_state.checkout_item_ids = selected_ids
                    st.switch_page("views/checkout.py")
            
finally:
    db.close()
