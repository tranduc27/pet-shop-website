import streamlit as st
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.order import Order
from app.models.product import Product
from st_app.utils import t

st.title(f"💳 {t('checkout')}")

db = SessionLocal()
try:
    cart_items = db.query(Cart).filter_by(session_id=st.session_state.session_id).all()
    if not cart_items:
        st.warning("Your cart is empty.")
        st.stop()
        
    total = sum([(db.query(Product).filter_by(id=item.product_id).first().price * item.quantity) for item in cart_items if db.query(Product).filter_by(id=item.product_id).first()])
    
    st.subheader(f"Order Summary: ${total:.2f}")
    
    st.write(f"### {t('guest_checkout')}")
    with st.form("checkout_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        address = st.text_area("Shipping Address")
        
        submitted = st.form_submit_button(t("submit_order"), type="primary")
        if submitted:
            if not name or not phone or not address:
                st.error("Please fill in all fields.")
            else:
                new_order = Order(
                    session_id=st.session_state.session_id,
                    guest_name=name,
                    guest_phone=phone,
                    guest_address=address,
                    total_price=total,
                    status="Pending"
                )
                db.add(new_order)
                # clear cart
                for it in cart_items:
                    db.delete(it)
                db.commit()
                st.success("Order placed successfully! Thank you for shopping with us.")
                st.balloons()
                st.session_state.order_placed = True
                
    if st.session_state.get('order_placed'):
        if st.button("Return to Shop"):
            del st.session_state.order_placed
            st.switch_page("views/shop.py")
finally:
    db.close()
