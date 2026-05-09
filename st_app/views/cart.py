import streamlit as st
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.product import Product
from app.models.review import Review
from st_app.utils import t

@st.dialog("Chi tiết sản phẩm", width="large")
def product_detail_modal(product):
    cols = st.columns(2)
    with cols[0]:
        img_url = product.image_url if product.image_url else f"https://picsum.photos/seed/{product.id}/400/400"
        if not img_url.startswith("http"):
             img_url = f"https://picsum.photos/seed/{product.id}/400/400"
        st.image(img_url, width="stretch")
    with cols[1]:
        st.header(product.name)
        
        # Rating display
        db = SessionLocal()
        try:
            reviews = db.query(Review).filter(Review.product_id == product.id).all()
            avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
            st.caption(f"{'⭐' * int(avg_rating)} ({len(reviews)} Đánh giá)")
        finally:
            db.close()

        st.write(f"**{t('')}:** {product.price:,.0f} VNĐ")
        st.write(product.description or "Không có mô tả")
        st.divider()
        st.info("Sản phẩm đã ở trong giỏ hàng của bạn")

st.title(f"🛒 {t('Giỏ hàng')}")

class GuestCartItem:
    def __init__(self, id, product_id, quantity):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity

db = SessionLocal()
try:
    is_guest = False
    if not st.session_state.get('user_id'):
        is_guest = True
        cart_items = [GuestCartItem(**d) for d in st.session_state.get('guest_cart', [])]
    else:
        user_id = st.session_state.user_id
        cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    
    if not cart_items:
        st.info(t('empty_cart'))
        if st.button("Khám phá", type="primary"):
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
                if st.button("🔍 " + t('Xem chi tiết'), key=f"view_{item.id}"):
                    product_detail_modal(product)
            with c3:
                new_qty = st.number_input(t('Số lượng'), min_value=1, value=item.quantity, key=f"qty_{item.id}")
                if new_qty != item.quantity:
                    if is_guest:
                        for gi in st.session_state.guest_cart:
                            if gi['id'] == item.id:
                                gi['quantity'] = new_qty
                        st.rerun()
                    else:
                        item.quantity = new_qty
                        db.commit()
                        st.rerun()
            with c4:
                st.write(f"**{product.price * item.quantity:,.0f} VNĐ**")
                if st.button("🗑️ Xóa", key=f"rem_{item.id}"):
                    if is_guest:
                        st.session_state.guest_cart = [gi for gi in st.session_state.guest_cart if gi['id'] != item.id]
                        st.rerun()
                    else:
                        db.delete(item)
                        db.commit()
                        st.rerun()
            
            if is_selected:
                total += product.price * item.quantity
            st.divider()
            
        st.markdown(f"### {t('Tổng tiền')}: {total:,.0f} VNĐ")
        if st.button(t('Thanh toán'), type="primary", width="stretch"):
            if is_guest:
                st.warning("Vui lòng đăng nhập để tiến hành thanh toán.")
                # Sử dụng time.sleep hoặc just st.stop() sau error để user đọc
                # Tuy nhiên st.switch_page chạy ngay lập tức. 
                # Có thể lưu state để hiển thị ở login page:
                st.session_state.login_message = "Vui lòng đăng nhập để tiếp tục thanh toán"
                st.switch_page("views/login.py")
            else:
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
                        st.session_state.is_guest_checkout = is_guest
                        st.switch_page("views/checkout.py")
            
finally:
    db.close()
