import streamlit as st
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.order import Order
from app.models.product import Product
from st_app.utils import t

st.title(f"💳 {t('checkout')}")

db = SessionLocal()
try:
    # Đầu tiên kiểm tra xem đơn hàng vừa được đặt hay không
    if st.session_state.get('order_placed'):
        st.success("🎉 Hàng đã được đặt thành công! Chúng tôi sẽ sớm liên hệ với bạn để xác định thông tin giao hàng.")
        st.info("Đơn hàng của bạn đang được xử lý. Cảm ơn bạn vì đã mua hàng của chúng tôi!")
        if st.button("Quay lại cửa hàng 🛍️"):
            del st.session_state.order_placed
            st.switch_page("views/shop.py")
        st.stop()

    if not st.session_state.get('user_id'):
        st.warning("⚠️ Vui lòng đăng nhập từ trang cửa hàng để tiếp tục thanh toán.")
        st.stop()

    cart_items_all = db.query(Cart).filter_by(user_id=st.session_state.user_id).all()
    if 'checkout_item_ids' in st.session_state:
        cart_items = [item for item in cart_items_all if item.id in st.session_state.checkout_item_ids]
    else:
        cart_items = cart_items_all
    if not cart_items:
        st.info("🛒 Giỏ hàng của bạn đang trống. Hãy thêm sản phẩm để tiếp tục thanh toán")
        if st.button("Quay lại cửa hàng"):
            st.switch_page("views/shop.py")
        st.stop()
        
    # Tính toán tổng tiền
    subtotal = sum([(db.query(Product).filter_by(id=item.product_id).first().price * item.quantity) for item in cart_items if db.query(Product).filter_by(id=item.product_id).first()])
    shipping_fee = 30000 if subtotal < 1000000 else 0.00
    total = subtotal + shipping_fee
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 📋 Đơn hàng")
        st.markdown("<div style='background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
        for item in cart_items:
            prod = db.query(Product).filter_by(id=item.product_id).first()
            if prod:
                st.markdown(f"**{prod.name}**  \n`x{item.quantity}` - {prod.price * item.quantity:,.0f} VNĐ")
        st.divider()
        st.markdown(f"**Tổng tiền:** {subtotal:,.0f} VNĐ")
        if shipping_fee == 0:
            st.markdown(f"**Phí giao hàng:** 🟢 Miễn phí")
        else:
            st.markdown(f"**Phí giao hàng:** {shipping_fee:,.0f} VNĐ")
        st.markdown(f"### **Tổng tiền: <span style='color:#0068FF'>{total:,.0f} VNĐ</span>**", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col1:
        st.markdown(f"### 📍 Thông tin giao hàng")
        name = st.text_input("Họ và tên", placeholder="e.g. Tran Dinh Duc")
        
        c_phone, c_email = st.columns(2)
        with c_phone:
            phone = st.text_input("Số điện thoại", placeholder="0988...")
        with c_email:
            email = st.text_input("Email", placeholder="example@gmail.com")
            
        address = st.text_area("Địa chỉ", placeholder="e.g. 123 Hanoi Street, Hoan Kiem, HN")
        note = st.text_input("Ghi chú (Tùy chọn)", placeholder="e.g. Giao hàng trong giờ hành chính.")
        
        st.markdown("---")
        st.markdown(f"### 💵 Phương thức thanh toán")
        
        payment_method = st.radio(
            "Chọn phương thức thanh toán ",
            ["Thanh toán bằng tiền mặt", "Credit/Debit Card", "Chuyển khoản ngân hàng", "Ví điện tử (MoMo/ZaloPay)"],
            horizontal=False
        )
        
        # Giao diện người dùng theo phương thức thanh toán
        if payment_method == "Credit/Debit Card":
            st.info("🔒 Form thanh toán")
            cc_name = st.text_input("Cardholder Name", placeholder="TRAN DINH DUC")
            cc_num = st.text_input("Card Number", placeholder="0000 0000 0000 0000", max_chars=19)
            cc1, cc2 = st.columns(2)
            with cc1:
                st.text_input("Expiry Date", placeholder="MM/YY")
            with cc2:
                st.text_input("CVV", placeholder="123", type="password")
                
        elif payment_method == "Chuyển khoản ngân hàng":
            st.info("🏦 Thông tin tài khoản ngân hàng")
            st.markdown("""
            Vui lòng chuyển tiền theo thông tin dưới đây
            
            **Ngân hàng:** Vietcombank (VCB)  
            **Tên chủ tài khoản:** PET SHOP PREMIUM VN  
            **Số tài khoản:** `0123456789`  
            **Nội dung chuyển khoản:** `PAY-[Your Phone Number]`
            """)
            st.file_uploader("Tải lên hóa đơn chuyển tiền (Tùy chọn)", type=["png", "jpg", "jpeg", "pdf"])
            
        elif payment_method == "Ví điện tử (MoMo/ZaloPay)":
            st.info("📱 Quét mã QR để thanh toán qua MoMo/ZaloPay")
            c_qr1, c_qr2, _ = st.columns([1,1,2])
            with c_qr1:
                st.markdown("**MoMo**")
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=MoMoPayment", width=120)
            with c_qr2:
                st.markdown("**ZaloPay**")
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=ZaloPayPayment", width=120)
        
        st.markdown("---")
        
        # Nút xác nhận
        if st.button("✅ Xác nhận & Đặt hàng", width="stretch", type="primary"):
            if not name or not phone or not address:
                st.error("⚠️ Vui lòng điền đầy đủ các thông tin cần thiết (Tên, Số điện thoại, Địa chỉ).")
            elif payment_method == "Credit/Debit Card" and (not cc_name or not cc_num):
                st.error("⚠️ Vui lòng điền đầy đủ thông tin của Credit Card.")
            else:
                # Kiểm tra kho và giảm số lượng
                stock_error = False
                for item in cart_items:
                    prod = db.query(Product).filter_by(id=item.product_id).first()
                    if prod and prod.stock is not None:
                        if prod.stock <= 0:
                            st.error(f"Sản phẩm '{prod.name}' đã hết hàng vì có khách hàng khác vừa mua hoặc đổi trạng thái. Vui lòng xóa/giảm bớt khỏi giỏ hàng.")
                            stock_error = True
                            break
                        elif prod.stock < item.quantity:
                            st.error(f"Sản phẩm '{prod.name}' hiện chỉ còn {prod.stock} sản phẩm trong kho. Không đủ đáp ứng số lượng bạn chọn. Vui lòng cập nhật lại giỏ hàng.")
                            stock_error = True
                            break
                            
                if stock_error:
                    st.stop()
                    
                # Trừ số lượng kho
                for item in cart_items:
                    prod = db.query(Product).filter_by(id=item.product_id).first()
                    if prod and prod.stock is not None:
                        prod.stock -= item.quantity
                
                final_address = f"{address}\nEmail: {email}\nNote: {note}\nPayment Method: {payment_method}"
                
                new_order = Order(
                    session_id=st.session_state.session_id,
                    user_id=st.session_state.user_id,
                    guest_name=name,
                    guest_phone=phone,
                    guest_address=final_address,
                    total_price=total,
                    status="Pending"
                )
                db.add(new_order)
                
                # xóa giỏ hàng
                for it in cart_items:
                    db.delete(it)
                db.commit()
                
                st.balloons()
                st.session_state.order_placed = True
                st.rerun()

finally:
    db.close()
