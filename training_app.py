import streamlit as st
import os

# ==========================================
# CẤU HÌNH TRANG & BỘ NHỚ (SESSION STATE)
# ==========================================
# Đổi layout="centered" thành layout="wide" để tràn viền 16:9
st.set_page_config(page_title="Riken Viet - Đào tạo nội bộ", page_icon="🎓", layout="wide")

if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = False

# ==========================================
# KHU VỰC 1: HEADER (Dàn ngang)
# ==========================================
col_logo, col_title = st.columns([1, 5]) # Chia tỷ lệ phần Header

with col_logo:
    if os.path.exists("rkv_logo.png"):
        st.image("rkv_logo.png", use_container_width=True)
    else:
        st.warning("⚠️ Thiếu file rkv_logo.png")

with col_title:
    st.title("🎓 Cổng Đào Tạo Năng Lực & Hội Nhập")
    st.markdown("**Xin chào thành viên mới!** Vui lòng theo dõi video bên trái và hoàn thành bài kiểm tra ở cột bên phải để hoàn tất thủ tục hội nhập.")

st.markdown("---")

# ==========================================
# KHU VỰC 2: CHIA CỘT MÀN HÌNH 16:9
# ==========================================
# Cột trái chiếu video to (tỷ lệ 1.5), cột phải làm bài Quiz (tỷ lệ 1.0)
col_video, col_quiz = st.columns([1.5, 1.0], gap="large")

with col_video:
    st.subheader("📺 Phim Giới thiệu & Đào tạo Năng lực")
    # Streamlit sẽ tự động stretch video ra vừa khít tỷ lệ cột
    VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    st.video(VIDEO_URL)

with col_quiz:
    st.subheader("📝 Bài Kiểm Tra Kiến Thức")
    st.info("Vui lòng trả lời đúng 100% các câu hỏi để qua môn.")

    with st.form("quiz_form"):
        q1 = st.radio(
            "Câu 1: Giải pháp cốt lõi mà công ty chúng ta cung cấp là gì?",
            options=["A. Thiết bị phòng cháy chữa cháy nói chung", 
                     "B. Hệ thống camera giám sát an ninh", 
                     "C. Các thiết bị và hệ thống đo, cảnh báo rò rỉ khí", 
                     "D. Thiết bị y tế cá nhân"],
            index=None 
        )
        
        q2 = st.radio(
            "Câu 2: Tủ điều khiển trung tâm trong hệ thống đo khí có chức năng chính là gì?",
            options=["A. Đo nhiệt độ và độ ẩm của phòng", 
                     "B. Thu thập tín hiệu, hiển thị nồng độ và kích hoạt rơ-le", 
                     "C. Đóng ngắt nguồn điện toàn nhà máy tự động", 
                     "D. Bơm hóa chất vào bồn chứa"],
            index=None
        )
        
        q3 = st.radio(
            "Câu 3: Nguyên tắc xử lý liên động (Interlock) cơ bản khi Alarm 2 kích hoạt?",
            options=["A. Phát nhạc nền thông báo", 
                     "B. Chỉ nháy đèn vàng cảnh báo", 
                     "C. Tự động đóng van ngắt cấp khí và bật quạt xả hút", 
                     "D. Mở tung tất cả các cửa ra vào"],
            index=None
        )

        # Nút nộp bài trải rộng hết cỡ của cột phải
        submit_btn = st.form_submit_button("📤 Nộp bài kiểm tra", type="primary", use_container_width=True)

# ==========================================
# KHU VỰC 3: XỬ LÝ KẾT QUẢ & CẤP CHỨNG NHẬN
# ==========================================
if submit_btn:
    score = 0
    if q1 == "C. Các thiết bị và hệ thống đo, cảnh báo rò rỉ khí": score += 1
    if q2 == "B. Thu thập tín hiệu, hiển thị nồng độ và kích hoạt rơ-le": score += 1
    if q3 == "C. Tự động đóng van ngắt cấp khí và bật quạt xả hút": score += 1
    
    if score == 3:
        st.session_state.quiz_passed = True
        st.success("🎉 Xuất sắc! Bạn đã trả lời đúng 3/3 câu hỏi.")
    else:
        st.session_state.quiz_passed = False
        st.error(f"⚠️ Bạn mới trả lời đúng {score}/3 câu hỏi. Vui lòng xem lại video và chọn lại đáp án nhé!")

# Bảng hoàn thành khóa học dàn rộng ở dưới cùng
if st.session_state.quiz_passed:
    st.balloons() 
    st.markdown("---")
    
    col_cert1, col_cert2 = st.columns([2, 1])
    with col_cert1:
        st.subheader("🎓 Hoàn thành Khóa học")
        st.success("Hệ thống đã ghi nhận bạn hoàn thành khóa Onboarding hội nhập!")
    with col_cert2:
        st.markdown("<br>", unsafe_allow_html=True) # Đẩy nút bấm xuống một chút cho cân bằng
        st.download_button(
            label="📥 Tải Sổ tay nhân viên (PDF)",
            data="Nội dung file giả lập", 
            file_name="SoTay_NhanVien.pdf",
            type="primary",
            use_container_width=True
        )
