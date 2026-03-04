import streamlit as st
import os
import pandas as pd
from datetime import datetime

try:
    from github import Github
except ImportError:
    Github = None

# ==========================================
# CẤU HÌNH TRANG & BỘ NHỚ
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
    # KHO CSS HIỆU ỨNG TỔNG HỢP CHO CẢ 3 TAB
    st.markdown("""
    <style>
    /* Hiệu ứng Tab 1: Khí cháy nổ */
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 78, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0); }
    }
    .alert-box {
        background: linear-gradient(45deg, #ff4e50, #f9d423); padding: 15px; border-radius: 8px; color: white; animation: pulse-red 2s infinite; margin-bottom: 15px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Hiệu ứng Tab 2: Khí độc PPM */
    .toxic-glow {
        background-color: #1a1a1a; padding: 15px; border-radius: 8px; border-left: 5px solid #a8ff78; color: #a8ff78; margin-bottom: 15px; font-weight: bold;
    }
    .ppm-container { width: 100%; background-color: #e9ecef; border-radius: 5px; margin: 10px 0 25px 0; border: 1px solid #ccc; position: relative; height: 35px; box-shadow: inset 0 1px 3px rgba(0,0,0,.1); }
    .ppm-bar { height: 100%; border-radius: 5px 0 0 5px; display: flex; align-items: center; justify-content: flex-end; padding-right: 5px; color: white; font-weight: bold; font-size: 12px; }
    
    /* Hiệu ứng Tab 3: Oxy suy giảm */
    @keyframes blink { 50% { opacity: 0.5; } }
    .oxy-bg { background-color: #222; border-radius: 6px; width: 100%; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .oxy-bar { height: 32px; border-radius: 6px; color: white; text-align: right; padding-right: 15px; font-weight: bold; line-height: 32px; font-size: 14px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); transition: width 1s ease-in-out; }
    .danger-blink { animation: blink 1s linear infinite; }
    </style>
    """, unsafe_allow_html=True)

    st.title("☣️ Kiến Thức Cơ Bản Về Các Loại Khí Nguy Hiểm")
    st.markdown("Trong môi trường công nghiệp, rủi ro về khí là những **'Kẻ thù vô hình'**. Việc sử dụng các thiết bị dò khí (gas detectors) để theo dõi nồng độ của các loại khí này cũng như đảm bảo lượng oxy luôn ở mức an toàn là điều bắt buộc để bảo vệ tính mạng con người.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🔥 1. Khí dễ cháy", "☠️ 2. Khí độc", "💨 3. Thiếu oxy & Ngạt khí"])

    # ---------------- TAB 1: KHÍ DỄ CHÁY ----------------
    with tab1:
        st.header("🔥 Khí dễ cháy (Combustible gases)")
        st.markdown('<div class="alert-box"><b>⚠️ ĐỊNH NGHĨA:</b> Là loại khí có thể gây cháy hoặc nổ nếu chúng hòa trộn với oxy (trong không khí) ở một nồng độ nhất định và tiếp xúc với nguồn gây cháy (tia lửa, nhiệt độ cao).</div>', unsafe_allow_html=True)
        
        if os.path.exists("image_combustible.png"):
            st.image("image_combustible.png", use_container_width=True)

        st.markdown("### 📊 Trực quan hóa Giới hạn cháy nổ (Explosive Range)")
        
        html_lel_uel = """
        <div style="width: 100%; background-color: #f1f3f4; border-radius: 8px; position: relative; height: 40px; margin-bottom: 30px; display: flex; text-align: center; color: white; font-weight: bold; line-height: 40px; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="width: 25%; background-color: #28a745; border-radius: 8px 0 0 8px;">Quá loãng (Chưa thể cháy)</div>
            <div style="width: 45%; background-color: #dc3545; position: relative;">
                <span style="position: absolute; top: -30px; left: 0; color: #dc3545; font-size: 16px;">▼ LEL</span>
                🔥 VÙNG CHÁY NỔ (NGUY HIỂM) 🔥
                <span style="position: absolute; top: -30px; right: 0; color: #dc3545; font-size: 16px;">UEL ▼</span>
            </div>
            <div style="width: 30%; background-color: #ffc107; border-radius: 0 8px 8px 0; color: #333;">Quá đặc (Thiếu Oxy)</div>
        </div>
        """
        st.markdown(html_lel_uel, unsafe_allow_html=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown("""
            **Giải thích thuật ngữ:**
            * **LEL (Lower Explosive Limit):** Giới hạn nổ dưới. Dưới mức này, khí quá loãng để cháy.
            * **UEL (Upper Explosive Limit):** Giới hạn nổ trên. Trên mức này, hỗn hợp quá đặc khí nên không cháy được.
            * **Quy định an toàn:** Khí dễ cháy bao gồm các loại khí có giới hạn nổ dưới (LEL) từ **10% trở xuống**, hoặc những khí có khoảng chênh lệch giữa UEL và LEL từ **20% trở lên**.
            """)
        with col2:
            st.markdown("""
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #0056b3; height: 100%;">
                <h4 style="color: #0056b3; margin-top: 0;">💡 Tiêu chuẩn An toàn (Riken Keiki)</h4>
                <p style="color: #333; font-size: 15px;">
                    Điểm báo động (Alarm) <b>KHÔNG ĐƯỢC PHÉP</b> cài đặt vượt quá <b>1/4 (tức 25%) của mức LEL</b>.<br>
                    Nhờ đó công nhân có "thời gian vàng" để sơ tán trước khi đạt ngưỡng nổ.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- TAB 2: KHÍ ĐỘC ----------------
    with tab2:
        st.header("☠️ Khí độc (Toxic gases)")
        st.markdown('<div class="toxic-glow">☢️ ĐỊNH NGHĨA: Là các loại khí gây hại cho sức khỏe con người. Mức độ nguy hiểm thường được đánh giá qua "nồng độ cho phép" – mức tối đa mà người lao động có thể tiếp xúc nhiều lần nhưng không bị ảnh hưởng xấu.</div>', unsafe_allow_html=True)
        
        
        if os.path.exists("image_toxic.png"):
            st.image("image_toxic.png", use_container_width=True)

        st.markdown("### 🔬 Khái niệm PPM (Phần triệu) nguy hiểm tới mức nào?")
        st.write("Trong 1.000.000 hạt không khí, chỉ cần lẫn vào vài chục hạt khí độc đã đủ cướp đi sinh mạng con người. Hãy xem mô phỏng tỷ lệ dưới đây:")
        
        html_ppm = """
        <div class="ppm-container">
            <div class="ppm-bar" style="width: 1.28%; background-color: #dc3545;">1.28%</div>
            <span style="position:absolute; left: 2%; top: 7px; color: #333; font-weight: bold;">CO (Carbon monoxide): 12,800 ppm (Tử vong trong 1-3 phút)</span>
        </div>
        <div class="ppm-container">
            <div class="ppm-bar" style="width: 0.5%; background-color: #8b0000;">0.5%</div>
            <span style="position:absolute; left: 1%; top: 7px; color: #333; font-weight: bold;">H2S (Hydrogen sulfide): 5,000 ppm (Tử vong NGAY LẬP TỨC)</span>
        </div>
        """
        st.markdown(html_ppm, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.error("**Carbon monoxide (CO) - Sát thủ thầm lặng**\n* Khí không màu và không mùi.\n* **Cơ chế:** Xâm nhập vào máu, kết hợp với hemoglobin trong hồng cầu, ngăn cơ thể vận chuyển oxy.\n* **Triệu chứng:** Đau đầu, buồn nôn, chóng mặt.")
        with col2:
            st.warning("**Hydrogen sulfide (H2S) - Khí mùi trứng thối**\n* Tình trạng ngộ độc xảy ra khi nồng độ vượt quá **10 ppm**.\n* **Sự đánh lừa nguy hiểm:** Gây **tê liệt khứu giác** làm nạn nhân không còn ngửi thấy mùi thối nữa.\n* **Triệu chứng:** Kích ứng mắt, phổi, phù phổi.")

    # ---------------- TAB 3: THIẾU OXY ----------------
    with tab3:
        st.header("💨 Tình trạng thiếu oxy và ngạt khí (Anoxia)")
        st.markdown("Trong điều kiện bình thường, không khí chúng ta hít thở chứa khoảng **20,93% oxy**. Tình trạng 'thiếu oxy' được xác định khi nồng độ oxy trong không khí **giảm xuống dưới 18%**.")
        
        if os.path.exists("image_oxygen.png"):
            st.image("image_oxygen.png", use_container_width=True)

        st.markdown("### 📊 Mức độ đe dọa sinh tồn khi Oxy suy giảm:")
        
        # Thanh CSS Depletion Bar được làm lại đẹp hơn
        html_oxy = """
        <div class="oxy-bg"><div class="oxy-bar" style="width: 100%; background: linear-gradient(90deg, #11998e, #38ef7d);">20.93% - KHÔNG KHÍ BÌNH THƯỜNG</div></div>
        <div class="oxy-bg"><div class="oxy-bar" style="width: 86%; background: linear-gradient(90deg, #f2c94c, #f2994a); color: #000;">Dưới 18% - THIẾU OXY (Báo động an toàn)</div></div>
        <div class="oxy-bg"><div class="oxy-bar" style="width: 67%; background: linear-gradient(90deg, #e65c00, #F9D423);">16% ~ 12% - Thở gấp, tăng nhịp tim, buồn nôn</div></div>
        <div class="oxy-bg"><div class="oxy-bar danger-blink" style="width: 38%; background: linear-gradient(90deg, #b20a2c, #fffbd5); color: #000;">10% ~ 6% - Ảo giác, co giật, bất tỉnh</div></div>
        <div class="oxy-bg"><div class="oxy-bar danger-blink" style="width: 15%; background: linear-gradient(90deg, #cb2d3e, #ef473a);">≤ 6% - TỬ VONG NGAY LẬP TỨC</div></div>
        """
        st.markdown(html_oxy, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.success("💡 **Bài học sinh tử:** Không một ai có thể tự 'ngửi' hay 'cảm nhận' được lượng Oxy đang giảm đi trong không gian hạn hẹp. Do đó, đeo máy đo khí đa chỉ tiêu (như dòng GX) là quy tắc bắt buộc để sống sót.")
