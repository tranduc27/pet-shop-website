import streamlit as st
from app.database import SessionLocal
from app.models.cart import Cart
from app.models.order import Order
from app.models.product import Product
from st_app.utils import t

st.title(f"💳 {t('checkout')}")

db = SessionLocal()
try:
    # First check if the order has just been placed
    if st.session_state.get('order_placed'):
        st.success("🎉 Order placed successfully! We will contact you soon to confirm your delivery.")
        st.info("Your order is being processed. Thank you for shopping with us!")
        if st.button("Return to Shop 🛍️"):
            del st.session_state.order_placed
            st.switch_page("views/shop.py")
        st.stop()

    if not st.session_state.get('user_id'):
        st.warning("⚠️ Please login from the shop page to proceed to checkout.")
        st.stop()

    cart_items_all = db.query(Cart).filter_by(user_id=st.session_state.user_id).all()
    if 'checkout_item_ids' in st.session_state:
        cart_items = [item for item in cart_items_all if item.id in st.session_state.checkout_item_ids]
    else:
        cart_items = cart_items_all
    if not cart_items:
        st.info("🛒 Your cart is empty. Please add some products to proceed with checkout.")
        if st.button("Return to Shop"):
            st.switch_page("views/shop.py")
        st.stop()
        
    # Calculate totals
    subtotal = sum([(db.query(Product).filter_by(id=item.product_id).first().price * item.quantity) for item in cart_items if db.query(Product).filter_by(id=item.product_id).first()])
    shipping_fee = 30000 if subtotal < 1000000 else 0.00
    total = subtotal + shipping_fee
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 📋 Order Summary")
        st.markdown("<div style='background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
        for item in cart_items:
            prod = db.query(Product).filter_by(id=item.product_id).first()
            if prod:
                st.markdown(f"**{prod.name}**  \n`x{item.quantity}` - {prod.price * item.quantity:,.0f} VNĐ")
        st.divider()
        st.markdown(f"**Subtotal:** {subtotal:,.0f} VNĐ")
        if shipping_fee == 0:
            st.markdown(f"**Shipping Fee:** 🟢 Free")
        else:
            st.markdown(f"**Shipping Fee:** {shipping_fee:,.0f} VNĐ")
        st.markdown(f"### **Total: <span style='color:#0068FF'>{total:,.0f} VNĐ</span>**", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col1:
        st.markdown(f"### 📍 Delivery Information")
        name = st.text_input("Full Name", placeholder="e.g. Tran Dinh Duc")
        
        c_phone, c_email = st.columns(2)
        with c_phone:
            phone = st.text_input("Phone Number", placeholder="0988...")
        with c_email:
            email = st.text_input("Email (Optional)", placeholder="example@gmail.com")
            
        address = st.text_area("Detailed Shipping Address", placeholder="e.g. 123 Hanoi Street, Hoan Kiem, HN")
        note = st.text_input("Order Notes (Optional)", placeholder="e.g. Deliver during office hours.")
        
        st.markdown("---")
        st.markdown(f"### 💵 Payment Method")
        
        payment_method = st.radio(
            "Select Payment Method",
            ["Cash on Delivery (COD)", "Credit/Debit Card", "Bank Transfer", "E-Wallet (MoMo/ZaloPay)"],
            horizontal=False
        )
        
        # Payment Method Conditional UI
        if payment_method == "Credit/Debit Card":
            st.info("🔒 Secure Card Payment Form")
            cc_name = st.text_input("Cardholder Name", placeholder="TRAN DINH DUC")
            cc_num = st.text_input("Card Number", placeholder="0000 0000 0000 0000", max_chars=19)
            cc1, cc2 = st.columns(2)
            with cc1:
                st.text_input("Expiry Date", placeholder="MM/YY")
            with cc2:
                st.text_input("CVV", placeholder="123", type="password")
                
        elif payment_method == "Bank Transfer":
            st.info("🏦 Bank Account Information")
            st.markdown("""
            Please transfer the amount to the following bank account. **We will verify your transaction manually.**
            
            **Bank:** Vietcombank (VCB)  
            **Account Name:** PET SHOP PREMIUM VN  
            **Account Number:** `0123456789`  
            **Transfer Content:** `PAY-[Your Phone Number]`
            """)
            st.file_uploader("Upload Transfer Receipt (Optional)", type=["png", "jpg", "jpeg", "pdf"])
            
        elif payment_method == "E-Wallet (MoMo/ZaloPay)":
            st.info("📱 Scan QR Code to Pay via MoMo/ZaloPay")
            c_qr1, c_qr2, _ = st.columns([1,1,2])
            with c_qr1:
                st.markdown("**MoMo**")
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=MoMoPayment", width=120)
            with c_qr2:
                st.markdown("**ZaloPay**")
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=ZaloPayPayment", width=120)
        
        st.markdown("---")
        
        # Submit Button
        if st.button("✅ Confirm & Place Order", width="stretch", type="primary"):
            if not name or not phone or not address:
                st.error("⚠️ Please fill in all required delivery information (Name, Phone, Address).")
            elif payment_method == "Credit/Debit Card" and (not cc_name or not cc_num):
                st.error("⚠️ Please fill in your Credit Card details.")
            else:
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
                
                # clear cart
                for it in cart_items:
                    db.delete(it)
                db.commit()
                
                st.balloons()
                st.session_state.order_placed = True
                st.rerun()

finally:
    db.close()
