import streamlit as st
import os
import pandas as pd
from datetime import datetime

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
                    "Câu 1 (C)": ans1[:15] + "...", 
                    "Câu 2 (B)": ans2[:15] + "...",
                    "Câu 3 (C)": ans3[:15] + "..."
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
            with st.spinner("Đang gửi bài lên máy chủ GitHub..."):
                score = 0
                if q1.startswith("C"): score += 1
                if q2.startswith("B"): score += 1
                if q3.startswith("C"): score += 1
                
                success, msg = save_to_github(user_name, score, str(q1), str(q2), str(q3))
                if success:
                    if score == 3:
                        st.session_state.quiz_passed = True
                        st.success("🎉 CHÚC MỪNG! Bạn đã trả lời đúng hoàn toàn.")
                    else:
                        st.session_state.quiz_passed = False
                        st.error(f"⚠️ Bạn đạt {score}/3 điểm. Vui lòng xem lại kiến thức và thực hiện lại bài thi!")
                else:
                    st.warning("⚠️ Lỗi kết nối GitHub!")

# ==========================================
# 4. THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==========================================
with st.sidebar:
    if os.path.exists("images/rkv_logo.png"):
        st.image("images/rkv_logo.png", use_container_width=True)
    st.markdown("## 📑 Menu Đào Tạo")
    app_mode = st.radio("Chọn chuyên mục:", [
        "🎓 Cổng Đào Tạo Hội Nhập",
        "☣️ Kiến Thức: Phân Loại Khí",
        "📟 Phân Loại Thiết Bị"
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
        st.markdown("**Xin chào thành viên mới!** Vui lòng tìm hiểu về lịch sử công ty, theo dõi video và hoàn thành bài kiểm tra.")
    with col_admin:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.popover("🗄️ Dành cho Quản lý (Admin)", use_container_width=True):
            st.markdown("**📂 Kho lưu trữ Lịch sử Đào tạo**")
            if st.button("🔄 Tải dữ liệu mới nhất", use_container_width=True):
                with st.spinner("Đang trích xuất dữ liệu..."):
                    records = fetch_history_from_github()
                    if records:
                        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
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
            st.success("🎉 Hệ thống xác nhận bạn hoàn thành khóa Onboarding!")
        with col_cert2:
            st.download_button("📥 Tải Sổ tay nhân viên (PDF)", data="Nội dung PDF...", file_name="SoTay_RikenViet.pdf", type="primary", use_container_width=True)

# ---------------- TRANG 2: KIẾN THỨC VỀ KHÍ (FULL RECOVERY) ----------------
elif app_mode == "☣️ Kiến Thức: Phân Loại Khí":
    st.markdown("""<style> 
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 78, 80, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0); } } 
    .alert-box { background: linear-gradient(45deg, #ff4e50, #f9d423); padding: 15px; border-radius: 8px; color: white; animation: pulse-red 2s infinite; margin-bottom: 15px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); } 
    .toxic-glow { background-color: #1a1a1a; padding: 15px; border-radius: 8px; border-left: 5px solid #a8ff78; color: #a8ff78; margin-bottom: 15px; font-weight: bold; } 
    .special-glow { background: linear-gradient(90deg, #2c003e, #4c0070); padding: 15px; border-radius: 8px; border-left: 5px solid #d400ff; color: #f8e5ff; margin-bottom: 15px; font-weight: bold; } 
    .ppm-container { width: 100%; background-color: #e9ecef; border-radius: 5px; margin: 10px 0 25px 0; border: 1px solid #ccc; position: relative; height: 35px; box-shadow: inset 0 1px 3px rgba(0,0,0,.1); } 
    .ppm-bar { height: 100%; border-radius: 5px 0 0 5px; display: flex; align-items: center; justify-content: flex-end; padding-right: 5px; color: white; font-weight: bold; font-size: 12px; } 
    .ppb-bar { height: 100%; border-radius: 5px; display: flex; align-items: center; justify-content: flex-start; padding-left: 10px; color: white; font-weight: bold; font-size: 13px; background: linear-gradient(90deg, #d400ff, #8a2be2); box-shadow: 0 0 10px #d400ff; } 
    @keyframes blink { 50% { opacity: 0.5; } } 
    .oxy-bg { background-color: #222; border-radius: 6px; width: 100%; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); } 
    .oxy-bar { height: 32px; border-radius: 6px; color: white; text-align: right; padding-right: 15px; font-weight: bold; line-height: 32px; font-size: 14px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); transition: width 1s ease-in-out; } 
    .danger-blink { animation: blink 1s linear infinite; } 
    </style>""", unsafe_allow_html=True)

    st.title("☣️ Kiến Thức Chuyên Sâu Các Loại Khí Nguy Hiểm")
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 1. Khí dễ cháy", "☠️ 2. Khí độc", "💨 3. Thiếu oxy & Ngạt khí", "🏥 4. Khí đặc biệt (Y tế/Hun trùng)"])

    # --- TAB 1: KHÍ DỄ CHÁY ---
    with tab1:
        st.header("🔥 Khí dễ cháy (Combustible gases)")
        st.markdown('<div class="alert-box"><b>⚠️ ĐỊNH NGHĨA:</b> Là khí có thể cháy nổ khi hòa trộn với oxy ở một nồng độ nhất định và tiếp xúc với nguồn cháy.</div>', unsafe_allow_html=True)
        if os.path.exists("images/image_combustible.png"): st.image("images/image_combustible.png", use_container_width=True)
        
        st.markdown("### 📊 Trực quan hóa Giới hạn cháy nổ (Explosive Range)")
        html_lel_uel = """<div style="width: 100%; background-color: #f1f3f4; border-radius: 8px; position: relative; height: 40px; margin-bottom: 30px; display: flex; text-align: center; color: white; font-weight: bold; line-height: 40px; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="width: 25%; background-color: #28a745; border-radius: 8px 0 0 8px;">Quá loãng</div><div style="width: 45%; background-color: #dc3545; position: relative;"><span style="position: absolute; top: -30px; left: 0; color: #dc3545; font-size: 16px;">▼ LEL</span>🔥 VÙNG CHÁY NỔ (NGUY HIỂM) 🔥<span style="position: absolute; top: -30px; right: 0; color: #dc3545; font-size: 16px;">UEL ▼</span></div><div style="width: 30%; background-color: #ffc107; border-radius: 0 8px 8px 0; color: #333;">Quá đặc (Thiếu Oxy)</div></div>"""
        st.markdown(html_lel_uel, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1.2, 1], gap="medium")
        with col1:
            st.markdown("### 📋 Bảng tra cứu LEL/UEL phổ biến")
            st.markdown("""
            | Tên Khí (Công thức) | LEL (%) | UEL (%) |
            | :--- | :---: | :---: |
            | **Methane (CH4)** | 5.0 | 15.0 |
            | **Hydrogen (H2)** | 4.0 | 75.6 |
            | **Propane (C3H8)** | 2.1 | 9.5 |
            | **Iso-butane (i-C4H10)** | 1.8 | 8.4 |
            | **Acetylene (C2H2)** | 2.5 | 100.0 |
            | **Carbon Monoxide (CO)** | 12.5 | 74.0 |
            """)
        with col2:
            st.info("**💡 Tiêu chuẩn An toàn (Riken Keiki)**\n\nĐiểm Alarm **KHÔNG ĐƯỢC PHÉP** cài đặt vượt quá **1/4 (tức 25%) mức LEL**. Ví dụ: Methane có LEL=5.0% thì máy sẽ báo động ngay khi đạt **1.25%vol**.")

    # --- TAB 2: KHÍ ĐỘC ---
    with tab2:
        st.header("☠️ Khí độc (Toxic gases)")
        st.markdown('<div class="toxic-glow">☢️ ĐỊNH NGHĨA: Gây hại trực tiếp cho sức khỏe con người qua đường hô hấp. Mức độ nguy hiểm cực cao ở nồng độ cực thấp.</div>', unsafe_allow_html=True)
        if os.path.exists("images/image_toxic.png"): st.image("images/image_toxic.png", use_container_width=True)
        
        st.markdown("### 🔄 Quy đổi nồng độ: % Thể tích (%vol) sang Phần triệu (PPM)")
        st.info("💡 **Công thức:** 1% vol = 10,000 ppm. Khí độc được đo bằng ppm vì chúng giết người ngay cả khi chỉ chiếm 0.001% không khí.")
        
        col_c1, col_c2 = st.columns([1.2, 1], gap="medium")
        with col_c1:
            st.markdown("""
            | % Thể tích (% vol) | Phần triệu (ppm) | Mức độ / Ví dụ |
            | :--- | :--- | :--- |
            | 100 % | 1,000,000 ppm | Khí nguyên chất |
            | 1 % | **10,000 ppm** | 🔴 Chết người ngay lập tức |
            | 0.1 % | 1,000 ppm | Báo động cực kỳ nghiêm trọng |
            | 0.01 % | 100 ppm | Ngưỡng phơi nhiễm (VD: CO) |
            | 0.001 % | 10 ppm | Mức báo động an toàn (VD: H2S) |
            """)
        with col_c2:
            st.markdown("### 🔬 Sát thủ tàng hình nguy hiểm cỡ nào?")
            html_ppm = """<div class="ppm-container"><div class="ppm-bar" style="width: 1.28%; background-color: #dc3545;">1.28%</div><span style="position:absolute; left: 2%; top: 7px; color: #333; font-weight: bold;">CO: 12,800 ppm (Tử vong 1-3 phút)</span></div><div class="ppm-container"><div class="ppm-bar" style="width: 0.5%; background-color: #8b0000;">0.5%</div><span style="position:absolute; left: 1%; top: 7px; color: #333; font-weight: bold;">H2S: 5,000 ppm (Tử vong NGAY LẬP TỨC)</span></div>"""
            st.markdown(html_ppm, unsafe_allow_html=True)
            st.warning("**Carbon monoxide (CO):** Không màu/mùi. Ngăn hồng cầu chở oxy.\n\n**Hydrogen sulfide (H2S):** Mùi trứng thối. Gây **tê liệt khứu giác** khiến nạn nhân tưởng đã an toàn.")

    # --- TAB 3: THIẾU OXY ---
    with tab3:
        st.header("💨 Thiếu oxy và ngạt khí (Anoxia)")
        st.markdown("Trong điều kiện chuẩn, không khí chứa **20.93% oxy**. Trạng thái nguy hiểm bắt đầu khi oxy giảm xuống dưới **18%**.")
        if os.path.exists("images/image_oxygen.png"): st.image("images/image_oxygen.png", use_container_width=True)
        st.markdown("### 📊 Mức độ đe dọa sinh tồn khi Oxy suy giảm:")
        html_oxy = """<div class="oxy-bg"><div class="oxy-bar" style="width: 100%; background: linear-gradient(90deg, #11998e, #38ef7d);">20.93% - KHÔNG KHÍ BÌNH THƯỜNG</div></div><div class="oxy-bg"><div class="oxy-bar" style="width: 86%; background: linear-gradient(90deg, #f2c94c, #f2994a); color: #000;">Dưới 18% - THIẾU OXY (Báo động an toàn)</div></div><div class="oxy-bg"><div class="oxy-bar" style="width: 67%; background: linear-gradient(90deg, #e65c00, #F9D423);">16% ~ 12% - Thở gấp, tăng nhịp tim, buồn nôn</div></div><div class="oxy-bg"><div class="oxy-bar danger-blink" style="width: 38%; background: linear-gradient(90deg, #b20a2c, #fffbd5); color: #000;">10% ~ 6% - Ảo giác, bất tỉnh, co giật</div></div><div class="oxy-bg"><div class="oxy-bar danger-blink" style="width: 15%; background: linear-gradient(90deg, #cb2d3e, #ef473a);">≤ 6% - TỬ VONG TRONG VÀI GIÂY</div></div>"""
        st.markdown(html_oxy, unsafe_allow_html=True)

    # --- TAB 4: KHÍ ĐẶC BIỆT ---
    with tab4:
        st.header("🏥 Khí đặc thù: Y tế, Khử trùng & Hun trùng")
        st.markdown('<div class="special-glow">☣️ CẢNH BÁO: Các loại khí y tế/khử trùng có độc tính cực mạnh, giới hạn an toàn tính bằng phần tỷ (ppb).</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns([1.2, 1], gap="large")
        with col_s1:
            st.markdown("### 1. Khử trùng / Hun trùng (Fumigation)")
            st.markdown("- **Các khí:** Phosphine (PH3), Methyl bromide, Ethylene oxide (EO).\n- **Độ độc:** PH3 an toàn chỉ ở mức **0.05 ppm** (50 ppb).")
            st.info("💡 **Khái niệm PPB (Phần tỷ):** 0.05 ppm = 50 ppb. Rất khó phát hiện nếu không có cảm biến siêu nhạy.")
            html_ppb = """<div class="ppm-container" style="height: 40px;"><div class="ppb-bar" style="width: 5%;">50 ppb (Mức báo động PH3)</div><span style="position:absolute; right: 10px; top: 10px; color: #777; font-size: 12px;">1 Tỷ hạt không khí</span></div>"""
            st.markdown(html_ppb, unsafe_allow_html=True)
            st.markdown("### 2. Khí Gây mê (Anesthetic)\n- N2O, Halothane, Sevoflurane...\n- Rò rỉ phòng mổ gây ảnh hưởng sức khỏe lâu dài cho đội ngũ y bác sĩ.")
        with col_s2:
            st.markdown("### 🛡️ Thiết bị chuyên dụng Riken Keiki")
            st.markdown("""<div style="background-color: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 10px;"><h5 style="color: #d400ff; margin-top: 0;">📟 SP-230 / 📼 FP-300 / 🔭 FI-8000</h5><p style="font-size: 14px; color: #555;">Đây là các dòng máy chuyên dụng sử dụng công nghệ băng cassette hoặc giao thoa quang học để đo nồng độ ppb chính xác tuyệt đối.</p></div>""", unsafe_allow_html=True)

# ---------------- TRANG 3: PHÂN LOẠI THIẾT BỊ ----------------
elif app_mode == "📟 Phân Loại Thiết Bị":
    st.markdown("""<style> .branch-title { font-size: 1.2rem; font-weight: bold; color: #0056b3; padding-bottom: 5px; border-bottom: 2px solid #0056b3; margin-top: 20px; margin-bottom: 15px; text-transform: uppercase; } .branch-title-fixed { color: #dc3545; border-bottom: 2px solid #dc3545; } </style>""", unsafe_allow_html=True)
    st.title("📟 Showroom: Thiết Bị Đo Khí Riken Keiki")
    tab_portable, tab_fixed = st.tabs(["📱 MÁY CẦM TAY (PORTABLE)", "🏭 HỆ THỐNG CỐ ĐỊNH (FIXED)"])

    with tab_portable:
        st.markdown('<div class="branch-title">1. Máy đo Đa Khí (Multi Gas Detectors)</div>', unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3, gap="medium")
        with col_m1:
            with st.container(border=True):
                if os.path.exists("images/gx-3r.png"): st.image("images/gx-3r.png")
                st.markdown("#### GX-3R (4 khí)\n- Nhỏ nhẹ nhất thế giới.\n- R sensor (BH 3 năm).\n- Bluetooth, IP66/68.")
            with st.container(border=True):
                if os.path.exists("images/sc-9000.png"): st.image("images/sc-9000.png")
                st.markdown("#### SC-9000 (Khí độc)\n- Lắp 3 khí độc (3-in-1).\n- Pin sạc 60h.\n- Bluetooth, chống va đập.")
        with col_m2:
            with st.container(border=True):
                if os.path.exists("images/gx-3r-pro.png"): st.image("images/gx-3r-pro.png")
                st.markdown("#### GX-3R Pro (5 khí)\n- Bản cao cấp, Bluetooth.\n- Đo tới 5 khí đồng thời.\n- Thiết kế không gây vướng.")
            with st.container(border=True):
                if os.path.exists("images/gx-force.png"): st.image("images/gx-force.png")
                st.markdown("#### GX-Force (4 khí)\n- Bơm hút gọn nhẹ (300g).\n- Pin 30h liên tục.\n- Thả rơi 3m, đo 27 khí cháy.")
        with col_m3:
            with st.container(border=True):
                if os.path.exists("images/gx-9000.png"): st.image("images/gx-9000.png")
                st.markdown("#### GX-9000 / 9000H\n- Bơm hút xa 45m.\n- Đo 6 khí (kể cả VOC).\n- Thả rơi 1.5m, Bluetooth.")
            with st.container(border=True):
                if os.path.exists("images/gx-6000.png"): st.image("images/gx-6000.png")
                st.markdown("#### GX-6000 (6 khí)\n- Tích hợp đo VOCs.\n- Chọn lọc Benzene.\n- Panic/Man-down alarm.")

        st.markdown('<div class="branch-title">2. Máy đo Đơn khí & 2 Khí nhỏ gọn</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2, gap="medium")
        with col_s1:
            with st.container(border=True):
                if os.path.exists("images/04-series.png"): st.image("images/04-series.png")
                st.markdown("#### Series 04\n- Siêu bền, chịu rơi 7m.\n- Pin cực dài (khô/sạc).\n- 12 model chuyên biệt.")
        with col_s2:
            with st.container(border=True):
                if os.path.exists("images/gw-3.png"): st.image("images/gw-3.png")
                st.markdown("#### Series GW-3\n- Nhẹ nhất thế giới.\n- Đeo cổ tay như đồng hồ.\n- Chuẩn IP66/68.")

        st.markdown('<div class="branch-title">3. Máy đo Khí dễ cháy chuyên dụng</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2, gap="medium")
        with col_c1:
            with st.container(border=True):
                if os.path.exists("images/gp-1000.png"): st.image("images/gp-1000.png")
                st.markdown("#### GP-1000 / NC-1000\n- **GP-1000**: Đo 0-100% LEL.\n- **NC-1000**: Đo LEL mức ppm.")
        with col_c2:
            with st.container(border=True):
                if os.path.exists("images/np-1000.png"): st.image("images/np-1000.png")
                st.markdown("#### NP-1000 / GP-03\n- **NP-1000**: Đo nồng độ cao 100vol%.\n- **GP-03**: Khuếch tán đơn khí cháy.")

        st.markdown('<div class="branch-title">4. Máy phát hiện rò rỉ & Khí đặc biệt</div>', unsafe_allow_html=True)
        col_l1, col_l2 = st.columns(2, gap="medium")
        with col_l1:
            with st.container(border=True):
                if os.path.exists("images/sp-230.png"): st.image("images/sp-230.png")
                st.markdown("#### SP-230 Series\n- Dò rò rỉ. Đèn LED soi sáng.\n- Type F (Freon), H2 (Hydro), FUM (Khử trùng).")
        with col_l2:
            with st.container(border=True):
                if os.path.exists("images/fi-8000.png"): st.image("images/fi-8000.png")
                st.markdown("#### FI-8000 / FP-31\n- **FI-8000**: Giao thoa quang học.\n- **FP-31**: Đo Formaldehyde chuẩn WHO.")

    with tab_fixed:
        st.markdown('<div class="branch-title branch-title-fixed">1. Tủ cảnh báo và Hệ thống trung tâm</div>', unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2, gap="medium")
        with col_f1:
            with st.container(border=True):
                if os.path.exists("images/gp-148.png"): st.image("images/gp-148.png")
                st.markdown("#### Hệ thống GP-148\n- UPS sẵn (3 ngày). Giám sát khí & lửa.\n- Trạm LPG, CNG, H2.")
            with st.container(border=True):
                if os.path.exists("images/rm-5000.png"): st.image("images/rm-5000.png")
                st.markdown("#### RM-5000 Series\n- Tủ đa điểm, thanh bar & số.\n- Tùy chọn Modbus RS-485.")
        with col_f2:
            with st.container(border=True):
                if os.path.exists("images/rm-6000.png"): st.image("images/rm-6000.png")
                st.markdown("#### RM-6000 Series\n- Bộ cảnh báo Module độc lập.\n- Màn hình LCD 3 màu đổi trạng thái.")
            with st.container(border=True):
                if os.path.exists("images/kanshiro.png"): st.image("images/kanshiro.png")
                st.markdown("#### Kanshiro II\n- Web SCADA. Quản lý 60.000 thẻ.\n- 100 triệu sự kiện, 3 năm xu hướng.")

        st.markdown('<div class="branch-title branch-title-fixed">2. Đầu dò khí thông minh (Smart Transmitters)</div>', unsafe_allow_html=True)
        col_f3, col_f4 = st.columns(2, gap="medium")
        with col_f3:
            with st.container(border=True):
                if os.path.exists("images/sd-3.png"): st.image("images/sd-3.png")
                st.markdown("#### SD-3 Series (Thế hệ mới)\n- F-Sensor: BH 3 năm, tự chẩn đoán.\n- SIL2/3, Thép SUS316, IP66/67.\n- Đo dải kép (ppm & LEL).")
            with st.container(border=True):
                if os.path.exists("images/sd-1.png"): st.image("images/sd-1.png")
                st.markdown("#### SD-1 Series\n- Vận hành 'khóa từ' an toàn.\n- Chống nổ Hydro/Axetylen.")
        with col_f4:
            with st.container(border=True):
                if os.path.exists("images/gd-70d.png"): st.image("images/gd-70d.png")
                st.markdown("#### Dòng GD-70D / GD-84D\n- Chuyên cho nhà máy Bán dẫn.\n- Plug & Play thay module nóng.")
            with st.container(border=True):
                if os.path.exists("images/gd-a2400.png"): st.image("images/gd-a2400.png")
                st.markdown("#### GD-A2400 / SD-2500\n- Cho lò đốt (thanh dài 250mm).\n- Chịu nhiệt độ cực cao 160°C.")

        st.markdown('<div class="branch-title branch-title-fixed">3. Máy phân tích đặc thù & Dùng trong nhà</div>', unsafe_allow_html=True)
        col_f5, col_f6 = st.columns(2, gap="medium")
        with col_f5:
            with st.container(border=True):
                if os.path.exists("images/600-series.png"): st.image("images/600-series.png")
                st.markdown("#### Dòng 600 Series\n- Gọn nhẹ cho văn phòng. Pin 1 năm.\n- OX-600 có sửa lỗi áp suất.")
        with col_f6:
            with st.container(border=True):
                if os.path.exists("images/fi-900.png"): st.image("images/fi-900.png")
                st.markdown("#### FI-900 / OHC-800\n- Giao thoa quang học & Nhiệt lượng kế.\n- Độ chính xác tuyệt đối ngành khí.")
