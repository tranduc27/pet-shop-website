import streamlit as st
import time
from app.database import SessionLocal
from app.models.user import User
from st_app.auth_utils import hash_password, verify_password
from st_app.email_service import generate_otp, send_otp_email
from app.models.cart import Cart

st.title("🔐 Đăng ký / Đăng nhập")

if "login_message" in st.session_state:
    st.info(st.session_state.login_message)
    del st.session_state.login_message

tab1, tab2, tab3 = st.tabs(["Đăng nhập", "Đăng ký", "Quên mật khẩu"])

with tab1:
    with st.form("login_form"):
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu ", type="password")
        if st.form_submit_button("Đăng nhập", type="primary", width="stretch"):
            if not u or not p:
                st.error("Vui lòng điền đầy đủ")
            else:
                db_l = SessionLocal()
                try:
                    user_exist = db_l.query(User).filter(User.username == u).first()
                    if user_exist and verify_password(p, user_exist.password):
                        st.session_state.user_id = user_exist.id
                        st.session_state.username = user_exist.username
                        
                        if "guest_cart" in st.session_state and st.session_state.guest_cart:
                            for item in st.session_state.guest_cart:
                                existing = db_l.query(Cart).filter_by(user_id=user_exist.id, product_id=item['product_id']).first()
                                if existing:
                                    existing.quantity += item['quantity']
                                else:
                                    new_item = Cart(user_id=user_exist.id, product_id=item['product_id'], quantity=item['quantity'])
                                    db_l.add(new_item)
                            db_l.commit()
                            st.session_state.guest_cart = []
                            
                        st.success("Đăng nhập thành công")
                        st.switch_page("views/shop.py")
                    else:
                        st.error("Tên đăng nhập hoặc mật khẩu không hợp lệ")
                finally:
                    db_l.close()

with tab2:
    with st.form("signup_form"):
        su = st.text_input("Tên đăng nhập", key="su")
        sp = st.text_input("Mật khẩu", type="password", key="sp")
        se = st.text_input("Email", key="se", placeholder="example@gmail.com")
        sphone = st.text_input("Số điện thoại", key="sphone", placeholder="0123...")
        if st.form_submit_button("Đăng ký & Đăng nhập", type="primary", width="stretch"):
            if not su or not sp or not sphone:
                st.error("Vui lòng điền đầy đủ thông tin")
            else:
                db_l = SessionLocal()
                try:
                    user_exist = db_l.query(User).filter(User.username == su).first()
                    if user_exist:
                        st.error("Tên đăng nhập đã tồn tại. Vui lòng chọn tên đăng nhập khác")
                    else:
                        new_u = User(username=su, password=hash_password(sp), email=se, phone=sphone)
                        db_l.add(new_u)
                        db_l.commit()
                        st.session_state.user_id = new_u.id
                        st.session_state.username = new_u.username
                        
                        if "guest_cart" in st.session_state and st.session_state.guest_cart:
                            for item in st.session_state.guest_cart:
                                existing = db_l.query(Cart).filter_by(user_id=new_u.id, product_id=item['product_id']).first()
                                if existing:
                                    existing.quantity += item['quantity']
                                else:
                                    new_item = Cart(user_id=new_u.id, product_id=item['product_id'], quantity=item['quantity'])
                                    db_l.add(new_item)
                            db_l.commit()
                            st.session_state.guest_cart = []
                            
                        st.success("Tài khoản đã được tạo thành công")
                        st.switch_page("views/shop.py")
                finally:
                    db_l.close()

with tab3:
    st.subheader("Khôi phục mật khẩu")
    if "reset_step" not in st.session_state:
        st.session_state.reset_step = 1

    if st.session_state.reset_step == 1:
        email = st.text_input("Điền Email bạn đã đăng ký", key="fg_email")
        if st.button("Gửi OTP", key="send_otp_btn"):
            if not email:
                st.error("Hãy nhập email của bạn")
            else:
                db_l = SessionLocal()
                try:
                    user = db_l.query(User).filter(User.email == email).first()
                    if not user:
                        st.error("Không có tài khoản nào tương ứng với email")
                    else:
                        otp = generate_otp()
                        st.session_state.reset_otp = otp
                        st.session_state.reset_email = email
                        st.session_state.reset_user_id = user.id
                        st.session_state.otp_created_at = time.time()
                        if send_otp_email(email, otp):
                            st.session_state.reset_step = 2
                            st.success("OTP đã được gửi tới email của bạn!")
                            st.rerun()
                finally:
                    db_l.close()

    elif st.session_state.reset_step == 2:
        st.info(f"An OTP has been sent to {st.session_state.reset_email}")
        if "dev_otp_msg" in st.session_state:
            st.warning(st.session_state.dev_otp_msg)
        entered_otp = st.text_input("Enter OTP", key="entered_otp")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verify OTP", key="verify_otp_btn"):
                if time.time() - st.session_state.get('otp_created_at', 0) > 120:
                    st.error("Mã OTP đã hết hạn (quá 2 phút). Vui lòng chọn Cancel và yêu cầu gửi mã mới.")
                elif 'reset_otp' in st.session_state and entered_otp == st.session_state.reset_otp:
                    st.session_state.reset_step = 3
                    st.success("OTP verified!")
                    # Vô hiệu hóa OTP ngay sau khi sử dụng thành công
                    del st.session_state.reset_otp
                    del st.session_state.otp_created_at
                    st.rerun()
                else:
                    st.error("Invalid OTP. Please try again.")
        with col2:
            if st.button("Cancel", key="cancel_otp_btn"):
                st.session_state.reset_step = 1
                if 'reset_otp' in st.session_state: del st.session_state.reset_otp
                if 'dev_otp_msg' in st.session_state: del st.session_state.dev_otp_msg
                if 'otp_created_at' in st.session_state: del st.session_state.otp_created_at
                st.rerun()

    elif st.session_state.reset_step == 3:
        new_pass = st.text_input("Nhập mật khẩu mới", type="password", key="new_pass")
        confirm_pass = st.text_input("Xác nhận mật khẩu", type="password", key="confirm_pass")
        if st.button("Đặt lại mật khẩu", key="reset_pass_btn"):
            if new_pass and new_pass == confirm_pass:
                db_l = SessionLocal()
                try:
                    user = db_l.query(User).filter(User.id == st.session_state.reset_user_id).first()
                    if user:
                        user.password = hash_password(new_pass)
                        db_l.commit()
                        st.success("Mật khẩu đã được đặt lại thành công")
                        st.session_state.reset_step = 1
                        if 'reset_otp' in st.session_state: del st.session_state.reset_otp
                        if 'reset_email' in st.session_state: del st.session_state.reset_email
                        if 'reset_user_id' in st.session_state: del st.session_state.reset_user_id
                        if 'dev_otp_msg' in st.session_state: del st.session_state.dev_otp_msg
                        if 'otp_created_at' in st.session_state: del st.session_state.otp_created_at
                        # Cố tình không chạy lại để họ có thể đọc thông báo thành công và nhấp vào Đăng nhập
                finally:
                    db_l.close()
            else:
                st.error("Mật khẩu không khớp hoặc để trống")
