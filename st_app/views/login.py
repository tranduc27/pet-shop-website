import streamlit as st
from app.database import SessionLocal
from app.models.user import User
from st_app.auth_utils import hash_password, verify_password

st.title("🔐 Login / Sign Up")

tab1, tab2 = st.tabs(["Login", "Sign Up (New Account)"])

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
        if st.form_submit_button("Sign Up & Login", type="primary", width="stretch"):
            if not su or not sp:
                st.error("Please fill in both fields.")
            else:
                db_l = SessionLocal()
                try:
                    user_exist = db_l.query(User).filter(User.username == su).first()
                    if user_exist:
                        st.error("Username already exists. Please choose another.")
                    else:
                        new_u = User(username=su, password=hash_password(sp))
                        db_l.add(new_u)
                        db_l.commit()
                        st.session_state.user_id = new_u.id
                        st.session_state.username = new_u.username
                        st.success("Account created successfully!")
                        st.switch_page("views/shop.py")
                finally:
                    db_l.close()
