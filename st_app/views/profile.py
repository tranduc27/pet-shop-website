import streamlit as st
import pandas as pd
from app.database import SessionLocal
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
import cloudinary
import cloudinary.uploader

st.title("👤 Thông tin tài khoản")

if "user_id" not in st.session_state:
    st.warning("Vui lòng đăng nhập")
    if st.button("Tới trang đăng nhập"):
        st.switch_page("views/login.py")
    st.stop()

db = SessionLocal()
try:
    user = db.query(User).filter(User.id == st.session_state.user_id).first()
    if not user:
        st.error("Không tìm thấy người dùng.")
        st.stop()

    # Tạo các cột bố cục
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Thông tin cơ bản")
        st.markdown(f"**Tên đăng nhập:** {user.username}")
        st.markdown(f"**Email:** {user.email or 'Chưa cung cấp'}")
        st.markdown(f"**Số điện thoại:** {user.phone or 'Chưa cung cấp'}")
        
    with col2:
        st.header("🛒 Lịch sử mua hàng")

        orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
        
        if not orders:
            st.info("Bạn chưa đặt hàng.")
        else:
            for order in orders:
                # Bản đồ trạng thái
                status_map = {
                    "pending": "Chờ xử lý", "Pending": "Chờ xử lý",
                    "shipped": "Đang giao", "delivered": "Đã giao",
                    "return_requested": "Yêu cầu trả hàng",
                    "returned": "Đã trả hàng",
                    "return_rejected": "Từ chối trả hàng"
                }
                
                # Định dạng tiêu đề đơn hàng
                dt_str = order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else "Ngày không xác định"
                status_vn = status_map.get(order.status, order.status)
                title = f"Đơn hàng #{order.id} - {dt_str} | Tổng cộng: {order.total_price:,.0f} VNĐ | Trạng thái: {status_vn}"
                
                with st.expander(title, expanded=True if order.id == orders[0].id else False): # Tự động mở đơn đầu tiên
                    # Tiến trình đơn hàng
                    steps = ["pending", "shipped", "delivered"]
                    if order.status.lower() in steps:
                        curr_idx = steps.index(order.status.lower())
                        st.progress((curr_idx + 1) / len(steps))
                        
                        cols = st.columns(3)
                        with cols[0]:
                            st.markdown("**✅ Chờ xử lý**" if curr_idx >= 0 else "⬜ Chờ xử lý")
                        with cols[1]:
                            st.markdown(f"**<div style='text-align: center'>{'✅ Đang giao' if curr_idx >= 1 else '⬜ Đang giao'}</div>**", unsafe_allow_html=True)
                        with cols[2]:
                            st.markdown(f"**<div style='text-align: right'>{'✅ Đã giao' if curr_idx >= 2 else '⬜ Đã giao'}</div>**", unsafe_allow_html=True)
                    elif order.status.lower() == "return_requested":
                        st.warning("🔄 Đang xử lý yêu cầu trả hàng")
                    elif order.status.lower() == "returned":
                        st.error("🔙 Đã hoàn trả hàng thủ tục xong")
                    elif order.status.lower() == "return_rejected":
                        st.error("❌ Yêu cầu trả hàng bị từ chối")
                        
                    st.divider()
                
                    st.write(f"**Tên:** {order.guest_name or user.username}")
                    st.write(f"**Số điện thoại:** {order.guest_phone or user.phone or 'Chưa cung cấp'}")
                    st.write(f"**Địa chỉ giao hàng (Kèm ghi chú/thanh toán):** {order.guest_address or 'Chưa cung cấp'}")
                    
                    # Lấy danh sách sản phẩm
                    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
                    if items:
                        item_data = []
                        for item in items:
                            product = db.query(Product).filter(Product.id == item.product_id).first()
                            product_name = product.name if product else "Sản phẩm không xác định"
                            item_data.append({
                                "Sản phẩm": product_name,
                                "Số lượng": item.quantity,
                                "Đơn giá": f"{item.price:,.0f} VNĐ"
                            })
                        st.table(pd.DataFrame(item_data))
                    else:
                        st.write("Không có sản phẩm trong đơn đặt hàng")
                        
                    st.divider()
                    if order.status.lower() == "delivered":
                        with st.form(f"return_form_{order.id}"):
                            st.write("Cảm thấy không hài lòng hoặc hàng bị lỗi?")
                            return_reason = st.text_area("Lý do trả hàng", key=f"reason_{order.id}")
                            return_image_file = st.file_uploader("Đính kèm hình ảnh hàng (Bắt buộc)", type=["png", "jpg", "jpeg", "webp"], key=f"image_{order.id}")
                            
                            submit_return = st.form_submit_button("Gửi yêu cầu trả hàng")
                            if submit_return:
                                if return_reason.strip() == "":
                                    st.error("Vui lòng nhập lý do trả hàng.")
                                elif return_image_file is None:
                                    st.error("Vui lòng đính kèm hình ảnh sản phẩm cần trả.")
                                else:
                                    order_to_update = db.query(Order).filter(Order.id == order.id).first()
                                    if order_to_update:
                                        final_image_url = None
                                        try:
                                            # Cấu hình Cloudinary nếu có trong secrets
                                            if "cloudinary" in st.secrets:
                                                cloudinary.config(
                                                    cloud_name = st.secrets["cloudinary"]["cloud_name"],
                                                    api_key = st.secrets["cloudinary"]["api_key"],
                                                    api_secret = st.secrets["cloudinary"]["api_secret"]
                                                )
                                            # Tải ảnh lên Cloudinary
                                            response = cloudinary.uploader.upload(return_image_file)
                                            final_image_url = response['secure_url']
                                            
                                            order_to_update.status = "return_requested"
                                            order_to_update.return_reason = return_reason
                                            order_to_update.return_image_url = final_image_url
                                            db.commit()
                                            st.success("Yêu cầu trả hàng đã được gửi thành công! Cửa hàng sẽ sớm liên hệ thay thế/hoàn tiền.")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Lỗi khi tải hình ảnh lên: {e}")
                    elif order.status == "return_requested":
                        st.info(f"Đang chờ xử lý yêu cầu trả hàng. Lý do: {order.return_reason}")
                        if order.return_image_url:
                            st.image(order.return_image_url, caption="Hình ảnh đính kèm", width=300)
                    elif order.status == "returned":
                        st.success(f"Yêu cầu trả hàng của bạn đã được hoàn tất. Cảm ơn phản hồi của bạn.")
                    elif order.status == "return_rejected":
                        st.error(f"Yêu cầu trả hàng của bạn bị từ chối. Vui lòng liên hệ hỗ trợ.")
finally:
    db.close()
