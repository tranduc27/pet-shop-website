import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.cart import Cart
from app.models.wishlist import Wishlist
from app.models.review import Review
from app.models.user import User
from st_app.auth_utils import hash_password, verify_password
from st_app.utils import t

st.title(f"🛍️ {t('shop')}")

db_l = SessionLocal()
try:
    cats = [c[0] for c in db_l.query(Product.category).distinct().all() if c[0]]
finally:
    db_l.close()
categories = ["Tất cả"] + sorted(cats)

scol1, scol2, scol3 = st.columns([2, 1, 1])
with scol1:
    search_query = st.text_input("🔍 Tìm kiếm sản phẩm...", "")
with scol2:
    category_filter = st.selectbox("Danh mục", categories)
with scol3:
    sort_by = st.selectbox("Sắp xếp theo", ["Mặc định", "Giá: Thấp đến cao", "Giá: Cao đến thấp", "Tên: A-Z", "Tên: Z-A"])

@st.dialog("Product Details", width="large")
def product_detail_modal(product):
    cols = st.columns(2)
    with cols[0]:
        img_url = product.image_url if product.image_url else f"https://picsum.photos/seed/{product.id}/400/400"
        if not img_url.startswith("http"):
             img_url = f"https://picsum.photos/seed/{product.id}/400/400"
        st.image(img_url, width="stretch")
    with cols[1]:
        st.header(product.name)
        
        # Calculate rating
        db = SessionLocal()
        try:
            reviews = db.query(Review).filter(Review.product_id == product.id).all()
            avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
            st.caption(f"{'⭐' * int(avg_rating)} ({len(reviews)} reviews)")
        finally:
            db.close()
            
        disc_p = product.discount_percent if product.discount_percent else 0
        if product.is_today_sale and disc_p > 0:
            new_price = product.price * (1 - disc_p / 100)
            st.markdown(f"**{t('price')}:** <s>{product.price:,.0f} VNĐ</s> <span style='color:#ff4757; font-weight:bold;'>{new_price:,.0f} VNĐ (-{int(disc_p)}%)</span>", unsafe_allow_html=True)
        else:
            st.write(f"**{t('price')}:** {product.price:,.0f} VNĐ")
        st.write(product.description or "No description available.")
        
        stock_limit = max(1, product.stock) if product.stock is not None else 100
        is_out_of_stock = product.stock is not None and product.stock <= 0
        qty = st.number_input(t('quantity'), min_value=1, max_value=stock_limit, value=1, disabled=is_out_of_stock)
        
        c1, c2 = st.columns(2)
        with c1:
            btn_label = t('out_of_stock') if is_out_of_stock else t('add_to_cart')
            if st.button(btn_label, width="stretch", type="primary", disabled=is_out_of_stock):
                if not st.session_state.get("user_id"):
                    st.switch_page("views/login.py")
                else:
                    db = SessionLocal()
                    try:
                        user_id = st.session_state.user_id
                        existing = db.query(Cart).filter_by(user_id=user_id, product_id=product.id).first()
                        if existing:
                            existing.quantity += qty
                        else:
                            new_item = Cart(user_id=user_id, product_id=product.id, quantity=qty)
                            db.add(new_item)
                        db.commit()
                        st.success("Added to cart!")
                        st.rerun()
                    finally:
                        db.close()
        with c2:
            if st.button("❤️ Add to Wishlist", width="stretch"):
                if not st.session_state.get("user_id"):
                    st.switch_page("views/login.py")
                else:
                    db = SessionLocal()
                    try:
                        user_id = st.session_state.user_id
                        exists = db.query(Wishlist).filter_by(user_id=user_id, product_id=product.id).first()
                        if not exists:
                            wl = Wishlist(user_id=user_id, product_id=product.id)
                            db.add(wl)
                            db.commit()
                            st.success("Added to wishlist!")
                        else:
                            st.info("Already in wishlist")
                    finally:
                        db.close()
                    
    st.divider()
    st.subheader("Customer Reviews")
    db = SessionLocal()
    try:
        reviews = db.query(Review).filter(Review.product_id == product.id).order_by(Review.created_at.desc()).all()
        if reviews:
            for r in reviews:
                st.markdown(f"**{r.reviewer_name}** {'⭐' * r.rating}")
                st.write(f"_{r.comment}_")
                st.markdown("---")
        else:
            st.info("No reviews yet for this product.")
            
        with st.expander("📝 Write a Review"):
            with st.form(f"review_form_{product.id}"):
                rev_name = st.text_input("Your Name", "Guest")
                rev_rating = st.slider("Rating", 1, 5, 5)
                rev_comment = st.text_area("Your Review")
                if st.form_submit_button("Submit"):
                    new_rev = Review(reviewer_name=rev_name, rating=rev_rating, comment=rev_comment, product_id=product.id)
                    db.add(new_rev)
                    db.commit()
                    st.success("Review added!")
                    st.rerun()
    finally:
        db.close()

db = SessionLocal()
try:
    products_query = db.query(Product)
    if search_query:
        products_query = products_query.filter(Product.name.ilike(f"%{search_query}%"))
    if category_filter != "Tất cả":
        products_query = products_query.filter(Product.category == category_filter)
    products = products_query.all()
    
    if sort_by == "Giá: Thấp đến cao":
        products.sort(key=lambda x: x.price * (1 - (x.discount_percent or 0) / 100) if x.is_today_sale else x.price)
    elif sort_by == "Giá: Cao đến thấp":
        products.sort(key=lambda x: x.price * (1 - (x.discount_percent or 0) / 100) if x.is_today_sale else x.price, reverse=True)
    elif sort_by == "Tên: A-Z":
        products.sort(key=lambda x: x.name.lower())
    elif sort_by == "Tên: Z-A":
        products.sort(key=lambda x: x.name.lower(), reverse=True)
    
    # If a product was selected from home page
    if 'selected_product_id' in st.session_state:
        selected_id = st.session_state.selected_product_id
        del st.session_state.selected_product_id
        prod = next((p for p in products if p.id == selected_id), None)
        if prod:
            product_detail_modal(prod)
            
    cols = st.columns(3)
    for i, prod in enumerate(products):
        with cols[i % 3]:
            # Simple card
            img_url = prod.image_url if prod.image_url else f"https://picsum.photos/seed/{prod.id}/400/400"
            if not img_url.startswith("http"):
                 img_url = f"https://picsum.photos/seed/{prod.id}/400/400"
            
            disc_p = prod.discount_percent if prod.discount_percent else 0
            if prod.is_today_sale and disc_p > 0:
                new_price = prod.price * (1 - disc_p / 100)
                price_html = f"<s>{prod.price:,.0f} VNĐ</s> <span style='color: #ff4757; font-weight: bold;'>➔ {new_price:,.0f} VNĐ</span>"
            else:
                price_html = f"{prod.price:,.0f} VNĐ"
            
            st.markdown(f"""
            <div class="product-card">
                <img src="{img_url}" class="product-image" />
                <h4 style="margin-top: 15px;">{prod.name}</h4>
                <p style="color: #888; font-size: 14px;">{price_html}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Details", key=f"shop_view_{prod.id}", width="stretch"):
                product_detail_modal(prod)
finally:
    db.close()
