import streamlit as st
import time
from app.database import SessionLocal
from app.models.user import User
from st_app.auth_utils import hash_password, verify_password
from st_app.email_service import generate_otp, send_otp_email

st.title("🔐 Login / Sign Up")

tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])

with tab1:
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login", type="primary", width="stretch"):
            if not u or not p:
                st.error("Please fill in both fields.")
            else:
                db_l = SessionLocal()
                try:
                    user_exist = db_l.query(User).filter(User.username == u).first()
                    if user_exist and verify_password(p, user_exist.password):
                        st.session_state.user_id = user_exist.id
                        st.session_state.username = user_exist.username
                        st.success("Logged in successfully! You can now access your cart and wishlist.")
                        st.switch_page("views/shop.py")
                    else:
                        st.error("Invalid username or password.")
                finally:
                    db_l.close()

with tab2:
    with st.form("signup_form"):
        su = st.text_input("Choose a Username", key="su")
        sp = st.text_input("Choose a Password", type="password", key="sp")
        se = st.text_input("Gmail (Optional)", key="se", placeholder="example@gmail.com")
        sphone = st.text_input("Phone Number", key="sphone", placeholder="0123...")
        if st.form_submit_button("Sign Up & Login", type="primary", width="stretch"):
            if not su or not sp or not sphone:
                st.error("Please fill in Username, Password and Phone Number.")
            else:
                db_l = SessionLocal()
                try:
                    user_exist = db_l.query(User).filter(User.username == su).first()
                    if user_exist:
                        st.error("Username already exists. Please choose another.")
                    else:
                        new_u = User(username=su, password=hash_password(sp), email=se, phone=sphone)
                        db_l.add(new_u)
                        db_l.commit()
                        st.session_state.user_id = new_u.id
                        st.session_state.username = new_u.username
                        st.success("Account created successfully!")
                        st.switch_page("views/shop.py")
                finally:
                    db_l.close()

with tab3:
    st.subheader("Recover Password")
    if "reset_step" not in st.session_state:
        st.session_state.reset_step = 1

    if st.session_state.reset_step == 1:
        email = st.text_input("Enter your registered Email", key="fg_email")
        if st.button("Send OTP", key="send_otp_btn"):
            if not email:
                st.error("Please enter your email.")
            else:
                db_l = SessionLocal()
                try:
                    user = db_l.query(User).filter(User.email == email).first()
                    if not user:
                        st.error("No account found with this email.")
                    else:
                        otp = generate_otp()
                        st.session_state.reset_otp = otp
                        st.session_state.reset_email = email
                        st.session_state.reset_user_id = user.id
                        st.session_state.otp_created_at = time.time()
                        if send_otp_email(email, otp):
                            st.session_state.reset_step = 2
                            st.success("OTP sent to your email!")
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
                elif entered_otp == st.session_state.reset_otp:
                    st.session_state.reset_step = 3
                    st.success("OTP verified!")
                    st.rerun()
                else:
                    st.error("Invalid OTP. Please try again.")
        with col2:
            if st.button("Cancel", key="cancel_otp_btn"):
                st.session_state.reset_step = 1
                if 'dev_otp_msg' in st.session_state: del st.session_state.dev_otp_msg
                if 'otp_created_at' in st.session_state: del st.session_state.otp_created_at
                st.rerun()

    elif st.session_state.reset_step == 3:
        new_pass = st.text_input("Enter New Password", type="password", key="new_pass")
        confirm_pass = st.text_input("Confirm New Password", type="password", key="confirm_pass")
        if st.button("Reset Password", key="reset_pass_btn"):
            if new_pass and new_pass == confirm_pass:
                db_l = SessionLocal()
                try:
                    user = db_l.query(User).filter(User.id == st.session_state.reset_user_id).first()
                    if user:
                        user.password = hash_password(new_pass)
                        db_l.commit()
                        st.success("Password reset successfully! You can now login in the Login tab.")
                        st.session_state.reset_step = 1
                        if 'reset_otp' in st.session_state: del st.session_state.reset_otp
                        if 'reset_email' in st.session_state: del st.session_state.reset_email
                        if 'reset_user_id' in st.session_state: del st.session_state.reset_user_id
                        if 'dev_otp_msg' in st.session_state: del st.session_state.dev_otp_msg
                        if 'otp_created_at' in st.session_state: del st.session_state.otp_created_at
                        # Don't rerun intentionally so they can read the success message and click Login instead
                finally:
                    db_l.close()
            else:
                st.error("Passwords do not match or cannot be empty.")
