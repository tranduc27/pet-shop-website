import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.review import Review
from st_app.utils import t

st.title(f"🐶 {t('home')}")

# Hero Section
st.markdown("""
<div style='background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=1200");
background-size: cover; background-position: center; border-radius: 20px; padding: 60px; text-align: center; color: white;'>
    <h1 style='font-size: 3em; margin-bottom: 10px; color: white;'>Premium Pet Supplies</h1>
    <p style='font-size: 1.2em;'>Give your best friend the love they deserve with our top-quality products.</p>
</div>
<br>
""", unsafe_allow_html=True)

st.subheader(f"🔥 {t('today_sales')}")

db = SessionLocal()
try:
    # Get products on sale
    sales = db.query(Product).filter(Product.is_today_sale == True).all()
    if not sales:
        st.info("No sales today. Check back tomorrow!")
    else:
        cols = st.columns(4)
        for i, prod in enumerate(sales):
            with cols[i % 4]:
                img_url = prod.image_url if prod.image_url else "https://via.placeholder.com/400"
                if not img_url.startswith("http"):
                    img_url = "https://picsum.photos/seed/" + str(prod.id) + "/400/400"
                
                disc_p = prod.discount_percent if prod.discount_percent else 0
                if prod.is_today_sale and disc_p > 0:
                    new_price = prod.price * (1 - disc_p / 100)
                    price_html = f"<s>&#36;{prod.price:.2f}</s> <span style='color: #ff4757; font-weight: bold;'>➔ &#36;{new_price:.2f}</span>"
                else:
                    price_html = f"&#36;{prod.price:.2f}"
                
                # HTML card rendering for beautiful UI
                st.markdown(f"""
                <div style="position: relative;" class="product-card">
                    <div class="discount-badge">-{int(disc_p)}%</div>
                    <img src="{img_url}" class="product-image" />
                    <h4 style="margin-top: 15px;">{prod.name}</h4>
                    <p style="color: #888; font-size: 14px;">{price_html}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View ##{prod.id}", key=f"view_sale_{prod.id}", use_container_width=True):
                    st.session_state.selected_product_id = prod.id
                    st.switch_page("views/shop.py")

    st.divider()
    st.subheader("🌟 Customer Testimonials")
    reviews = db.query(Review).filter(Review.product_id == None).order_by(Review.created_at.desc()).limit(5).all()
    if reviews:
        for r in reviews:
            st.markdown(f"**{r.reviewer_name}** {'⭐' * r.rating}")
            st.write(f"_{r.comment}_")
            st.caption(f"{r.created_at.strftime('%Y-%m-%d')} - Verified")
            st.markdown("---")
    else:
        st.info("No shop reviews yet. Be the first!")
        
    with st.expander("📝 Leave a Review for Pet Shop Premium"):
        with st.form("shop_review"):
            rev_name = st.text_input("Your Name", "Guest")
            rev_rating = st.slider("Rating", 1, 5, 5)
            rev_comment = st.text_area("Your Review")
            if st.form_submit_button("Submit Review"):
                new_rev = Review(reviewer_name=rev_name, rating=rev_rating, comment=rev_comment, product_id=None)
                db.add(new_rev)
                db.commit()
                st.success("Thank you for your feedback!")
                st.rerun()

finally:
    db.close()
