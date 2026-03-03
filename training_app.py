import streamlit as st
import os
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH TRANG & BỘ NHỚ (SESSION STATE)
# ==========================================
st.set_page_config(page_title="Riken Viet - Đào tạo nội bộ", page_icon="🎓", layout="wide")

if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = False

# ==========================================
# 2. KHU VỰC HEADER TỔNG
# ==========================================
col_logo, col_title = st.columns([1, 5]) 

with col_logo:
    if os.path.exists("rkv_logo.png"):
        st.image("rkv_logo.png", use_container_width=True)
    else:
        st.warning("⚠️ Thiếu file rkv_logo.png")

with col_title:
    st.title("🎓 Cổng Đào Tạo Năng Lực & Hội Nhập")
    st.markdown("**Xin chào thành viên mới!** Vui lòng tìm hiểu về lịch sử công ty, theo dõi video và hoàn thành bài kiểm tra để hoàn tất thủ tục hội nhập.")

st.markdown("---")

# ==========================================
# 3. KHU VỰC BẢN ĐỒ LỊCH SỬ TƯƠNG TÁC
# ==========================================
st.subheader("🗺️ Hành trình vươn xa của Riken Việt (2014 - Nay)")

# Tọa độ [Vĩ độ (Lat), Kinh độ (Lon)]
cities = ["TP. Hồ Chí Minh", "Hải Phòng"]
lats = [10.762622, 20.844912]
lons = [106.660172, 106.688084]
texts = [
    "<b>Trụ sở chính TP.HCM</b><br>Thành lập: 16/10/2014",
    "<b>Chi nhánh Miền Bắc (Hải Phòng)</b><br>Thành lập: 28/03/2017"
]

fig = go.Figure()

# Thêm các điểm sáng (Markers)
fig.add_trace(go.Scattergeo(
    lon = lons,
    lat = lats,
    text = texts,
    hoverinfo = 'text',
    mode = 'markers+text',
    textposition = "top right",
    textfont=dict(color="white", size=12),
    marker = dict(
        size = 15,
        color = 'red', # Điểm sáng màu đỏ Riken
        line = dict(width = 2, color = 'white')
    )
))

# Cấu hình giao diện bản đồ công nghệ
fig.update_layout(
    geo = dict(
        scope = 'asia',
        resolution = 50,
        showland = True,
        landcolor = "rgb(30, 30, 30)", 
        countrycolor = "rgb(100, 100, 100)",
        coastlinecolor = "rgb(0, 255, 255)", 
        center = dict(lon=106.0, lat=16.0), # Căn giữa Việt Nam
        projection_scale = 5.5 # Mức độ Zoom
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=10, b=10),
    height=450
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 4. KHU VỰC VIDEO & BÀI QUIZ (CHIA CỘT 16:9)
# ==========================================
col_video, col_quiz = st.columns([1.5, 1.0], gap="large")

with col_video:
    st.subheader("📺 Phim Giới thiệu & Đào tạo Năng lực")
    # Thay đường link video YouTube thực tế của công ty bạn vào đây
    VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    st.video(VIDEO_URL)

with col_quiz:
    st.subheader("📝 Bài Kiểm Tra Kiến Thức")
    st.info("Vui lòng trả lời đúng 100% các câu hỏi để hoàn thành.")

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

        # Nút nộp bài trải rộng
        submit_btn = st.form_submit_button("📤 Nộp bài kiểm tra", type="primary", use_container_width=True)

# ==========================================
# 5. XỬ LÝ KẾT QUẢ & CẤP CHỨNG NHẬN
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

# Bảng hoàn thành khóa học xuất hiện khi Pass
if st.session_state.quiz_passed:
    st.balloons() 
    st.markdown("---")
    
    col_cert1, col_cert2 = st.columns([2, 1])
    with col_cert1:
        st.subheader("🎓 Hoàn thành Khóa học")
        st.success("Hệ thống đã ghi nhận bạn hoàn thành khóa Onboarding hội nhập!")
    with col_cert2:
        st.markdown("<br>", unsafe_allow_html=True) 
        st.download_button(
            label="📥 Tải Sổ tay nhân viên (PDF)",
            data="Nội dung file PDF giả lập...", # Có thể dùng `open('file.pdf', 'rb').read()` sau này
            file_name="SoTay_NhanVien_RikenViet.pdf",
            type="primary",
            use_container_width=True
        )
