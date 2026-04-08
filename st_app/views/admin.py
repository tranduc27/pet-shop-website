import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review
import pandas as pd

st.title("⚙️ Admin Panel")

# Simple protection
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    with st.form("admin_login"):
        username = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if username == "admin" and pwd == "admin":  # simple hardcoded for demo
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Incorrect username or password")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Products", "Orders", "Reviews"])

db = SessionLocal()
try:
    with tab1:
        st.subheader("Manage Products")
        with st.expander("Add New Product"):
            with st.form("add_product"):
                p_name = st.text_input("Name")
                p_price = st.number_input("Price", min_value=0.0)
                p_stock = st.number_input("Stock", min_value=0)
                p_desc = st.text_area("Description")
                p_sale = st.checkbox("Today's Sale?")
                p_disc = st.number_input("Discount %", min_value=0.0, max_value=100.0)
                if st.form_submit_button("Add Product"):
                    new_p = Product(name=p_name, price=p_price, stock=p_stock, description=p_desc, is_today_sale=p_sale, discount_percent=p_disc)
                    db.add(new_p)
                    db.commit()
                    st.success("Product added!")
                    st.rerun()
                    
        prods = db.query(Product).all()
        if prods:
            df = pd.DataFrame([{
                'ID': p.id, 'Name': p.name, 'Price': p.price, 'Stock': p.stock if p.stock is not None else 0, 'On Sale': p.is_today_sale, 'Discount %': p.discount_percent if p.discount_percent is not None else 0.0
            } for p in prods])
            
            edited_df = st.data_editor(df, use_container_width=True, disabled=["ID"], key="product_editor")
            
            if st.button("Save Changes", type="primary"):
                for index, row in edited_df.iterrows():
                    p_id = row['ID']
                    p = db.query(Product).filter_by(id=p_id).first()
                    if p:
                        p.name = row['Name']
                        p.price = float(row['Price'])
                        p.stock = int(row['Stock'])
                        p.is_today_sale = bool(row['On Sale'])
                        p.discount_percent = float(row['Discount %'])
                db.commit()
                st.success("Successfully updated products!")
                st.rerun()
            
    with tab2:
        st.subheader("View Orders")
        orders = db.query(Order).all()
        if orders:
            odf = pd.DataFrame([{
                'ID': o.id, 'Status': o.status, 'Guest Name': o.guest_name, 'Total': o.total_price, 'Date': o.created_at
            } for o in orders])
            st.dataframe(odf, use_container_width=True)
        else:
            st.info("No orders yet.")
            
    with tab3:
        st.subheader("Manage Reviews")
        reviews = db.query(Review).order_by(Review.created_at.desc()).all()
        if reviews:
            rev_df = pd.DataFrame([{
                'ID': r.id, 'Reviewer': r.reviewer_name, 'Rating': r.rating, 
                'Type': f"Product #{r.product_id}" if r.product_id else "Shop",
                'Comment': r.comment, 'Date': r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""
            } for r in reviews])
            st.dataframe(rev_df, use_container_width=True)
            
            with st.expander("Delete a Review"):
                with st.form("delete_review_form"):
                    rev_id_to_delete = st.number_input("Review ID to delete", min_value=1, step=1)
                    if st.form_submit_button("Delete", type="primary"):
                        rev_to_del = db.query(Review).filter_by(id=rev_id_to_delete).first()
                        if rev_to_del:
                            db.delete(rev_to_del)
                            db.commit()
                            st.success(f"Review #{rev_id_to_delete} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Review not found.")
        else:
            st.info("No reviews submitted yet.")
finally:
    db.close()
