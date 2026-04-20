import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review
import pandas as pd
import cloudinary
import cloudinary.uploader

st.title("⚙️ Bảng Điều Khiển Admin")

# Bảo vệ cơ bản
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    with st.form("admin_login"):
        username = st.text_input("Tên đăng nhập")
        pwd = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("Đăng nhập"):
            if username == "admin" and pwd == "admin":  # gán cứng đơn giản cho bản demo
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Tên đăng nhập hoặc mật khẩu không đúng")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Sản phẩm", "Đơn hàng", "Đánh giá"])

db = SessionLocal()
try:
    with tab1:
        st.subheader("Quản lý sản phẩm")
        with st.expander("Thêm sản phẩm mới"):
            with st.form("add_product"):
                p_name = st.text_input("Tên sản phẩm")
                p_price = st.number_input("Giá", min_value=0.0)
                p_stock = st.number_input("Tồn kho", min_value=0)
                p_desc = st.text_area("Mô tả")
                p_image = st.text_input("URL hình ảnh (Tùy chọn)", placeholder="https://example.com/image.jpg")
                p_image_file = st.file_uploader("Hoặc tải ảnh lên Cloudinary", type=["png", "jpg", "jpeg", "webp"])
                p_sale = st.checkbox("Giảm giá hôm nay?")
                p_disc = st.number_input("Phần trăm giảm %", min_value=0.0, max_value=100.0)
                if st.form_submit_button("Thêm sản phẩm"):
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
                    st.success("Đã thêm sản phẩm thành công!")
                    st.rerun()
                    
        prods = db.query(Product).all()
        if prods:
            df = pd.DataFrame([{
                'ID': p.id, 'Tên sản phẩm': p.name, 'Mô tả': p.description if p.description else '', 'Giá': p.price, 'Tồn kho': p.stock if p.stock is not None else 0, 
                'URL hình ảnh': p.image_url if p.image_url else '',
                'Đang giảm giá': p.is_today_sale, 'Phần trăm giảm %': p.discount_percent if p.discount_percent is not None else 0.0
            } for p in prods])
            
            edited_df = st.data_editor(df, width="stretch", disabled=["ID"], key="product_editor")
            
            if st.button("Lưu thay đổi", type="primary"):
                for index, row in edited_df.iterrows():
                    p_id = row['ID']
                    p = db.query(Product).filter_by(id=p_id).first()
                    if p:
                        p.name = row['Tên sản phẩm']
                        p.description = row.get('Mô tả', '')
                        p.price = float(row['Giá'])
                        p.stock = int(row['Tồn kho'])
                        p.image_url = row['URL hình ảnh'] if row['URL hình ảnh'] else None
                        p.is_today_sale = bool(row['Đang giảm giá'])
                        p.discount_percent = float(row['Phần trăm giảm %'])
                db.commit()
                st.success("Cập nhật sản phẩm thành công!")
                st.rerun()
                
            with st.expander("Xóa sản phẩm"):
                with st.form("delete_product_form"):
                    prod_id_to_delete = st.number_input("ID sản phẩm cần xóa", min_value=0, step=1)
                    if st.form_submit_button("Xóa", type="primary"):
                        prod_to_del = db.query(Product).filter_by(id=prod_id_to_delete).first()
                        if prod_to_del:
                            db.delete(prod_to_del)
                            db.commit()
                            st.success(f"Đã xóa thành công sản phẩm #{prod_id_to_delete}!")
                            st.rerun()
                        else:
                            st.error("Không tìm thấy sản phẩm.")
                            
    with tab2:
        st.subheader("Xem đơn hàng")
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        if orders:
            odf = pd.DataFrame([{
                'ID': o.id, 'Trạng thái': o.status, 'Khách hàng': o.guest_name or "N/A", 'Tổng tiền': o.total_price, 'Ngày đặt': o.created_at.strftime('%Y-%m-%d %H:%M') if o.created_at else "", 'Lý do trả hàng': o.return_reason or ""
            } for o in orders])
            
            edited_odf = st.data_editor(
                odf, 
                width="stretch", 
                disabled=["ID", "Khách hàng", "Tổng tiền", "Ngày đặt", "Lý do trả hàng"],
                column_config={
                    "Trạng thái": st.column_config.SelectboxColumn(
                        "Trạng thái",
                        help="Thay đổi trạng thái đơn hàng",
                        options=["pending", "shipped", "delivered", "return_requested", "returned", "return_rejected"],
                        required=True
                    )
                },
                key="order_editor"
            )
            
            if st.button("Lưu thay đổi trạng thái", type="primary"):
                for index, row in edited_odf.iterrows():
                    o_id = row['ID']
                    o_status = row['Trạng thái']
                    o = db.query(Order).filter_by(id=o_id).first()
                    if o and o.status != o_status:
                        o.status = o_status
                db.commit()
                st.success("Cập nhật trạng thái đơn hàng thành công!")
                st.rerun()
        else:
            st.info("Chưa có đơn hàng nào.")
            
    with tab3:
        st.subheader("Quản lý đánh giá")
        reviews = db.query(Review).order_by(Review.created_at.desc()).all()
        if reviews:
            rev_df = pd.DataFrame([{
                'ID': r.id, 'Người đánh giá': r.reviewer_name, 'Số sao': r.rating, 
                'Loại': f"Sản phẩm #{r.product_id}" if r.product_id else "Cửa hàng",
                'Bình luận': r.comment, 'Ngày tạo': r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""
            } for r in reviews])
            st.dataframe(rev_df, width="stretch")
            
            with st.expander("Xóa đánh giá"):
                with st.form("delete_review_form"):
                    rev_id_to_delete = st.number_input("ID đánh giá cần xóa", min_value=1, step=1)
                    if st.form_submit_button("Xóa", type="primary"):
                        rev_to_del = db.query(Review).filter_by(id=rev_id_to_delete).first()
                        if rev_to_del:
                            db.delete(rev_to_del)
                            db.commit()
                            st.success(f"Đã xóa thành công đánh giá #{rev_id_to_delete}!")
                            st.rerun()
                        else:
                            st.error("Không tìm thấy đánh giá.")
        else:
            st.info("Chưa có đánh giá nào.")
finally:
    db.close()
