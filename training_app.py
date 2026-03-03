import streamlit as st
import os
import plotly.graph_objects as go
from datetime import datetime

# Thử import PyGithub, nếu chưa cài thì bỏ qua để web không bị sập
try:
    from github import Github
except ImportError:
    Github = None

# ==========================================
# 1. CẤU HÌNH TRANG & BỘ NHỚ
# ==========================================
st.set_page_config(page_title="Riken Viet - Đào tạo nội bộ", page_icon="🎓", layout="wide")

if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = False

# ==========================================
# HÀM LƯU KẾT QUẢ LÊN GITHUB
# ==========================================
def save_to_github(name, score):
    if Github is None:
        return False, "Chưa cài đặt thư viện PyGithub."
    
    try:
        # Lấy thông tin bảo mật từ Streamlit Secrets (Sẽ thiết lập ở Bước 3)
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["GITHUB_REPO"] # Ví dụ: "trggiang/rikenviet-training"
        
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # Định dạng tên file và nội dung
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = name.replace(" ", "_")
        file_path = f"KetQua_DaoTao/{safe_name}_{now}.txt" # Lưu vào thư mục KetQua_DaoTao
        
        content = f"--- KẾT QUẢ ĐÀO TẠO HỘI NHẬP RIKEN VIỆT ---\n"
        content += f"Họ và Tên: {name}\n"
        content += f"Thời gian hoàn thành: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        content += f"Điểm số đạt được: {score}/3\n"
        content += f"Trạng thái: {'ĐẠT' if score == 3 else 'CHƯA ĐẠT'}\n"
        
        # Lệnh đẩy file lên GitHub
        repo.create_file(file_path, f"Lưu bài thi của {name}", content, branch="main")
        return True, "Thành công"
    except Exception as e:
        return False, str(e)

# ==========================================
# CỬA SỔ POPUP BÀI KIỂM TRA (DIALOG)
# ==========================================
@st.dialog("📝 BÀI KIỂM TRA NĂNG LỰC & HỘI NHẬP", width="large")
def take_quiz_dialog():
    st.markdown("Vui lòng điền họ tên và hoàn thành các câu hỏi dưới đây. Bài thi sẽ được tự động lưu vào hệ thống nhân sự.")
    
    # Nhập tên
    user_name = st.text_input("👤 Nhập Họ và Tên của bạn (*Bắt buộc):", placeholder="VD: Nguyễn Văn A")
    st.markdown("---")
    
    # Câu hỏi
    q1 = st.radio("Câu 1: Giải pháp cốt lõi mà công ty chúng ta cung cấp là gì?",
                  ["A. Thiết bị PCCC", "B. Hệ thống camera an ninh", "C. Thiết bị đo, cảnh báo rò rỉ khí", "D. Thiết bị y tế"], index=None)
    
    q2 = st.radio("Câu 2: Tủ điều khiển trung tâm trong hệ thống đo khí có chức năng chính là gì?",
                  ["A. Đo nhiệt độ phòng", "B. Thu thập tín hiệu, hiển thị nồng độ và kích hoạt rơ-le", "C. Đóng ngắt điện", "D. Bơm hóa chất"], index=None)
    
    q3 = st.radio("Câu 3: Nguyên tắc xử lý liên động (Interlock) cơ bản khi Alarm 2 kích hoạt?",
                  ["A. Phát nhạc nền", "B. Chỉ nháy đèn vàng", "C. Đóng van ngắt cấp khí và bật quạt hút", "D. Mở tung cửa"], index=None)

    # Nút Gửi bài
    if st.button("📤 NỘP BÀI VÀ LƯU KẾT QUẢ", type="primary", use_container_width=True):
        if not user_name:
            st.error("⚠️ Vui lòng nhập Họ và Tên trước khi nộp bài!")
        elif not q1 or not q2 or not q3:
            st.error("⚠️ Vui lòng trả lời đầy đủ cả 3 câu hỏi!")
        else:
            with st.spinner("Đang tự động chấm điểm và lưu hồ sơ lên hệ thống GitHub..."):
                score = 0
                if q1.startswith("C"): score += 1
                if q2.startswith("B"): score += 1
                if q3.startswith("C"): score += 1
                
                # Gọi hàm lưu lên GitHub
                success, msg = save_to_github(user_name, score)
                
                if success:
                    st.success(f"✅ Đã lưu kết quả của **{user_name}** thành công vào cơ sở dữ liệu!")
                    if score == 3:
                        st.session_state.quiz_passed = True
                        st.success("🎉 CHÚC MỪNG! Bạn đã đạt điểm tuyệt đối 3/3.")
                    else:
                        st.session_state.quiz_passed = False
                        st.error(f"⚠️ Bạn đạt {score}/3 điểm. Vui lòng tắt cửa sổ, xem lại video và làm lại nhé!")
                else:
                    st.warning(f"⚠️ Chấm điểm hoàn tất ({score}/3) nhưng chưa thể lưu file lên GitHub (Lỗi: {msg}). Vui lòng kiểm tra lại cấu hình Secret Key.")

# ==========================================
# GIAO DIỆN CHÍNH (TRANG CHỦ)
# ==========================================
col_logo, col_title = st.columns([1, 5]) 
with col_logo:
    if os.path.exists("rkv_logo.png"): st.image("rkv_logo.png", use_container_width=True)
with col_title:
    st.title("🎓 Cổng Đào Tạo Năng Lực & Hội Nhập")

st.markdown("---")

# 1. Bản đồ (Giữ nguyên như bản cũ)
st.subheader("🗺️ Hành trình vươn xa của Riken Việt (2014 - Nay)")
fig = go.Figure()
fig.add_trace(go.Scattergeo(lon=[106.660172, 106.688084], lat=[10.762622, 20.844912], text=["<b>Trụ sở HCM</b>", "<b>CN Hải Phòng</b>"], mode='markers+text', textposition="top right", textfont=dict(color="white", size=13), marker=dict(size=14, color='red', line=dict(width=2, color='white'))))
fig.add_trace(go.Scattergeo(lon=[105.8542], lat=[21.0285], text=["<b>Hà Nội</b>"], mode='markers+text', textposition="top left", textfont=dict(color="yellow", size=14), marker=dict(size=20, color='red', symbol='star', line=dict(width=1.5, color='yellow'))))
fig.add_trace(go.Scattergeo(lon=[112.0, 114.2], lat=[16.5, 9.0], text=["<b>Hoàng Sa (VN)</b>", "<b>Trường Sa (VN)</b>"], mode='markers+text', textposition="bottom center", textfont=dict(color="#00FFFF", size=12), marker=dict(size=6, color='#00FFFF')))
fig.update_layout(geo=dict(resolution=50, showland=True, landcolor="rgb(30,30,30)", coastlinecolor="cyan", lataxis=dict(range=[6, 24]), lonaxis=dict(range=[101, 118])), paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=10), height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 2. Chiếu Video ở giữa trang
st.subheader("📺 Phim Giới thiệu & Đào tạo Năng lực")
st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") 

st.markdown("<br><br>", unsafe_allow_html=True)

# 3. Nút mở Popup làm bài kiểm tra (Ẩn dưới cùng)
st.markdown("<h3 style='text-align: center;'>Đánh giá mức độ hội nhập</h3>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🚀 BẮT ĐẦU LÀM BÀI KIỂM TRA", type="primary", use_container_width=True):
        take_quiz_dialog() # Gọi hàm mở cửa sổ Dialog

# 4. Hiển thị phần hoàn thành sau khi Pass
if st.session_state.quiz_passed:
    st.balloons() 
    st.markdown("---")
    col_cert1, col_cert2 = st.columns([2, 1])
    with col_cert1:
        st.success("🎉 Hệ thống đã xác nhận bạn hoàn thành khóa Onboarding!")
    with col_cert2:
        st.download_button("📥 Tải Sổ tay nhân viên (PDF)", data="Nội dung PDF...", file_name="SoTay_RikenViet.pdf", type="primary", use_container_width=True)
