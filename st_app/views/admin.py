import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review
import pandas as pd
import cloudinary
import cloudinary.uploader

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
                p_image = st.text_input("Image URL (Optional)", placeholder="https://example.com/image.jpg")
                p_image_file = st.file_uploader("Or Upload Image to Cloudinary", type=["png", "jpg", "jpeg", "webp"])
                p_sale = st.checkbox("Today's Sale?")
                p_disc = st.number_input("Discount %", min_value=0.0, max_value=100.0)
                if st.form_submit_button("Add Product"):
                    final_image_url = p_image
                    if p_image_file is not None:
                        try:
                            if "cloudinary" in st.secrets:
                                cloudinary.config(
                                  cloud_name = st.secrets["cloudinary"]["cloud_name"],
                                  api_key = st.secrets["cloudinary"]["api_key"],
                                  api_secret = st.secrets["cloudinary"]["api_secret"]
                                )
                            response = cloudinary.uploader.upload(p_image_file)
                            final_image_url = response['secure_url']
                        except Exception as e:
                            st.error(f"Lỗi tải ảnh lên Cloudinary: {e}")
                            st.stop()
                    
                    new_p = Product(name=p_name, price=p_price, stock=p_stock, description=p_desc, image_url=final_image_url, is_today_sale=p_sale, discount_percent=p_disc)
                    db.add(new_p)
                    db.commit()
                    st.success("Product added!")
                    st.rerun()
                    
        prods = db.query(Product).all()
        if prods:
            df = pd.DataFrame([{
                'ID': p.id, 'Name': p.name, 'Description': p.description if p.description else '', 'Price': p.price, 'Stock': p.stock if p.stock is not None else 0, 
                'Image URL': p.image_url if p.image_url else '',
                'On Sale': p.is_today_sale, 'Discount %': p.discount_percent if p.discount_percent is not None else 0.0
            } for p in prods])
            
            edited_df = st.data_editor(df, width="stretch", disabled=["ID"], key="product_editor")
            
            if st.button("Save Changes", type="primary"):
                for index, row in edited_df.iterrows():
                    p_id = row['ID']
                    p = db.query(Product).filter_by(id=p_id).first()
                    if p:
                        p.name = row['Name']
                        p.description = row.get('Description', '')
                        p.price = float(row['Price'])
                        p.stock = int(row['Stock'])
                        p.image_url = row['Image URL'] if row['Image URL'] else None
                        p.is_today_sale = bool(row['On Sale'])
                        p.discount_percent = float(row['Discount %'])
                db.commit()
                st.success("Successfully updated products!")
                st.rerun()
                
            with st.expander("Delete a Product"):
                with st.form("delete_product_form"):
                    prod_id_to_delete = st.number_input("Product ID to delete", min_value=0, step=1)
                    if st.form_submit_button("Delete", type="primary"):
                        prod_to_del = db.query(Product).filter_by(id=prod_id_to_delete).first()
                        if prod_to_del:
                            db.delete(prod_to_del)
                            db.commit()
                            st.success(f"Product #{prod_id_to_delete} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Product not found.")
                            
    with tab2:
        st.subheader("View Orders")
        orders = db.query(Order).all()
        if orders:
            odf = pd.DataFrame([{
                'ID': o.id, 'Status': o.status, 'Guest Name': o.guest_name, 'Total': o.total_price, 'Date': o.created_at
            } for o in orders])
            st.dataframe(odf, width="stretch")
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
            st.dataframe(rev_df, width="stretch")
            
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
