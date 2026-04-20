import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.review import Review
from st_app.utils import t

st.title(f"🐶 {t('Trang chủ')}")

# Phần hiển thị chính (Hero Section)
st.markdown("""
<div style='background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=1200");
background-size: cover; background-position: center; border-radius: 20px; padding: 60px; text-align: center; color: white;'>
    <h1 style='font-size: 3em; margin-bottom: 10px; color: white;'>Đồ Dùng Thú Cưng Cao Cấp</h1>
    <p style='font-size: 1.2em;'>Dành trọn yêu thương cho người bạn bốn chân với những sản phẩm chất lượng hàng đầu.</p>
</div>
<br>
""", unsafe_allow_html=True)

st.subheader(f"🔥 {t(' Giảm giá hôm nay')}")

db = SessionLocal()
try:
    # Lấy các sản phẩm đang giảm giá
    sales = db.query(Product).filter(Product.is_today_sale == True).all()
    if not sales:
        st.info("Không có giảm giá ngày hôm nay.")
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
                    price_html = f"<s>{prod.price:,.0f} VNĐ</s> <span style='color: #ff4757; font-weight: bold;'>➔ {new_price:,.0f} VNĐ</span>"
                else:
                    price_html = f"{prod.price:,.0f} VNĐ"
                
                out_of_stock_badge = ""
                if prod.stock is not None and prod.stock <= 0:
                    out_of_stock_badge = "<div style='position:absolute; top:10px; left:10px; background-color:#ff4757; color:white; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; z-index:10;'>Hết hàng</div>"
                
                # Render thẻ HTML để có giao diện đẹp
                st.markdown(f"""
                <div style="position: relative;" class="product-card">
                    {out_of_stock_badge}<div class="discount-badge">-{int(disc_p)}%</div>
                    <img src="{img_url}" class="product-image" />
                    <h4 style="margin-top: 15px;">{prod.name}</h4>
                    <p style="color: #888; font-size: 14px;">{price_html}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(t('Xem chi tiết'), key=f"view_sale_{prod.id}", use_container_width=True):
                    st.session_state.selected_product_id = prod.id
                    st.switch_page("views/shop.py")

    st.divider()
    st.subheader(f"🌟 {t('Đánh giá của khách hàng')}")
    reviews = db.query(Review).filter(Review.product_id == None).order_by(Review.created_at.desc()).limit(5).all()
    if reviews:
        for r in reviews:
            st.markdown(f"**{r.reviewer_name}** {'⭐' * r.rating}")
            st.write(f"_{r.comment}_")
            st.caption(f"{r.created_at.strftime('%Y-%m-%d')} - Xác nhận")
            st.markdown("---")
    else:
        st.info(t('Chưa có đánh giá'))
        
    with st.expander(f"📝 {t('leave_review')}"):
        with st.form("shop_review"):
            rev_name = st.text_input("Tên của bạn", "Khách")
            rev_rating = st.slider("Đánh giá", 1, 5, 5)
            rev_comment = st.text_area("Đánh giá của bạn")
            if st.form_submit_button("Gửi đánh giá"):
                new_rev = Review(reviewer_name=rev_name, rating=rev_rating, comment=rev_comment, product_id=None)
                db.add(new_rev)
                db.commit()
                st.success("Cảm ơn bạn vì đã đánh giá!")
                st.rerun()

    st.markdown("""
        <div style='background-color: var(--secondary-background-color); padding: 40px 20px; border-radius: 15px; margin-top: 40px; text-align: center; border: 1px solid rgba(128, 128, 128, 0.2);'>
            <h3 style='margin-bottom: 20px; font-weight: 600;'>🐾 Pet Shop Premium</h3>
            <div style='color: #666; font-size: 16px; line-height: 1.8;'>
                <p style='margin: 0;'><strong>📍 Địa chỉ:</strong> Học viện Công nghệ Bưu chính Viễn thông cơ sở Trần Phú, Hà Đông, Hà Nội</p>
                <p style='margin: 0;'><strong>📞 Hotline/Zalo:</strong> <a href='https://zalo.me/0375318910' target='_blank' style='color: inherit; text-decoration: none;'>0375 318 910</a></p>
                <p style='margin: 0;'><strong>💬 Facebook:</strong> <a href='https://www.facebook.com/ductrann.27/' target='_blank' style='color: #0084FF; text-decoration: none;'>@admin_petshop</a></p>
            </div>
            <div style='margin-top: 25px; margin-bottom: 10px; display: flex; justify-content: center;'>
                <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d4651.764567891729!2d105.78484157601898!3d20.98091798941867!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135accdd8a1ad71%3A0xa2f9b16036648187!2zSOG7jWMgdmnhu4duIEPDtG5nIG5naOG7hyBCxrB1IGNow61uaCB2aeG7hW4gdGjDtG5n!5e1!3m2!1svi!2s!4v1776620742146!5m2!1svi!2s" width="100%" height="300" style="border:0; max-width: 600px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
            </div>
            <div style='margin-top: 30px; font-size: 14px; color: #aaa;'>
                © 2026 Pet Shop. All rights reserved.
            </div>
        </div>
    """, unsafe_allow_html=True)

finally:
    db.close()
