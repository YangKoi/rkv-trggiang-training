import streamlit as st
import os
import pandas as pd
from datetime import datetime

try:
    from github import Github
except ImportError:
    Github = None

# ==========================================
# CẤU HÌNH TRANG & BỘ NHỚ (SESSION STATE)
# ==========================================
st.set_page_config(page_title="Riken Viet - Đào tạo nội bộ", page_icon="🎓", layout="wide")

if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = False

# ==========================================
# CÁC HÀM GIAO TIẾP VỚI GITHUB
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
# CỬA SỔ POPUP BÀI KIỂM TRA
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
# THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
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
# NỘI DUNG TỪNG TRANG
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
    # CSS Hiệu ứng động
    st.markdown("""
    <style>
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 78, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0); }
    }
    .alert-box {
        background: linear-gradient(45deg, #ff4e50, #f9d423); padding: 15px; border-radius: 8px; color: white; animation: pulse-red 2s infinite; margin-bottom: 15px;
    }
    .toxic-glow {
        background-color: #2b2b2b; padding: 15px; border-radius: 8px; border-left: 5px solid #a8ff78; color: #a8ff78; text-shadow: 0 0 5px #a8ff78; margin-bottom: 15px;
    }
    .oxy-bar { height: 25px; border-radius: 5px; color: white; text-align: right; padding-right: 10px; font-weight: bold; line-height: 25px; margin-bottom: 5px; transition: width 1s ease-in-out; }
    .oxy-bg { background-color: #333; border-radius: 5px; width: 100%; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

    st.title("☣️ Kiến Thức Cơ Bản Về Các Loại Khí Nguy Hiểm")
    st.markdown("""
    Trong môi trường công nghiệp, rủi ro về khí là những **"Kẻ thù vô hình"**. Việc sử dụng các thiết bị dò khí (gas detectors) để theo dõi nồng độ của các loại khí này cũng như đảm bảo lượng oxy luôn ở mức an toàn là điều bắt buộc để bảo vệ tính mạng con người.
    """)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🔥 1. Khí dễ cháy", "☠️ 2. Khí độc", "💨 3. Thiếu oxy & Ngạt khí"])

    with tab1:
        st.header("🔥 Khí dễ cháy (Combustible gases)")
        
        # Hiệu ứng Cảnh báo nổ
        st.markdown('<div class="alert-box"><b>⚠️ ĐỊNH NGHĨA:</b> Là loại khí có thể gây cháy hoặc nổ nếu chúng hòa trộn với oxy (trong không khí) ở một nồng độ nhất định và tiếp xúc với nguồn gây cháy (tia lửa, nhiệt độ cao).</div>', unsafe_allow_html=True)
        
        
        if os.path.exists("image_combustible.png"):
            st.image("image_combustible.png", use_container_width=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            * **Các khái niệm cơ bản:** Khoảng nồng độ có thể gây nổ này được gọi là "giới hạn cháy nổ" (Explosive range). 
                * Mức nồng độ khí thấp nhất có thể gây nổ gọi là **Giới hạn nổ dưới (LEL)**.
                * Mức cao nhất gọi là **Giới hạn nổ trên (UEL)**. 
                * Dưới mức LEL thì khí quá loãng để cháy, còn trên mức UEL thì lại thiếu oxy để duy trì sự cháy.
            * **Quy định an toàn:** Khí dễ cháy bao gồm các loại khí có giới hạn nổ dưới (LEL) từ **10% trở xuống**, hoặc những khí có khoảng chênh lệch giữa giới hạn nổ trên và giới hạn nổ dưới từ **20% trở lên**.
            * **Ví dụ điển hình:** Metan (Methane), Hydro (Hydrogen), Propane, Acetylene, v.v..
            """)
        with col2:
            st.info("💡 Thiết bị Riken Keiki sẽ luôn được cài đặt để kích hoạt báo động từ rất sớm, thường ở mức 10% LEL, để đảm bảo công nhân có đủ thời gian sơ tán trước khi đạt ngưỡng nổ.")

    with tab2:
        st.header("☠️ Khí độc (Toxic gases)")
        
        # Hiệu ứng khí độc phát sáng
        st.markdown('<div class="toxic-glow"><b>☢️ ĐỊNH NGHĨA:</b> Là các loại khí gây hại cho sức khỏe con người. Mức độ nguy hiểm thường được đánh giá qua "nồng độ cho phép" – mức tối đa trong không khí mà người lao động có thể tiếp xúc nhiều lần nhưng không bị ảnh hưởng xấu.</div>', unsafe_allow_html=True)
        
        
        if os.path.exists("image_toxic.png"):
            st.image("image_toxic.png", use_container_width=True)

        st.markdown("### Một số loại khí độc cực kỳ phổ biến và nguy hiểm:")
        col1, col2 = st.columns(2)
        with col1:
            st.error("**Carbon monoxide (CO) - Sát thủ thầm lặng**\n* Khí không màu và không mùi.\n* **Cơ chế:** Xâm nhập vào máu, kết hợp với hemoglobin trong hồng cầu và ngăn chặn cơ thể vận chuyển oxy.\n* **Triệu chứng:** Đau đầu, buồn nôn, chóng mặt.\n* **Nguy hiểm tột độ:** Ở nồng độ rất cao (khoảng 1,28% hoặc 12.800 ppm), nó có thể cướp đi sinh mạng chỉ trong **1 đến 3 phút**.")
        with col2:
            st.warning("**Hydrogen sulfide (H2S) - Khí mùi trứng thối**\n* Tình trạng ngộ độc xảy ra khi nồng độ vượt quá **10 ppm**.\n* **Triệu chứng:** Kích ứng mắt và phổi, viêm phế quản, phù phổi.\n* **Sự đánh lừa nguy hiểm:** Gây **tê liệt khứu giác** làm bạn không còn ngửi thấy mùi thối đặc trưng của nó nữa.\n* **Nguy hiểm tột độ:** Ở mức 5.000 ppm, H2S gây tử vong ngay lập tức.")

    with tab3:
        st.header("💨 Tình trạng thiếu oxy và ngạt khí (Anoxia)")
        st.markdown("Trong điều kiện bình thường, không khí chúng ta hít thở chứa khoảng **20,93% oxy**. Tình trạng 'thiếu oxy' được xác định khi nồng độ oxy trong không khí **giảm xuống dưới 18%**.")
        
        
        if os.path.exists("image_oxygen.png"):
            st.image("image_oxygen.png", use_container_width=True)

        st.markdown("### 📊 Biểu đồ trực quan hậu quả suy giảm Oxy:")
        
        # Hiệu ứng thanh đo suy giảm Oxy bằng HTML/CSS
        html_oxy = """
        <div class="oxy-bg"><div class="oxy-bar" style="width: 100%; background-color: #28a745;">20.93% - BÌNH THƯỜNG</div></div>
        <div class="oxy-bg"><div class="oxy-bar" style="width: 86%; background-color: #ffc107; color: black;">Dưới 18% - THIẾU OXY CẢNH BÁO</div></div>
        <div class="oxy-bg"><div class="oxy-bar" style="width: 67%; background-color: #fd7e14;">16% ~ 12% - Tăng nhịp tim, thở gấp, đau đầu, buồn nôn</div></div>
        <div class="oxy-bg"><div class="oxy-bar" style="width: 38%; background-color: #e83e8c;">10% ~ 6% - Mất khả năng di chuyển, ảo giác, co giật, bất tỉnh</div></div>
        <div class="oxy-bg"><div class="oxy-bar" style="width: 15%; background-color: #dc3545;">≤ 6% - NGỪNG THỞ, TỬ VONG NGAY LẬP TỨC</div></div>
        """
        st.markdown(html_oxy, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("Bởi vì con người không có giác quan để nhận biết nồng độ Oxy bị tuột giảm, việc sử dụng các thiết bị đo đa khí (như dòng GX-3R) mang bên người là quy tắc sinh tử khi bước vào không gian hạn hẹp (bồn chứa, cống ngầm).")

    st.markdown("---")
