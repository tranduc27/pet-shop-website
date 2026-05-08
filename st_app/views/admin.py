import streamlit as st
from app.database import SessionLocal
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review
from app.models.user import User
from sqlalchemy import func
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

db = SessionLocal()
try:
    # Tổng quan Dashboard
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.sum(Order.total_price)).filter(Order.status != 'returned').scalar() or 0
    total_users = db.query(User).count()
    
    st.subheader("📊 Tổng quan")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sản phẩm", total_products)
    col2.metric("Đơn hàng", total_orders)
    col3.metric("Doanh thu", f"{total_revenue:,.0f} đ")
    col4.metric("Người dùng", total_users)
    st.divider()

    st.subheader("📈 Thống kê doanh thu")
    stat_orders = db.query(Order).filter(Order.status != 'returned').all()
    if stat_orders:
        df_stat = pd.DataFrame([{
            'total_price': o.total_price,
            'created_at': o.created_at
        } for o in stat_orders])
        
        df_stat['created_at'] = pd.to_datetime(df_stat['created_at'])
        df_stat['Tuần'] = df_stat['created_at'].dt.to_period('W').apply(lambda r: r.start_time.strftime('%Y-%m-%d'))
        df_stat['Tháng'] = df_stat['created_at'].dt.to_period('M').apply(lambda r: r.strftime('%Y-%m'))
        df_stat['Năm'] = df_stat['created_at'].dt.to_period('Y').apply(lambda r: r.strftime('%Y'))
        
        time_period = st.radio("Chọn mốc thời gian:", ["Theo Tuần", "Theo Tháng", "Theo Năm"], horizontal=True)
        
        if time_period == "Theo Tuần":
            group_col = 'Tuần'
        elif time_period == "Theo Tháng":
            group_col = 'Tháng'
        else:
            group_col = 'Năm'
            
        revenue_df = df_stat.groupby(group_col)['total_price'].sum().reset_index()
        revenue_df.rename(columns={'total_price': 'Doanh thu'}, inplace=True)
        
        st.bar_chart(revenue_df.set_index(group_col))
    else:
        st.info("Chưa có dữ liệu doanh thu.")
        
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Sản phẩm", "Đơn hàng", "Đánh giá", "Tài khoản"])
    @st.dialog("Thêm sản phẩm mới", width="large")
    def add_product_dialog():
        with st.form("add_product"):
            p_name = st.text_input("Tên sản phẩm")
            p_price = st.number_input("Giá", min_value=0.0)
            p_stock = st.number_input("Tồn kho", min_value=0)
            p_desc = st.text_area("Mô tả")
            p_image = st.text_input("URL hình ảnh (Tùy chọn)", placeholder="https://example.com/image.jpg")
            p_image_file = st.file_uploader("Hoặc tải ảnh lên Cloudinary", type=["png", "jpg", "jpeg", "webp"])
            p_pet_type = st.selectbox("Loại thú cưng", ["Chung", "Chó", "Mèo"])
            p_sale = st.checkbox("Giảm giá hôm nay?")
            p_disc = st.number_input("Phần trăm giảm %", min_value=0.0, max_value=100.0)
            if st.form_submit_button("Thêm sản phẩm", type="primary"):
                final_image_url = p_image
                if p_image_file is not None:
                    try:
                        if "cloudinary" in st.secrets:
                            cloudinary.config(
                              cloud_name = st.secrets["cloudinary"]["cloud_name"],
                              api_key = st.secrets["cloudinary"]["api_key"],
                              api_secret = st.secrets["cloudinary"]["api_secret"]
                            )
                            # Upload directly from bytes
                            response = cloudinary.uploader.upload(p_image_file.read())
                            final_image_url = response['secure_url']
                        else:
                            st.error("Chưa cấu hình Cloudinary trong secrets!")
                            st.stop()
                    except Exception as e:
                        st.error(f"Lỗi tải ảnh lên Cloudinary: {e}")
                        st.stop()
                
                new_p = Product(name=p_name, price=p_price, stock=p_stock, description=p_desc, image_url=final_image_url, pet_type=p_pet_type, is_today_sale=p_sale, discount_percent=p_disc)
                db.add(new_p)
                db.commit()
                st.success("Đã thêm sản phẩm thành công!")
                st.rerun()

    @st.dialog("Xóa sản phẩm")
    def delete_product_dialog():
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

    with tab1:
        st.subheader("Quản lý sản phẩm")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Thêm sản phẩm mới", use_container_width=True):
                add_product_dialog()
        with c2:
            if st.button("🗑️ Xóa sản phẩm", use_container_width=True):
                delete_product_dialog()
                
        st.divider()

        prods = db.query(Product).all()
        if prods:
            df = pd.DataFrame([{
                'ID': p.id, 'Tên sản phẩm': p.name, 'Loại thú cưng': p.pet_type or "Chung", 'Mô tả': p.description if p.description else '', 'Giá': p.price, 'Tồn kho': p.stock if p.stock is not None else 0, 
                'URL hình ảnh': p.image_url if p.image_url else '',
                'Đang giảm giá': p.is_today_sale, 'Phần trăm giảm %': p.discount_percent if p.discount_percent is not None else 0.0
            } for p in prods])
            
            edited_df = st.data_editor(
                df, 
                width="stretch", 
                disabled=["ID"], 
                key="product_editor",
                column_config={
                    "URL hình ảnh": st.column_config.TextColumn(
                        "URL hình ảnh (Cloudinary)", help="Đường dẫn hình ảnh sản phẩm"
                    ),
                    "Giá": st.column_config.NumberColumn(
                        "Giá (VNĐ)",
                        help="Giá bán sản phẩm",
                        min_value=0,
                        step=1000,
                        format="%d đ"
                    ),
                    "Phần trăm giảm %": st.column_config.NumberColumn(
                        "Giảm giá (%)",
                        min_value=0,
                        max_value=100,
                        format="%d %%"
                    ),
                    "Loại thú cưng": st.column_config.SelectboxColumn(
                        "Dành cho",
                        help="Dành cho thú cưng nào",
                        options=["Chung", "Chó", "Mèo"],
                        required=True
                    ),
                    "Đang giảm giá": st.column_config.CheckboxColumn(
                        "Đang Sale?",
                        default=False,
                    )
                }
            )
            
            if st.button("Lưu thay đổi", type="primary"):
                for index, row in edited_df.iterrows():
                    p_id = row['ID']
                    p = db.query(Product).filter_by(id=p_id).first()
                    if p:
                        p.name = row['Tên sản phẩm']
                        p.pet_type = row['Loại thú cưng']
                        p.description = row.get('Mô tả', '')
                        p.price = float(row['Giá'])
                        p.stock = int(row['Tồn kho'])
                        p.image_url = row['URL hình ảnh'] if row['URL hình ảnh'] else None
                        p.is_today_sale = bool(row['Đang giảm giá'])
                        p.discount_percent = float(row['Phần trăm giảm %'])
                db.commit()
                st.success("Cập nhật sản phẩm thành công!")
                st.rerun()
    with tab2:
        st.subheader("Xem đơn hàng")
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        if orders:
            odf = pd.DataFrame([{
                'ID': o.id, 
                'Trạng thái': o.status, 
                'Khách hàng': o.guest_name or "N/A", 
                'SĐT': o.guest_phone or "N/A",
                'Địa chỉ': o.guest_address or "N/A",
                'Tổng tiền': o.total_price, 
                'Ngày đặt': o.created_at.strftime('%Y-%m-%d %H:%M') if o.created_at else "", 
                'Ngày giao': o.delivery_date.strftime('%Y-%m-%d') if o.delivery_date else "Chưa có",
                'Lý do trả hàng': o.return_reason or "",
                'Ảnh trả hàng': o.return_image_url or None
            } for o in orders])
            
            edited_odf = st.data_editor(
                odf, 
                width="stretch", 
                disabled=["ID", "Khách hàng", "SĐT", "Địa chỉ", "Tổng tiền", "Ngày đặt", "Ngày giao", "Lý do trả hàng", "Ảnh trả hàng"],
                column_config={
                    "Trạng thái": st.column_config.SelectboxColumn(
                        "Trạng thái",
                        help="Thay đổi trạng thái đơn hàng",
                        options=["pending", "shipped", "delivered", "return_requested", "returned", "return_rejected"],
                        required=True
                    ),
                    "Ảnh trả hàng": st.column_config.ImageColumn(
                        "Ảnh trả hàng",
                        help="Hình ảnh sản phẩm khách hàng yêu cầu trả"
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
            
    with tab4:
        st.subheader("Quản lý tài khoản")
        users = db.query(User).all()
        if users:
            u_df = pd.DataFrame([{
                'ID': u.id,
                'Tên đăng nhập': u.username,
                'Email': u.email or "",
                'Số điện thoại': u.phone or "",
                'Vai trò': u.role
            } for u in users])
            st.dataframe(u_df, width="stretch")
            
            with st.expander("Xóa tài khoản"):
                with st.form("delete_user_form"):
                    u_id_to_delete = st.number_input("ID tài khoản cần xóa", min_value=1, step=1)
                    if st.form_submit_button("Xóa", type="primary"):
                        u_to_del = db.query(User).filter_by(id=u_id_to_delete).first()
                        if u_to_del:
                            db.delete(u_to_del)
                            db.commit()
                            st.success(f"Đã xóa thành công tài khoản #{u_id_to_delete}!")
                            st.rerun()
                        else:
                            st.error("Không tìm thấy tài khoản.")
        else:
            st.info("Chưa có tài khoản nào.")
finally:
    db.close()
