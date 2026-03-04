import streamlit as st
import os
import pandas as pd
from datetime import datetime

try:
    from github import Github
except ImportError:
    Github = None

# ==========================================
# 1. CẤU HÌNH TRANG & BỘ NHỚ (SESSION STATE)
# ==========================================
st.set_page_config(page_title="Riken Viet - Đào tạo nội bộ", page_icon="🎓", layout="wide")

if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = False

# ==========================================
# 2. CÁC HÀM GIAO TIẾP VỚI GITHUB
# ==========================================
def save_to_github(name, score, q1_ans, q2_ans, q3_ans):
    if Github is None: return False, "Chưa cài đặt thư viện PyGithub."
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["GITHUB_REPO"]
        
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = name.replace(" ", "_")
        file_path = f"KetQua_DaoTao/{safe_name}_{now}.txt" 
        
        content = f"--- KẾT QUẢ ĐÀO TẠO HỘI NHẬP RIKEN VIỆT ---\n"
        content += f"Họ và Tên: {name}\n"
        content += f"Thời gian hoàn thành: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        content += f"Điểm số đạt được: {score}/3\n"
        content += f"Trạng thái: {'ĐẠT' if score == 3 else 'CHƯA ĐẠT'}\n"
        content += f"--- CHI TIẾT BÀI LÀM ---\n"
        content += f"Câu 1 chọn: {q1_ans}\n"
        content += f"Câu 2 chọn: {q2_ans}\n"
        content += f"Câu 3 chọn: {q3_ans}\n"
        
        repo.create_file(file_path, f"Lưu bài thi của {name}", content, branch="main")
        return True, "Thành công"
    except Exception as e:
        return False, str(e)

def fetch_history_from_github():
    if Github is None: return None
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["GITHUB_REPO"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        try:
            contents = repo.get_contents("KetQua_DaoTao")
        except:
            return [] 
            
        records = []
        for file in contents:
            if file.name.endswith(".txt"):
                text = file.decoded_content.decode("utf-8")
                lines = text.split('\n')
                name, date, score, status = "", "", "", ""
                ans1, ans2, ans3 = "N/A", "N/A", "N/A" 
                
                for line in lines:
                    if line.startswith("Họ và Tên:"): name = line.split(":", 1)[1].strip()
                    if line.startswith("Thời gian hoàn thành:"): date = line.replace("Thời gian hoàn thành:", "").strip()
                    if line.startswith("Điểm số đạt được:"): score = line.split(":", 1)[1].strip()
                    if line.startswith("Trạng thái:"): status = line.split(":", 1)[1].strip()
                    if line.startswith("Câu 1 chọn:"): ans1 = line.split(":", 1)[1].strip()
                    if line.startswith("Câu 2 chọn:"): ans2 = line.split(":", 1)[1].strip()
                    if line.startswith("Câu 3 chọn:"): ans3 = line.split(":", 1)[1].strip()
                
                records.append({
                    "Họ Tên": name, "Thời gian": date, "Điểm": score, "Kết quả": status,
                    "Câu 1 (Đúng: C)": ans1[:15] + "..." if len(ans1) > 15 else ans1, 
                    "Câu 2 (Đúng: B)": ans2[:15] + "..." if len(ans2) > 15 else ans2,
                    "Câu 3 (Đúng: C)": ans3[:15] + "..." if len(ans3) > 15 else ans3
                })
        return records
    except Exception as e:
        st.error(f"Lỗi truy xuất: {e}")
        return None

# ==========================================
# 3. CỬA SỔ POPUP BÀI KIỂM TRA
# ==========================================
@st.dialog("📝 BÀI KIỂM TRA NĂNG LỰC & HỘI NHẬP", width="large")
def take_quiz_dialog():
    st.markdown("Vui lòng điền họ tên và hoàn thành các câu hỏi dưới đây.")
    user_name = st.text_input("👤 Nhập Họ và Tên của bạn (*Bắt buộc):", placeholder="VD: Nguyễn Văn A")
    st.markdown("---")
    
    q1 = st.radio("Câu 1: Giải pháp cốt lõi mà công ty chúng ta cung cấp là gì?",
                  ["A. Thiết bị PCCC", "B. Hệ thống camera an ninh", "C. Thiết bị đo, cảnh báo rò rỉ khí", "D. Thiết bị y tế"], index=None)
    q2 = st.radio("Câu 2: Tủ điều khiển trung tâm trong hệ thống đo khí có chức năng chính là gì?",
                  ["A. Đo nhiệt độ phòng", "B. Thu thập tín hiệu, hiển thị nồng độ và kích hoạt rơ-le", "C. Đóng ngắt điện", "D. Bơm hóa chất"], index=None)
    q3 = st.radio("Câu 3: Nguyên tắc xử lý liên động (Interlock) cơ bản khi Alarm 2 kích hoạt?",
                  ["A. Phát nhạc nền", "B. Chỉ nháy đèn vàng", "C. Đóng van ngắt cấp khí và bật quạt hút", "D. Mở tung cửa"], index=None)

    if st.button("📤 NỘP BÀI VÀ LƯU KẾT QUẢ", type="primary", use_container_width=True):
        if not user_name: st.error("⚠️ Vui lòng nhập Họ và Tên!")
        elif not q1 or not q2 or not q3: st.error("⚠️ Vui lòng trả lời đầy đủ 3 câu hỏi!")
        else:
            with st.spinner("Đang chấm điểm và lưu chi tiết đáp án lên máy chủ..."):
                score = 0
                if q1.startswith("C"): score += 1
                if q2.startswith("B"): score += 1
                if q3.startswith("C"): score += 1
                
                success, msg = save_to_github(user_name, score, str(q1), str(q2), str(q3))
                
                if success:
                    if score == 3:
                        st.session_state.quiz_passed = True
                        st.success("🎉 CHÚC MỪNG! Bạn đã trả lời đúng hoàn toàn. Hãy tắt bảng này để nhận chứng nhận.")
                    else:
                        st.session_state.quiz_passed = False
                        st.error(f"⚠️ Bạn đạt {score}/3 điểm. Vui lòng xem lại kiến thức và thực hiện lại bài thi!")
                else:
                    st.warning("⚠️ Lỗi kết nối máy chủ GitHub!")

# ==========================================
# 4. THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==========================================
with st.sidebar:
    if os.path.exists("rkv_logo.png"):
        st.image("rkv_logo.png", use_container_width=True)
    st.markdown("## 📑 Menu Đào Tạo")
    app_mode = st.radio("Chọn chuyên mục:", [
        "🎓 Cổng Đào Tạo Hội Nhập",
        "☣️ Kiến Thức: Phân Loại Khí"
    ])
    st.markdown("---")
    st.info("💡 **Gợi ý:** Hãy đọc kỹ phần 'Kiến thức Phân loại khí' trước khi làm bài kiểm tra hội nhập nhé!")

# ==========================================
# 5. NỘI DUNG TỪNG TRANG
# ==========================================

# ---------------- TRANG 1: ĐÀO TẠO HỘI NHẬP ----------------
if app_mode == "🎓 Cổng Đào Tạo Hội Nhập":
    col_title, col_admin = st.columns([4, 1.5]) 
    with col_title:
        st.title("🎓 Cổng Đào Tạo Năng Lực & Hội Nhập")
        st.markdown("**Xin chào thành viên mới!** Vui lòng tìm hiểu về lịch sử công ty, theo dõi video và hoàn thành bài kiểm tra để hoàn tất thủ tục hội nhập.")
    with col_admin:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.popover("🗄️ Dành cho Quản lý (Admin)", use_container_width=True):
            st.markdown("**📂 Kho lưu trữ Lịch sử Đào tạo**")
            if st.button("🔄 Tải dữ liệu mới nhất", use_container_width=True):
                with st.spinner("Đang trích xuất chi tiết bài làm..."):
                    records = fetch_history_from_github()
                    if records:
                        df = pd.DataFrame(records)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    elif records == []:
                        st.info("Trống! Chưa có nhân viên nào nộp bài.")

    st.markdown("---")
    st.subheader("📺 Phim Giới thiệu & Đào tạo Năng lực")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") 

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Đánh giá mức độ hội nhập</h3>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 BẮT ĐẦU LÀM BÀI KIỂM TRA", type="primary", use_container_width=True):
            take_quiz_dialog() 

    if st.session_state.quiz_passed:
        st.balloons() 
        st.markdown("---")
        col_cert1, col_cert2 = st.columns([2, 1])
        with col_cert1:
            st.success("🎉 Hệ thống đã xác nhận bạn hoàn thành khóa Onboarding!")
        with col_cert2:
            st.download_button("📥 Tải Sổ tay nhân viên (PDF)", data="Nội dung PDF...", file_name="SoTay_RikenViet.pdf", type="primary", use_container_width=True)

# ---------------- TRANG 2: KIẾN THỨC VỀ KHÍ ----------------
elif app_mode == "☣️ Kiến Thức: Phân Loại Khí":
    st.title("☣️ Kiến Thức Cơ Bản Về Các Loại Khí Nguy Hiểm")
    st.markdown("""
    Trong môi trường công nghiệp, rủi ro về khí là những **"Kẻ thù vô hình"**. Thiết bị của RIKEN KEIKI ra đời với sứ mệnh chính là bảo vệ sinh mạng người lao động trước 3 nhóm khí nguy hiểm cơ bản nhất:
    """)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🔥 1. Khí Cháy Nổ (Combustible/LEL)", "☠️ 2. Khí Độc (Toxic/PPM)", "💨 3. Khí Oxy (O2)"])

    with tab1:
        st.header("🔥 Khí Cháy Nổ (Combustible Gases)")
        if os.path.exists("image_combustible.png"):
            st.image("image_combustible.png", use_container_width=True, caption="Khí cháy nổ có thể phát nổ nếu hỗn hợp khí và oxy (không khí) nằm trong khoảng cháy nổ và gặp nguồn bắt cháy.")
        else: st.warning("⚠️ Thiếu file 'image_combustible.png'.")

        st.error("**Nguy cơ:** Gây ra hỏa hoạn và các vụ nổ thảm khốc phá hủy toàn bộ nhà máy.")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            * **Khoảng cháy nổ:** Được giới hạn bởi Giới hạn nổ dưới (LEL) và Giới hạn nổ trên (UEL).
            * **Quy định báo động an toàn:** Điểm báo động không được phép vượt quá **1/4 (25%) của mức LEL** để có đủ thời gian phản ứng trước khi nổ.
            * **Các loại khí phổ biến:**
                * **Methane (CH4):** Khí tự nhiên, mức LEL là 5.0 vol%.
                * **Hydrogen (H2):** Rất dễ nổ, mức LEL là 4.0 vol%.
                * **Isobutane (i-C4H10):** Khí gas công nghiệp, mức LEL chỉ 1.8 vol%.
            """)
        with col2:
            st.info("💡 **Giải pháp Riken Keiki:**\nCác dòng máy đo khí cháy nổ của chúng ta sử dụng công nghệ cảm biến xúc tác (Catalytic) hoặc quang học siêu nhạy, không bị nhiễu bởi các khí khác.")

    with tab2:
        st.header("☠️ Khí Độc (Toxic Gases)")
        if os.path.exists("image_toxic.png"):
            st.image("image_toxic.png", use_container_width=True, caption="Khí độc gây hại trực tiếp qua đường hô hấp. Nhiều loại khí không màu, không mùi.")
        else: st.warning("⚠️ Thiếu file 'image_toxic.png'.")

        st.warning("**Nguy cơ:** Phá hủy hệ hô hấp, hệ thần kinh, gây ngộ độc cấp tính hoặc tử vong nhanh chóng.")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            * **Giới hạn tiếp xúc:** Được tính bằng PPM (phần triệu) theo chuẩn ACGIH, bao gồm TWA (Giới hạn trung bình 8 giờ) và STEL (Phơi nhiễm ngắn hạn 15 phút).
            * **Các loại khí sát thủ phổ biến:**
                * **Carbon Monoxide (CO):** Kết hợp với hemoglobin trong máu chặn sự vận chuyển oxy. Mức TWA là 25 ppm. Mức 1.28% (12,800 ppm) gây tử vong chỉ trong 1-3 phút.
                * **Hydrogen Sulfide (H2S):** Khí có mùi trứng thối ở nồng độ thấp. Tuy nhiên, mức 100-300 ppm làm **tê liệt khứu giác hoàn toàn trong 2-15 phút**, khiến người lao động nhầm tưởng an toàn. Ở 700-1,000 ppm sẽ gây liệt hô hấp và tử vong.
            """)
        with col2:
            st.info("💡 **Giải pháp Riken Keiki:**\nSử dụng cảm biến điện hóa (Electrochemical) chuyên biệt, giúp đo chính xác nồng độ phần triệu với độ bền cao.")

    with tab3:
        st.header("💨 Khí Oxy (Oxygen - O2)")
        if os.path.exists("image_oxygen.png"):
            st.image("image_oxygen.png", use_container_width=True, caption="Sự nguy hiểm của không gian hạn hẹp (thiếu Oxy) và môi trường dễ bắt lửa (thừa Oxy).")
        else: st.warning("⚠️ Thiếu file 'image_oxygen.png'.")

        st.info("**Nguy cơ:** Cả việc Thiếu hụt (Anoxia) hay Dư thừa (Enrichment) Oxy đều vô cùng nguy hiểm.")
        st.markdown("""
        * **Mức tiêu chuẩn:** Không khí bình thường hít thở luôn chứa **20.93% Oxy**.
        """)
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            st.error("**📉 Thiếu Oxy / Ngạt thở (< 18%)**\nGiới hạn an toàn là 18%, dưới mức này phải có thiết bị bảo hộ hô hấp.\n* **16-12%:** Tăng nhịp tim/nhịp thở, nhức đầu.\n* **10-6%:** Buồn nôn, mất kiểm soát di chuyển, tím tái, bất tỉnh.\n* **Dưới 6%:** Ngừng thở, tim ngừng đập và tử vong.")
        with col_o2:
            st.warning("**📈 Thừa Oxy (> 23.5%)**\nXảy ra khi có rò rỉ từ các bình chứa khí Oxy công nghiệp. Môi trường thừa Oxy khiến mọi vật liệu trở nên cực kỳ dễ bắt lửa và bùng cháy.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("Hầu hết các máy đo khí cầm tay của Riken Keiki đều tích hợp cảm biến đo Oxy (Galvanic cell) để bảo vệ mạng sống người lao động trong không gian hạn hẹp.")

    st.markdown("---")
    st.markdown("*Nắm vững những kiến thức này, bạn sẽ hiểu vì sao công việc tại Riken Việt không chỉ là kinh doanh thiết bị, mà là **Bảo vệ Sự sống**!*")
