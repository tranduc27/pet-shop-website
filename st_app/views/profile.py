import streamlit as st
import pandas as pd
from app.database import SessionLocal
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product

st.title("👤 My Profile")

if "user_id" not in st.session_state:
    st.warning("Please log in to view your profile.")
    if st.button("Go to Login"):
        st.switch_page("views/login.py")
    st.stop()

db = SessionLocal()
try:
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    if not user:
        st.error("User not found.")
        st.stop()

    # Tạo các cột bố cục
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Basic Information")
        st.markdown(f"**Username:** {user.username}")
        st.markdown(f"**Email:** {user.email or 'Not provided'}")
        st.markdown(f"**Phone:** {user.phone or 'Not provided'}")
        
    with col2:
        st.header("🛒 Order History")

        orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
        
        if not orders:
            st.info("You haven't placed any orders yet.")
        else:
            for order in orders:
                # Định dạng tiêu đề đơn hàng
                dt_str = order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else "Unknown Date"
                title = f"Order #{order.id} - {dt_str} | Total: ${order.total_price:.2f} | Status: {order.status.capitalize()}"
                
                with st.expander(title):
                    st.write(f"**Delivery Name:** {order.guest_name or user.username}")
                    st.write(f"**Delivery Phone:** {order.guest_phone or user.phone or 'N/A'}")
                    st.write(f"**Delivery Address:** {order.guest_address or 'N/A'}")
                    
                    # Lấy danh sách sản phẩm
                    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
                    if items:
                        item_data = []
                        for item in items:
                            product = db.query(Product).filter(Product.id == item.product_id).first()
                            product_name = product.name if product else "Unknown Product"
                            item_data.append({
                                "Product": product_name,
                                "Quantity": item.quantity,
                                "Price/Unit": f"${item.price:.2f}"
                            })
                        st.table(pd.DataFrame(item_data))
                    else:
                        st.write("No items found for this order.")
finally:
    db.close()
