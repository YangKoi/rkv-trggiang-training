import streamlit as st
import os

# ==========================================
# CẤU HÌNH TRANG & BỘ NHỚ (SESSION STATE)
# ==========================================
st.set_page_config(page_title="Riken Viet - Đào tạo nội bộ", page_icon="🎓", layout="centered")

# Khởi tạo biến lưu trạng thái hoàn thành bài thi
if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = False

# ==========================================
# KHU VỰC 1: HEADER & VIDEO
# ==========================================
# Hiển thị Logo từ file rkv_logo.png có sẵn trên GitHub
if os.path.exists("rkv_logo.png"):
    st.image("rkv_logo.png", width=200)
else:
    st.warning("⚠️ Không tìm thấy file 'rkv_logo.png' trong thư mục. Vui lòng kiểm tra lại tên file trên GitHub.")

st.title("🎓 Cổng Đào Tạo Năng Lực & Hội Nhập")
st.markdown("---")

st.markdown("""
**Xin chào thành viên mới!** 👋

Để bắt đầu hành trình của mình, bạn vui lòng dành ít phút theo dõi video giới thiệu về lịch sử, năng lực lõi và các giải pháp an toàn khí mà công ty chúng ta đang cung cấp.
""")

# Chiếu Video (Thay link YouTube nội bộ của bạn vào đây)
VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
st.video(VIDEO_URL)

st.markdown("---")

# ==========================================
# KHU VỰC 2: BÀI QUIZ TRẮC NGHIỆM
# ==========================================
st.subheader("📝 Bài Kiểm Tra Kiến Thức")
st.info("Vui lòng trả lời đúng 100% các câu hỏi dưới đây để hoàn thành khóa đào tạo.")

# Dùng Form để gộp các câu hỏi
with st.form("quiz_form"):
    q1 = st.radio(
        "Câu 1: Giải pháp cốt lõi mà công ty chúng ta cung cấp cho các nhà máy công nghiệp là gì?",
        options=["A. Thiết bị phòng cháy chữa cháy nói chung", 
                 "B. Hệ thống camera giám sát an ninh", 
                 "C. Các thiết bị và hệ thống đo, cảnh báo rò rỉ khí", 
                 "D. Thiết bị y tế cá nhân"],
        index=None 
    )
    
    q2 = st.radio(
        "Câu 2: Tủ điều khiển trung tâm trong hệ thống đo khí có chức năng chính là gì?",
        options=["A. Đo nhiệt độ và độ ẩm của phòng", 
                 "B. Thu thập tín hiệu từ đầu dò, hiển thị nồng độ và kích hoạt rơ-le cảnh báo", 
                 "C. Đóng ngắt nguồn điện toàn nhà máy tự động", 
                 "D. Bơm hóa chất vào bồn chứa"],
        index=None
    )
    
    q3 = st.radio(
        "Câu 3: Nguyên tắc xử lý liên động (Interlock) cơ bản khi hệ thống phát hiện rò rỉ khí chạm mức Alarm 2 là gì?",
        options=["A. Phát nhạc nền thông báo", 
                 "B. Chỉ nháy đèn vàng cảnh báo", 
                 "C. Tự động đóng van ngắt cấp khí và bật quạt xả hút", 
                 "D. Mở tung tất cả các cửa ra vào"],
        index=None
    )

    # Nút nộp bài
    submit_btn = st.form_submit_button("📤 Nộp bài kiểm tra", type="primary")

# ==========================================
# KHU VỰC 3: XỬ LÝ KẾT QUẢ & CẤP CHỨNG NHẬN
# ==========================================
if submit_btn:
    # Kiểm tra đáp án
    score = 0
    if q1 == "C. Các thiết bị và hệ thống đo, cảnh báo rò rỉ khí": score += 1
    if q2 == "B. Thu thập tín hiệu từ đầu dò, hiển thị nồng độ và kích hoạt rơ-le cảnh báo": score += 1
    if q3 == "C. Tự động đóng van ngắt cấp khí và bật quạt xả hút": score += 1
    
    if score == 3:
        st.session_state.quiz_passed = True
        st.success("🎉 Xuất sắc! Bạn đã trả lời đúng 3/3 câu hỏi.")
    else:
        st.session_state.quiz_passed = False
        st.error(f"⚠️ Bạn mới trả lời đúng {score}/3 câu hỏi. Vui lòng xem lại video và chọn lại đáp án nhé!")

# Chỉ hiển thị phần tải tài liệu NẾU đã qua bài Quiz
if st.session_state.quiz_passed:
    st.balloons() 
    st.markdown("---")
    st.subheader("🎓 Hoàn thành Khóa học")
    st.success("Hệ thống đã ghi nhận bạn hoàn thành khóa Onboarding hội nhập!")
    
    # Nút tải tài liệu sau khi pass
    st.download_button(
        label="📥 Tải Sổ tay nhân viên (PDF)",
        data="Nội dung file giả lập", 
        file_name="SoTay_NhanVien.pdf",
        type="primary"
    )
