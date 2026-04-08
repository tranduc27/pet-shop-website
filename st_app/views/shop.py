import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.cart import Cart
from app.models.wishlist import Wishlist
from app.models.review import Review
from st_app.utils import t

st.title(f"🛍️ {t('shop')}")

@st.dialog("Product Details", width="large")
def product_detail_modal(product):
    cols = st.columns(2)
    with cols[0]:
        img_url = product.image_url if product.image_url else f"https://picsum.photos/seed/{product.id}/400/400"
        if not img_url.startswith("http"):
             img_url = f"https://picsum.photos/seed/{product.id}/400/400"
        st.image(img_url, use_container_width=True)
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
            st.markdown(f"**{t('price')}:** <s>&#36;{product.price:.2f}</s> <span style='color:#ff4757; font-weight:bold;'>&#36;{new_price:.2f} (-{int(disc_p)}%)</span>", unsafe_allow_html=True)
        else:
            st.write(f"**{t('price')}:** ${product.price:.2f}")
        st.write(product.description or "No description available.")
        
        size = st.selectbox(t('size'), product.size.split(',') if product.size else ["Default"])
        stock_limit = max(1, product.stock) if product.stock is not None else 100
        qty = st.number_input(t('quantity'), min_value=1, max_value=stock_limit, value=1)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t('add_to_cart'), use_container_width=True, type="primary"):
                db = SessionLocal()
                try:
                    session_id = st.session_state.session_id
                    existing = db.query(Cart).filter_by(session_id=session_id, product_id=product.id).first()
                    if existing:
                        existing.quantity += qty
                    else:
                        new_item = Cart(session_id=session_id, product_id=product.id, quantity=qty)
                        db.add(new_item)
                    db.commit()
                    st.success("Added to cart!")
                    st.rerun()
                finally:
                    db.close()
        with c2:
            if st.button("❤️ Add to Wishlist", use_container_width=True):
                db = SessionLocal()
                try:
                    exists = db.query(Wishlist).filter_by(session_id=st.session_state.session_id, product_id=product.id).first()
                    if not exists:
                        wl = Wishlist(session_id=st.session_state.session_id, product_id=product.id)
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
    products = db.query(Product).all()
    
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
                price_html = f"<s>&#36;{prod.price:.2f}</s> <span style='color: #ff4757; font-weight: bold;'>➔ &#36;{new_price:.2f}</span>"
            else:
                price_html = f"&#36;{prod.price:.2f}"
            
            st.markdown(f"""
            <div class="product-card">
                <img src="{img_url}" class="product-image" />
                <h4 style="margin-top: 15px;">{prod.name}</h4>
                <p style="color: #888; font-size: 14px;">{price_html}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Details", key=f"shop_view_{prod.id}", use_container_width=True):
                product_detail_modal(prod)
finally:
    db.close()
