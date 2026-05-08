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
        
        # Phần tạo và hiển thị nút tải hóa đơn
        if 'last_order_id' in st.session_state:
            last_order = db.query(Order).filter_by(id=st.session_state.last_order_id).first()
            if last_order:
                order_items = db.query(OrderItem).filter_by(order_id=last_order.id).all()
                try:
                    from fpdf import FPDF
                    import os
                    
                    pdf = FPDF()
                    pdf.add_page()
                    font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "Roboto-Regular.ttf")
                    pdf.add_font("Roboto", "", font_path, uni=True)
                    pdf.set_font("Roboto", size=16)
                    
                    pdf.cell(0, 10, txt="HÓA ĐƠN MUA HÀNG - PET SHOP", ln=True, align="C")
                    pdf.set_font("Roboto", size=12)
                    pdf.cell(0, 10, txt=f"Mã đơn hàng: #{last_order.id}", ln=True, align="C")
                    pdf.ln(10)
                    
                    pdf.set_font("Roboto", size=12)
                    pdf.cell(0, 10, txt="THÔNG TIN KHÁCH HÀNG", ln=True, align="L")
                    pdf.cell(0, 10, txt=f"Khách hàng: {last_order.guest_name}", ln=True, align="L")
                    pdf.cell(0, 10, txt=f"Số điện thoại: {last_order.guest_phone}", ln=True, align="L")
                    
                    address_lines = last_order.guest_address.split('\n')
                    pdf.cell(0, 10, txt="Thông tin giao hàng & ghi chú:", ln=True, align="L")
                    for line in address_lines:
                        pdf.cell(0, 10, txt=f"  {line}", ln=True, align="L")
                    pdf.ln(5)
                    
                    pdf.cell(0, 10, txt="CHI TIẾT ĐƠN HÀNG", ln=True, align="L")
                    
                    pdf.cell(100, 10, txt="Sản phẩm", border=1, align="C")
                    pdf.cell(40, 10, txt="Số lượng", border=1, align="C")
                    pdf.cell(50, 10, txt="Đơn giá", border=1, align="C")
                    pdf.ln(10)
                    
                    for item in order_items:
                        prod = db.query(Product).filter_by(id=item.product_id).first()
                        prod_name = prod.name if prod else "Sản phẩm không xác định"
                        # Cắt chuỗi nếu tên sản phẩm quá dài
                        if len(prod_name) > 40:
                            prod_name = prod_name[:37] + "..."
                        pdf.cell(100, 10, txt=str(prod_name), border=1)
                        pdf.cell(40, 10, txt=str(item.quantity), border=1, align="C")
                        pdf.cell(50, 10, txt=f"{item.price:,.0f} VNĐ", border=1, align="R")
                        pdf.ln(10)
                        
                    pdf.ln(5)
                    pdf.set_font("Roboto", size=14)
                    pdf.cell(140, 10, txt="Tổng tiền:", align="R")
                    pdf.cell(50, 10, txt=f"{last_order.total_price:,.0f} VNĐ", align="R")
                    pdf.ln(20)
                    
                    pdf.set_font("Roboto", size=10)
                    pdf.cell(0, 10, txt="Cảm ơn bạn đã mua sắm tại Pet Shop!", ln=True, align="C")
                    
                    pdf_bytes = bytes(pdf.output())
                    
                    c_btn, _ = st.columns([1, 2])
                    with c_btn:
                        st.download_button(
                            label="📥 Tải Hóa Đơn (PDF)",
                            data=pdf_bytes,
                            file_name=f"HoaDon_PetShop_Order{last_order.id}.pdf",
                            mime="application/pdf",
                            type="primary"
                        )
                    st.divider()
                except Exception as e:
                    st.error(f"Không thể tạo hóa đơn PDF: {e}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Quay lại cửa hàng 🛍️", use_container_width=True):
                del st.session_state.order_placed
                if 'last_order_id' in st.session_state: del st.session_state.last_order_id
                st.switch_page("views/shop.py")
        with c2:
            if st.button("Kiểm tra đơn hàng vừa đặt 📦", use_container_width=True):
                del st.session_state.order_placed
                if 'last_order_id' in st.session_state: del st.session_state.last_order_id
                st.switch_page("views/profile.py")
                
        st.stop()

    is_guest = not st.session_state.get('user_id')

    if is_guest:
        class GuestCartItem:
            def __init__(self, id, product_id, quantity):
                self.id = id
                self.product_id = product_id
                self.quantity = quantity
        cart_items_all = [GuestCartItem(**d) for d in st.session_state.get('guest_cart', [])]
    else:
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
        
        from datetime import datetime, timedelta
        min_date = datetime.now().date() + timedelta(days=1)
        delivery_date = st.date_input("Ngày mong muốn nhận hàng", value=min_date, min_value=min_date)
        
        note = st.text_input("Ghi chú (Tùy chọn)", placeholder="e.g. Giao hàng trong giờ hành chính.")
        
        shipping_method = st.radio(
            "Phương thức vận chuyển",
            ["Giao hàng tiêu chuẩn (COD)", "Giao hàng hỏa tốc"],
            horizontal=True
        )
        
        st.markdown(f"**Phí vận chuyển ước tính:** {'Chưa tính (Mặc định 30k)' if not st.session_state.shipping_calculated else f'{shipping_fee:,.0f} VNĐ'}")
        
        if st.button("📍 Tính phí vận chuyển (Bắt buộc trước khi thanh toán)", use_container_width=True):
            if shipping_method == "Giao hàng tiêu chuẩn (COD)":
                if province != "Hà Nội":
                    st.session_state.shipping_fee = 30000
                    st.session_state.ship_msg = "Phí giao hàng tiêu chuẩn ngoại thành là 30.000 VNĐ."
                else:
                    st.session_state.shipping_fee = 15000
                    st.session_state.ship_msg = "Phí giao hàng tiêu chuẩn là 15.000 VNĐ."
                st.session_state.shipping_calculated = True
                st.session_state.ship_msg_type = "success"
                st.rerun()
            else:
                if province != "Hà Nội":
                    st.session_state.shipping_fee = 30000
                    st.session_state.shipping_calculated = True
                    st.session_state.ship_msg = "Giao hàng hỏa tốc chỉ áp dụng tại Hà Nội. Áp dụng phí COD mặc định."
                    st.session_state.ship_msg_type = "error"
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
                            st.session_state.ship_msg = f"Khoảng cách ước tính: {dist:.1f} km. Phí ship hỏa tốc: {st.session_state.shipping_fee:,.0f} VNĐ"
                            st.session_state.ship_msg_type = "success"
                            st.rerun()
                        else:
                            st.session_state.ship_msg = "Không tìm thấy địa chỉ trên bản đồ. Vui lòng chọn Giao hàng tiêu chuẩn."
                            st.session_state.ship_msg_type = "error"
                            st.session_state.shipping_fee = 15000
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
            st.info("🔒 Form thanh toán an toàn")
            
            card_type = st.radio("Loại thẻ", ["Visa", "MasterCard", "JCB", "Napas"], horizontal=True)
            
            if card_type == "Visa":
                bg_gradient = "linear-gradient(135deg, #1a1f71 0%, #005ce6 100%)"
                logo = "VISA"
            elif card_type == "MasterCard":
                bg_gradient = "linear-gradient(135deg, #231f20 0%, #cc0000 50%, #ff6600 100%)"
                logo = "MasterCard"
            elif card_type == "JCB":
                bg_gradient = "linear-gradient(135deg, #007940 0%, #00a859 100%)"
                logo = "JCB"
            else:
                bg_gradient = "linear-gradient(135deg, #008f51 0%, #f47d31 100%)"
                logo = "NAPAS"
            
            # CSS for realistic credit card
            st.markdown(f"""
            <style>
            .credit-card {{
                background: {bg_gradient};
                border-radius: 15px;
                padding: 20px;
                color: white;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                margin-bottom: 20px;
                font-family: 'Courier New', Courier, monospace;
                position: relative;
            }}
            .cc-chip {{
                width: 40px;
                height: 30px;
                background: #ffcc00;
                border-radius: 5px;
                margin-bottom: 15px;
            }}
            .cc-logo {{
                position: absolute;
                top: 20px;
                right: 20px;
                font-size: 1.5rem;
                font-weight: bold;
                font-style: italic;
                font-family: 'Arial', sans-serif;
            }}
            .cc-number {{
                font-size: 1.5rem;
                letter-spacing: 2px;
                margin-bottom: 10px;
            }}
            .cc-details {{
                display: flex;
                justify-content: space-between;
                font-size: 0.9rem;
            }}
            </style>
            """, unsafe_allow_html=True)
            
            cc_name = st.text_input("Tên chủ thẻ (Cardholder Name)", placeholder="TRAN DINH DUC")
            cc_num = st.text_input("Số thẻ (Card Number)", placeholder="0000 0000 0000 0000", max_chars=19)
            cc1, cc2 = st.columns(2)
            with cc1:
                cc_exp = st.text_input("Ngày hết hạn (MM/YY)", placeholder="MM/YY")
            with cc2:
                cc_cvv = st.text_input("CVV", placeholder="123", type="password")
            
            st.markdown(f"""
            <div class="credit-card">
                <div class="cc-logo">{logo}</div>
                <div class="cc-chip"></div>
                <div class="cc-number">{cc_num if cc_num else '**** **** **** ****'}</div>
                <div class="cc-details">
                    <div>{cc_name.upper() if cc_name else 'CARDHOLDER NAME'}</div>
                    <div>{cc_exp if cc_exp else 'MM/YY'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
                
        elif payment_method == "Chuyển khoản ngân hàng":
            if 'pay_code' not in st.session_state:
                import random
                import string
                st.session_state.pay_code = "PAY-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                
            pay_code = st.session_state.pay_code
            
            st.info("🏦 Thông tin tài khoản ngân hàng")
            bc1, bc2 = st.columns([1, 1])
            with bc1:
                st.markdown(f"""
                <div style='background-color:#f8f9fa; padding:15px; border-radius:10px; border-left: 5px solid #005A9E;'>
                <p style='color:#005A9E; font-weight:bold; margin-bottom:5px;'>Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank)</p>
                <p style='margin:0;'><b>Chủ tài khoản:</b> PET SHOP PREMIUM VN</p>
                <p style='margin:0; font-size:1.2rem; color:#d63031; font-weight:bold;'>Số TK: 0123456789</p>
                <p style='margin-top:10px;'><b>Nội dung chuyển khoản:</b> <span style='background:#eccc68; padding:2px 5px; border-radius:3px; font-weight:bold;'>{pay_code}</span></p>
                </div>
                """, unsafe_allow_html=True)
                st.file_uploader("Tải lên hóa đơn chuyển tiền (Tùy chọn)", type=["png", "jpg", "jpeg", "pdf"])
            with bc2:
                qr_data = f"Vietcombank|0123456789|PET SHOP PREMIUM VN|{total}|{pay_code}"
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}", caption="Quét mã QR để thanh toán")
            
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
                
                final_address = f"{address_detail}\n{province}\nEmail: {email}\nGhi chú: {note}\nPhương thức vận chuyển: {shipping_method}\nPhương thức thanh toán: {payment_method}"
                
                new_order = Order(
                    session_id=st.session_state.get('session_id'),
                    user_id=st.session_state.get('user_id'),
                    guest_name=name,
                    guest_phone=phone,
                    guest_address=final_address,
                    total_price=total,
                    status="Pending",
                    delivery_date=delivery_date
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
                if is_guest:
                    st.session_state.guest_cart = [gi for gi in st.session_state.guest_cart if gi['id'] not in st.session_state.checkout_item_ids]
                else:
                    for it in cart_items:
                        db.delete(it)
                db.commit()
                
                st.balloons()
                st.session_state.order_placed = True
                st.session_state.last_order_id = new_order.id
                
                if 'shipping_fee' in st.session_state: del st.session_state.shipping_fee
                if 'shipping_calculated' in st.session_state: del st.session_state.shipping_calculated
                if 'ship_msg' in st.session_state: del st.session_state.ship_msg
                if 'pay_code' in st.session_state: del st.session_state.pay_code
                
                st.rerun()

finally:
    db.close()
