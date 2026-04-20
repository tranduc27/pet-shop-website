import streamlit as st
import math
import requests
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from st_app.utils import t

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Bán kính trái đất (km)
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_coordinates(address_detail, province="Hà Nội"):
    parts = [p.strip() for p in address_detail.split(",") if p.strip()]
    attempts = [address_detail]
    if len(parts) >= 2:
        attempts.append(", ".join(parts[-2:]))
    if len(parts) >= 3:
        attempts.append(parts[-1])
        
    headers = {"User-Agent": "PetShopApp/1.0"}
    for attempt in attempts:
        q = f"{attempt}, {province}, Việt Nam"
        url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    return float(data[0]['lat']), float(data[0]['lon'])
        except:
            pass
    return None, None

st.title(f"💳 {t('checkout')}")

db = SessionLocal()
try:
    # Đầu tiên kiểm tra xem đơn hàng vừa được đặt hay không
    if st.session_state.get('order_placed'):
        st.success("🎉 Hàng đã được đặt thành công! Chúng tôi sẽ sớm liên hệ với bạn để xác định thông tin giao hàng.")
        st.info("Đơn hàng của bạn đang được xử lý. Cảm ơn bạn vì đã mua hàng của chúng tôi!")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Quay lại cửa hàng 🛍️", use_container_width=True):
                del st.session_state.order_placed
                st.switch_page("views/shop.py")
        with c2:
            if st.button("Kiểm tra đơn hàng vừa đặt 📦", use_container_width=True, type="primary"):
                del st.session_state.order_placed
                st.switch_page("views/profile.py")
                
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
        
    if 'shipping_fee' not in st.session_state:
        st.session_state.shipping_fee = 30000
    if 'shipping_calculated' not in st.session_state:
        st.session_state.shipping_calculated = False

    # Tính toán tổng tiền
    subtotal = sum([(db.query(Product).filter_by(id=item.product_id).first().price * item.quantity) for item in cart_items if db.query(Product).filter_by(id=item.product_id).first()])
    shipping_fee = st.session_state.shipping_fee
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
            
        province = st.selectbox("Tỉnh / Thành phố", ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Tỉnh khác..."])
        address_detail = st.text_area("Địa chỉ cụ thể (Quận/Huyện, Phường/Xã, Số nhà...)", placeholder="e.g. Trần Phú, Hà Đông")
        note = st.text_input("Ghi chú (Tùy chọn)", placeholder="e.g. Giao hàng trong giờ hành chính.")
        
        st.markdown(f"**Phí vận chuyển ước tính:** {'Chưa tính (Mặc định 30k)' if not st.session_state.shipping_calculated else f'{shipping_fee:,.0f} VNĐ'}")
        
        if st.button("📍 Tính phí vận chuyển (Bắt buộc trước khi thanh toán)", use_container_width=True):
            if province != "Hà Nội":
                st.session_state.shipping_fee = 30000
                st.session_state.shipping_calculated = True
                st.session_state.ship_msg = "Phí giao hàng ngoại tỉnh là 30.000 VNĐ."
                st.session_state.ship_msg_type = "success"
                st.rerun()
            else:
                if not address_detail.strip():
                    st.error("Vui lòng nhập địa chỉ cụ thể để tính khoảng cách")
                else:
                    lat, lon = get_coordinates(address_detail.strip(), province="Hà Nội")
                    if lat and lon:
                        shop_lat = 20.9808814
                        shop_lon = 105.787212
                        dist = haversine(shop_lat, shop_lon, lat, lon)
                        dist_round = math.ceil(dist)
                        if dist <= 1:
                            st.session_state.shipping_fee = 0
                        else:
                            st.session_state.shipping_fee = dist_round * 15000
                        st.session_state.shipping_calculated = True
                        st.session_state.ship_msg = f"Khoảng cách ước tính: {dist:.1f} km. Phí ship: {st.session_state.shipping_fee:,.0f} VNĐ"
                        st.session_state.ship_msg_type = "success"
                        st.rerun()
                    else:
                        st.session_state.ship_msg = "Không tìm thấy địa chỉ của bạn trên bản đồ OpenStreetMap. Áp dụng mức phí mặc định 30.000 VNĐ."
                        st.session_state.ship_msg_type = "error"
                        st.session_state.shipping_fee = 30000
                        st.session_state.shipping_calculated = True
                        st.rerun()
                        
        if 'ship_msg' in st.session_state:
            if st.session_state.ship_msg_type == "success":
                st.success(st.session_state.ship_msg)
            else:
                st.error(st.session_state.ship_msg)
        
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
            if not name or not phone or not address_detail:
                st.error("⚠️ Vui lòng điền đầy đủ các thông tin cần thiết (Tên, Số điện thoại, Địa chỉ cụ thể).")
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
                
                final_address = f"{address_detail}\n{province}\nEmail: {email}\nGhi chú: {note}\nPhương thức thanh toán: {payment_method}"
                
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
                db.flush() # Để lấy ID của order vừa tạo
                
                for it in cart_items:
                    prod = db.query(Product).filter_by(id=it.product_id).first()
                    if prod:
                        db.add(OrderItem(
                            order_id=new_order.id,
                            product_id=it.product_id,
                            quantity=it.quantity,
                            price=prod.price
                        ))

                # xóa giỏ hàng
                for it in cart_items:
                    db.delete(it)
                db.commit()
                
                st.balloons()
                st.session_state.order_placed = True
                
                if 'shipping_fee' in st.session_state: del st.session_state.shipping_fee
                if 'shipping_calculated' in st.session_state: del st.session_state.shipping_calculated
                if 'ship_msg' in st.session_state: del st.session_state.ship_msg
                
                st.rerun()

finally:
    db.close()
