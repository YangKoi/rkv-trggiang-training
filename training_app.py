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
# 3. POPUP BÀI KIỂM TRA
# ==========================================
@st.dialog("📝 BÀI KIỂM TRA HỘI NHẬP", width="large")
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
            with st.spinner("Đang nộp bài..."):
                score = 0
                if q1.startswith("C"): score += 1
                if q2.startswith("B"): score += 1
                if q3.startswith("C"): score += 1
                
                success, msg = save_to_github(user_name, score, str(q1), str(q2), str(q3))
                if success:
                    if score == 3:
                        st.session_state.quiz_passed = True
                        st.success("🎉 CHÚC MỪNG! Bạn đã đạt điểm tuyệt đối.")
                    else:
                        st.session_state.quiz_passed = False
                        st.error(f"⚠️ Bạn đạt {score}/3 điểm. Vui lòng học lại kiến thức!")
                else:
                    st.warning("⚠️ Lỗi kết nối máy chủ GitHub!")

# ==========================================
# 4. SIDEBAR (CẬP NHẬT BẢN QUYỀN)
# ==========================================
with st.sidebar:
    if os.path.exists("images/rkv_logo.png"):
        st.image("images/rkv_logo.png", use_container_width=True)
    st.markdown("## 📑 Menu Đào Tạo")
    app_mode = st.radio("Chọn chuyên mục:", [
        "🎓 Cổng Đào Tạo Hội Nhập",
        "☣️ Kiến Thức: Phân Loại Khí",
        "📟 Phân Loại Thiết Bị",
        "📖 Tiêu Chuẩn & Thuật Ngữ" # THÊM TAB MỚI
    ])
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #888888; font-size: 13px; margin-top: 30px;'>© Bản quyền thuộc về Riken Việt</div>", unsafe_allow_html=True)
# ==========================================
# 5. NỘI DUNG TỪNG TRANG
# ==========================================

# ---------------- TRANG 1: ĐÀO TẠO HỘI NHẬP ----------------
if app_mode == "🎓 Cổng Đào Tạo Hội Nhập":
    col_title, col_admin = st.columns([4, 1.5]) 
    with col_title:
        st.title("🎓 Cổng Đào Tạo Hội Nhập")
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
    st.subheader("📺 Video giới thiệu")
    st.video("https://youtu.be/DL9K-LVeqdc?si=T6vL91uEHSAbV_Dh") 
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

    st.title("☣️ Các Loại Khí Nguy Hiểm")
    st.markdown("Trong môi trường công nghiệp, rủi ro về khí là những **'Kẻ thù vô hình'**. Các thiết bị được thiết kế để theo dõi và bảo vệ sinh mạng.")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["🔥 1. Khí dễ cháy", "☠️ 2. Khí độc", "💨 3. Thiếu oxy & Ngạt khí", "🏥 4. Khí đặc biệt (Y tế/Hun trùng)"])

    # --- TAB 1: KHÍ DỄ CHÁY ---
    with tab1:
        st.header("🔥 Khí dễ cháy (Combustible gases)")
        st.markdown('<div class="alert-box"><b>⚠️ ĐỊNH NGHĨA:</b> Là khí có thể cháy hoặc nổ nếu hòa trộn với oxy ở một nồng độ nhất định và tiếp xúc với nguồn gây cháy (tia lửa, nhiệt độ cao).</div>', unsafe_allow_html=True)
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
            st.info("**💡 Tiêu chuẩn An toàn (Riken Keiki)**\n\nĐiểm Alarm **KHÔNG ĐƯỢC PHÉP** cài đặt vượt quá **1/4 (tức 25%) mức LEL**. Nhờ đó công nhân có 'thời gian vàng' để sơ tán.")

    # --- TAB 2: KHÍ ĐỘC ---
    with tab2:
        st.header("☠️ Khí độc (Toxic gases)")
        st.markdown('<div class="toxic-glow">☢️ ĐỊNH NGHĨA: Gây hại trực tiếp cho sức khỏe con người qua đường hô hấp. Mức độ nguy hiểm cực cao ở nồng độ cực thấp.</div>', unsafe_allow_html=True)
        if os.path.exists("images/image_toxic.png"): st.image("images/image_toxic.png", use_container_width=True)
        
        st.markdown("### 🔄 Quy đổi nồng độ: % Thể tích (%vol) sang Phần triệu (PPM)")
        st.info("💡 **Công thức:** 1% vol = 10,000 ppm. Vì khí độc nguy hiểm ở nồng độ cực thấp, người ta dùng 'ppm' thay vì '%' để tránh nhầm lẫn.")
        
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
            st.warning("**Carbon monoxide (CO):** Không màu/mùi. Xâm nhập máu ngăn vận chuyển oxy.\n\n**Hydrogen sulfide (H2S):** Mùi trứng thối. Gây **tê liệt khứu giác** khiến bạn tưởng đã hết nguy hiểm.")

    # --- TAB 3: THIẾU OXY ---
    with tab3:
        st.header("💨 Tình trạng thiếu oxy và ngạt khí (Anoxia)")
        st.markdown("Trong điều kiện bình thường, không khí chứa khoảng **20.93% oxy**. Tình trạng 'thiếu oxy' được xác định khi nồng độ giảm xuống dưới **18%**.")
        if os.path.exists("images/image_oxygen.png"): st.image("images/image_oxygen.png", use_container_width=True)
        st.markdown("### 📊 Mức độ đe dọa sinh tồn khi Oxy suy giảm:")
        html_oxy = """<div class="oxy-bg"><div class="oxy-bar" style="width: 100%; background: linear-gradient(90deg, #11998e, #38ef7d);">20.93% - KHÔNG KHÍ BÌNH THƯỜNG</div></div><div class="oxy-bg"><div class="oxy-bar" style="width: 86%; background: linear-gradient(90deg, #f2c94c, #f2994a); color: #000;">Dưới 18% - THIẾU OXY (Báo động an toàn)</div></div><div class="oxy-bg"><div class="oxy-bar" style="width: 67%; background: linear-gradient(90deg, #e65c00, #F9D423);">16% ~ 12% - Thở gấp, tăng nhịp tim, buồn nôn</div></div><div class="oxy-bg"><div class="oxy-bar danger-blink" style="width: 38%; background: linear-gradient(90deg, #b20a2c, #fffbd5); color: #000;">10% ~ 6% - Ảo giác, bất tỉnh, co giật</div></div><div class="oxy-bg"><div class="oxy-bar danger-blink" style="width: 15%; background: linear-gradient(90deg, #cb2d3e, #ef473a);">≤ 6% - TỬ VONG LẬP TỨC</div></div>"""
        st.markdown(html_oxy, unsafe_allow_html=True)
        st.success("💡 **Quy tắc sống còn:** Tuyệt đối không tự ý bước vào không gian hạn hẹp (hầm, cống) mà không có máy đo khí đo kiểm trước!")

    # --- TAB 4: KHÍ ĐẶC BIỆT ---
    with tab4:
        st.header("🏥 Khí đặc thù: Y tế, Khử trùng & Hun trùng")
        st.markdown('<div class="special-glow">☣️ CẢNH BÁO NGHIÊM NGẶT: Các loại khí dùng trong y tế, khử trùng và hun trùng (fumigation) được pháp luật và tiêu chuẩn an toàn phân loại nghiêm ngặt vào nhóm khí độc nguy hiểm tột độ. Bắt buộc phải có thiết bị phát hiện và báo động rò rỉ tại cơ sở lưu trữ.</div>', unsafe_allow_html=True)

        st.subheader("1. Khí khử trùng / Hun trùng (Fumigation gases)")
        st.markdown("""
        * **Các loại phổ biến:** Bao gồm Phosphine (PH3), Methyl bromide (CH3Br), Ethylene oxide (EO - thường dùng khử trùng dụng cụ y tế), Hydrogen cyanide, Sulfuryl fluoride, Methyl iodide, và Propylene oxide.
        * **Mức độ nguy hiểm cực cao:** Lấy ví dụ như **Phosphine (PH3)**, nồng độ giới hạn cho phép (TLV) theo tiêu chuẩn an toàn chỉ ở mức rất nhỏ là **0.05 ppm**. Ethylene oxide và Methyl bromide cũng là các hóa chất có độc tính mạnh, có khả năng gây ngộ độc nếu hít phải dù chỉ ở nồng độ thấp.
        """)
        
        st.info("💡 **Khái niệm PPB (Phần tỷ):** 0.05 ppm tương đương với **50 ppb**. Để phát hiện một lượng khí siêu nhỏ này đòi hỏi cảm biến công nghệ tối tân.")
        html_ppb = """<div class="ppm-container" style="height: 40px;"><div class="ppb-bar" style="width: 5%;">50 ppb (Mức báo động PH3)</div><span style="position:absolute; right: 10px; top: 10px; color: #777; font-size: 12px;">1 Tỷ hạt không khí</span></div>"""
        st.markdown(html_ppb, unsafe_allow_html=True)
        
        st.markdown("""
        **Thiết bị đo chuyên dụng:** Vì tính chất đặc thù, chúng yêu cầu các thiết bị phát hiện riêng biệt:
        - **Máy dò rò rỉ di động SP-230 (TYPE FUM):** Là dòng máy kiểu bơm hút được thiết kế riêng để phát hiện rò rỉ khí khử trùng. Một máy có thể hỗ trợ đo tới 7 loại khí khử trùng khác nhau.
        - **Hệ thống phát hiện siêu nhạy:** Để phát hiện PH3 rò rỉ ở nồng độ cực thấp, người ta sử dụng các máy đo dùng băng cassette (ví dụ: FP-300, FP-301) có khả năng phát hiện ở mức **ppb (phần tỷ)**.
        - **Máy đo nồng độ quang học FI-8000:** Có phiên bản sử dụng buồng đo 48 mm chuyên dùng để đo nồng độ chính xác của các loại khí hun trùng này trong không gian kín.
        """)

        st.markdown("---")
        st.subheader("2. Khí gây mê trong y tế (Anesthetic gases)")
        st.markdown("""
        Bên cạnh khí khử trùng, môi trường y tế còn đặc biệt lưu tâm đến các loại khí gây mê.
        * **Các loại phổ biến:** Nitrous oxide (khí cười - N2O), Halothane, Isoflurane, Sevoflurane, Desflurane, và Enflurane.
        * **Thiết bị đo:** Các loại khí gây mê này thường được đo lường nồng độ bằng **máy đo giao thoa quang học FI-8000** (phiên bản dùng buồng đo 24 mm). Máy dùng phương pháp đo chiết suất ánh sáng của khí, giúp đo lường chính xác mà không làm suy giảm độ nhạy của cảm biến theo thời gian.
        """)
        
        st.success("🎯 **Nhìn chung:** Dù ứng dụng trong công nghiệp hay y tế, đây đều là những khí có nguy cơ tiềm ẩn rất lớn. Quá trình làm việc đòi hỏi máy đo khí phải có độ chuẩn xác cực cao và khả năng phản hồi nhanh chóng.")

# ---------------- TRANG 3: PHÂN LOẠI THIẾT BỊ ----------------
elif app_mode == "📟 Phân Loại Thiết Bị":
    st.markdown("""<style> 
    .branch-title { font-size: 1.2rem; font-weight: bold; color: #0056b3; padding-bottom: 5px; border-bottom: 2px solid #0056b3; margin-top: 20px; margin-bottom: 15px; text-transform: uppercase; } 
    .branch-title-fixed { color: #dc3545; border-bottom: 2px solid #dc3545; } 
    </style>""", unsafe_allow_html=True)
    
    st.title("📟 Thiết Bị Đo Khí Riken Keiki")
    st.markdown("Hệ thống thiết bị được phân chia bài bản nhằm giúp Sales và Kỹ thuật lựa chọn chính xác giải pháp cho Khách hàng dựa trên nhu cầu Đo di động (Portable) hay Lắp giám sát cố định (Fixed).")
    st.markdown("---")

    tab_portable, tab_fixed = st.tabs(["📱 NHÁNH 1: MÁY ĐO CẦM TAY (PORTABLE)", "🏭 NHÁNH 2: HỆ THỐNG CỐ ĐỊNH (FIXED)"])

    # ================= KHU VỰC MÁY CẦM TAY =================
    with tab_portable:
        
        # 1. MÁY ĐO ĐA KHÍ
        st.markdown('<div class="branch-title">1. Máy đo Đa Khí (Multi Gas Detectors)</div>', unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3, gap="medium")
        
        with col_m1:
            with st.container(border=True):
                if os.path.exists("images/gx-3r.png"): st.image("images/gx-3r.png")
                st.markdown("#### GX-3R (4 khí)")
                st.markdown("- Dòng đo 4 khí khuếch tán **nhỏ và nhẹ nhất thế giới**.\n- Tích hợp R sensor (Bảo hành 3 năm).\n- Hỗ trợ Bluetooth báo động theo thời gian thực.\n- Chuẩn chống nước, chống bụi IP66/68.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gx-3r&post_type=any", use_container_width=True)
            
            with st.container(border=True):
                if os.path.exists("images/sc-9000.png"): st.image("images/sc-9000.png")
                st.markdown("#### SC-9000 (Khí độc)")
                st.markdown("- Máy đa khí độc bơm hút, lắp tối đa 3 cảm biến (**3-in-1**).\n- Tuổi thọ pin sạc cực dài khoảng 60 giờ.\n- Chống va đập, IP66/68, hỗ trợ Bluetooth.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=sc-9000&post_type=any", use_container_width=True)

        with col_m2:
            with st.container(border=True):
                if os.path.exists("images/gx-3r-pro.png"): st.image("images/gx-3r-pro.png")
                st.markdown("#### GX-3R Pro (5 khí)")
                st.markdown("- Bản cao cấp, hỗ trợ Bluetooth. Đo tới **5 thành phần khí** bằng cảm biến kép.\n- Hoạt động linh hoạt bằng pin sạc hoặc pin khô.\n- Thiết kế không gây vướng víu.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gx-3r-pro&post_type=any", use_container_width=True)
            
            with st.container(border=True):
                if os.path.exists("images/gx-force.png"): st.image("images/gx-force.png")
                st.markdown("#### GX-Force (4 khí)")
                st.markdown("- Dòng bơm hút nhẹ gọn chỉ 300g.\n- Hoạt động liên tục **30 giờ**.\n- Chịu lực thả rơi 3m, cảm biến BH 3 năm.\n- Chuyển đổi đo cho 27 loại khí cháy khác nhau.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gx-force&post_type=any", use_container_width=True)

        with col_m3:
            with st.container(border=True):
                if os.path.exists("images/gx-9000.png"): st.image("images/gx-9000.png")
                st.markdown("#### GX-9000 / GX-9000H")
                st.markdown("- Bơm hút công suất cao (hút xa 45m).\n- GX-9000: Đo tối đa **6 khí (kể cả VOC)**.\n- GX-9000H: Chuyên dùng cho môi trường H2S nồng độ cao.\n- Vượt test thả rơi 1.5m.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gx-9000&post_type=any", use_container_width=True)
            
            with st.container(border=True):
                if os.path.exists("images/gx-6100.png"): st.image("images/gx-6100.png")
                st.markdown("#### GX-6100 (6 khí)")
                st.markdown("- Thiết bị bơm hút đo 6 khí, tích hợp đo **VOCs**.\n- Có chế độ đo chọn lọc Benzene.\n- Tính năng an toàn: Báo động hoảng loạn (panic), ngã (man down), tích hợp đèn LED.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gx-6000&post_type=any", use_container_width=True)

        # 2. ĐƠN KHÍ VÀ 2 KHÍ NHỎ GỌN
        st.markdown('<div class="branch-title">2. Máy đo Đơn khí & 2 Khí nhỏ gọn</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2, gap="medium")
        with col_s1:
            with st.container(border=True):
                if os.path.exists("images/04-series.png"): st.image("images/04-series.png")
                st.markdown("#### Series 04")
                st.markdown("- Dòng khuếch tán **siêu bền**, chịu rơi từ 7 mét.\n- Hỗ trợ cả pin khô và pin sạc thời lượng cao.\n- Có tới 12 model chuyên biệt (Model CX-04 đo được 2 khí cùng lúc).")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=04-series&post_type=any", use_container_width=True)
        with col_s2:
            with st.container(border=True):
                if os.path.exists("images/gw-3.png"): st.image("images/gw-3.png")
                st.markdown("#### Series GW-3")
                st.markdown("- Thuộc nhóm thiết bị nhỏ gọn và **nhẹ nhất thế giới**.\n- Thiết kế mang tính cách mạng: Có thể **đeo trên cổ tay** bằng dây đeo đi kèm.\n- Chuẩn chống bụi/nước IP66/68.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gw-3&post_type=any", use_container_width=True)

        # 3. KHÍ DỄ CHÁY
        st.markdown('<div class="branch-title">3. Máy đo Khí dễ cháy chuyên dụng</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2, gap="medium")
        with col_c1:
            with st.container(border=True):
                if os.path.exists("images/gp-1000.png"): st.image("images/gp-1000.png")
                st.markdown("#### GP-1000 / NC-1000")
                st.markdown("- **GP-1000:** Bơm hút dải đo 0-100% LEL, chuyển đổi dễ dàng mục tiêu đo cho 25 loại khí cháy. Có bộ tăng cường bơm hút xa.\n- **NC-1000:** Chuyên đo LEL ở nồng độ cực thấp (ppm).")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gp-1000&post_type=any", use_container_width=True)
        with col_c2:
            with st.container(border=True):
                if os.path.exists("images/np-1000.png"): st.image("images/np-1000.png")
                st.markdown("#### NP-1000 / GP-03")
                st.markdown("- **NP-1000:** Đo nồng độ cao tới 100 vol% trong môi trường khí trơ (N2, CO2). Linh hoạt chuyển đổi 5 loại khí gốc.\n- **GP-03:** Máy khuếch tán đơn khí dễ cháy kèm ốp cao su chống sốc.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=np-1000&post_type=any", use_container_width=True)

        # 4. RÒ RỈ VÀ ĐẶC BIỆT
        st.markdown('<div class="branch-title">4. Máy phát hiện rò rỉ & Khí đặc biệt</div>', unsafe_allow_html=True)
        col_l1, col_l2 = st.columns(2, gap="medium")
        with col_l1:
            with st.container(border=True):
                if os.path.exists("images/sp-230.png"): st.image("images/sp-230.png")
                st.markdown("#### SP-230 Series")
                st.markdown("- Dòng máy chuyên tìm tâm điểm rò rỉ kiểu bơm hút.\n- **TYPE F:** Đo khí Fluorocarbon (Freon tủ lạnh).\n- **TYPE FUM:** Đo 7 loại khí khử trùng.\n- **TYPE SC:** Dò tới 50 loại khí bán dẫn.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=sp-230&post_type=any", use_container_width=True)
        with col_l2:
            with st.container(border=True):
                if os.path.exists("images/fi-8000.png"): st.image("images/fi-8000.png")
                st.markdown("#### FI-8000 / FP-31")
                st.markdown("- **FI-8000:** Dùng cảm biến giao thoa quang học, đo độ chính xác tuyệt đối cho khí gây mê y tế, khí hun trùng, nồng độ dung môi.\n- **FP-31:** Đo Formaldehyde (HCHO) chuyên dụng qua ruy băng quang điện.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=fi-8000&post_type=any", use_container_width=True)

    # ================= KHU VỰC HỆ THỐNG CỐ ĐỊNH =================
    with tab_fixed:
        
        # 1. TỦ CẢNH BÁO
        st.markdown('<div class="branch-title branch-title-fixed">1. Tủ cảnh báo và Hệ thống trung tâm (Alarm Units & Systems)</div>', unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2, gap="medium")
        
        with col_f1:
            with st.container(border=True):
                if os.path.exists("images/gp-148.png"): st.image("images/gp-148.png")
                st.markdown("#### Hệ thống GP-148")
                st.markdown("- Tủ cảnh báo khí dễ cháy cao cấp.\n- **Tích hợp sẵn UPS:** Duy trì hoạt động 3 ngày khi mất điện.\n- Cho phép kết hợp giám sát cả đầu dò khí và đầu dò ngọn lửa (Max 12 điểm).\n- Lý tưởng cho trạm chiết nạp LPG, CNG, H2.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gp-148&post_type=any", use_container_width=True)
                
            with st.container(border=True):
                if os.path.exists("images/rm-5000.png"): st.image("images/rm-5000.png")
                st.markdown("#### RM-5000 Series")
                st.markdown("- Tủ cảnh báo đa điểm (Multi-point).\n- Hiển thị nồng độ trực quan bằng **thanh bar meter** và số điện tử.\n- Tích hợp mạng truyền thông RS-485 (tùy chọn).")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=rm-5000&post_type=any", use_container_width=True)

        with col_f2:
            with st.container(border=True):
                if os.path.exists("images/rm-6000.png"): st.image("images/rm-6000.png")
                st.markdown("#### RM-6000 Series")
                st.markdown("- Bộ cảnh báo điểm đơn thiết kế dạng **module độc lập** (dễ bảo trì tháo lắp).\n- Màn hình LCD **3 màu đổi theo trạng thái** (Xanh: Bình thường, Cam: Báo động 1, Đỏ: Báo động 2).")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=rm-6000&post_type=any", use_container_width=True)

            with st.container(border=True):
                if os.path.exists("images/kanshiro.png"): st.image("images/kanshiro.png")
                st.markdown("#### Phần mềm Kanshiro II")
                st.markdown("- Hệ thống giám sát SCADA trên máy tính/điện thoại qua trình duyệt Web.\n- Quản lý siêu khủng: Lên tới **60.000 thẻ (tags)** tín hiệu.\n- Lưu trữ 100 triệu sự kiện và 3 năm dữ liệu xu hướng.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://product.rikenkeiki.co.jp/products/244-.html", use_container_width=True)

        # 2. ĐẦU DÒ THÔNG MINH
        st.markdown('<div class="branch-title branch-title-fixed">2. Đầu dò khí thông minh (Smart Detectors & Transmitters)</div>', unsafe_allow_html=True)
        col_f3, col_f4 = st.columns(2, gap="medium")
        
        with col_f3:
            with st.container(border=True):
                if os.path.exists("images/sd-3.png"): st.image("images/sd-3.png")
                st.markdown("#### SD-3 Series (Thế hệ mới)")
                st.markdown("- **Cảm biến F-Sensor**: Hiệu suất cao, BH 3 năm, tự chẩn đoán suy giảm.\n- **Đạt chuẩn SIL2/SIL3** và chống nổ quốc tế IECEx/ATEX.\n- Vỏ thép SCS14 siêu bền, chịu nhiệt -40 đến +70°C.\n- Đo dải kép (ppm & LEL), ngõ ra HART/Modbus.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=sd-3&post_type=any", use_container_width=True)

            with st.container(border=True):
                if os.path.exists("images/sd-1.png"): st.image("images/sd-1.png")
                st.markdown("#### Dòng SD-1 Series")
                st.markdown("- Tiêu chuẩn chống nổ khắt khe (dùng được trong môi trường Hydro và Axetylen).\n- Vận hành hoàn toàn bằng **'khóa từ'** bên ngoài kính, an toàn không cần mở nắp.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=sd-1&post_type=any", use_container_width=True)

            with st.container(border=True):
                if os.path.exists("images/gd-70d.png"): st.image("images/gd-70d.png")
                st.markdown("#### Dòng GD-70D")
                st.markdown("- Chuyên dùng cho nhà máy bán dẫn.\n- Thiết kế **Plug & Play**: Thay module cảm biến là đổi được loại khí đo, không cần thay vỏ máy. Tiết kiệm 20% điện năng.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gd-70d&post_type=any", use_container_width=True)

        with col_f4:
            with st.container(border=True):
                if os.path.exists("images/gd-84d.png"): st.image("images/gd-84d.png")
                st.markdown("#### Dòng GD-84D-EX")
                st.markdown("- Máy đo đa khí cho nhà máy bán dẫn.\n- **Thay thế 4 máy cũ thành 1 máy** (Tiết kiệm 1/4 chi phí).\n- Hỗ trợ cấp nguồn và mạng qua cổng PoE.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gd-84d&post_type=any", use_container_width=True)

            with st.container(border=True):
                if os.path.exists("images/gd-d58.png"): st.image("images/gd-d58.png")
                st.markdown("#### Dòng GD-D58 & SD-D58")
                st.markdown("- Máy đo kiểu bơm hút chống cháy nổ.\n- Cấu trúc siêu bền bỉ, an toàn tuyệt đối ngay cả trong bầu không khí chứa Hydro.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=gd-d58&post_type=any", use_container_width=True)

            with st.container(border=True):
                if os.path.exists("images/gd-a2400.png"): st.image("images/gd-a2400.png")
                st.markdown("#### GD-A2400 / SD-2500 Series")
                st.markdown("- Chuyên dụng cho ống khói, lò đốt.\n- Có **thanh dài thọc sâu (250mm)** trực tiếp vào ống dẫn để lấy mẫu ở tâm dòng chảy.\n- Chịu nhiệt độ khắc nghiệt tới 160°C.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://product.rikenkeiki.co.jp/products/113-GD-A2400.html", use_container_width=True)

        # 3. MÁY PHÂN TÍCH & DÂN DỤNG
        st.markdown('<div class="branch-title branch-title-fixed">3. Máy phân tích đặc thù & Dùng trong nhà (Analyzers & Indoor)</div>', unsafe_allow_html=True)
        col_f5, col_f6 = st.columns(2, gap="medium")
        
        with col_f5:
            with st.container(border=True):
                if os.path.exists("images/600-series.png"): st.image("images/600-series.png")
                st.markdown("#### Dòng 600 Series (OX, EC, RI)")
                st.markdown("- Thiết kế siêu gọn nhẹ dùng cho văn phòng/trong nhà.\n- Màn hình 3 màu dễ nhìn, linh hoạt nguồn cấp (Điện AC, DC hoặc dùng Pin khô lên tới 1 năm).\n- Riêng OX-600 có cảm biến sửa lỗi áp suất.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=600-series&post_type=any", use_container_width=True)

            with st.container(border=True):
                if os.path.exists("images/fp-300.png"): st.image("images/fp-300.png")
                st.markdown("#### Dòng FP-300 / FP-301")
                st.markdown("- Dùng công nghệ **cuộn băng (tape)** chuyên dụng để đo khí độc nồng độ siêu nhỏ trong phòng sạch.\n- Có chức năng hiển thị lượng băng còn lại và cảnh báo sắp hết.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=fp-300&post_type=any", use_container_width=True)

        with col_f6:
            with st.container(border=True):
                if os.path.exists("images/fi-900.png"): st.image("images/fi-900.png")
                st.markdown("#### FI-900 / FI-915")
                st.markdown("- Máy phân tích **Giao thoa quang học**.\n- Đo cực kỳ ổn định, không cần thời gian khởi động (warm-up).\n- Cảm biến không bị suy giảm độ nhạy do nhiễm độc hóa chất silicon.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=fi-900&post_type=any", use_container_width=True)

            with st.container(border=True):
                if os.path.exists("images/ohc-800.png"): st.image("images/ohc-800.png")
                st.markdown("#### OHC-800 (Nhiệt lượng kế)")
                st.markdown("- Chuyên ngành khí thiên nhiên chống cháy nổ.\n- Đo trực tiếp và liên tục giá trị **Nhiệt lượng (Calorific)** và **Trọng lượng riêng (Density)**.")
                st.link_button("🔍 Tra cứu trên Riken Viet", "https://rikenviet.vn/?s=ohc-800&post_type=any", use_container_width=True)
# ---------------- TRANG 4: TIÊU CHUẨN & THUẬT NGỮ ----------------
elif app_mode == "📖 Tiêu Chuẩn & Thuật Ngữ":
    st.title("📖 Từ Điển: Tiêu Chuẩn & Thuật Ngữ Kỹ Thuật")
   
    tab_std, tab_expo = st.tabs(["🛡️ Tiêu Chuẩn Chống Cháy Nổ & An Toàn", "⚠️ Giới Hạn Phơi Nhiễm Khí Độc"])

    with tab_std:
        st.subheader("Nhóm 1: Các tiêu chuẩn chống cháy nổ theo khu vực địa lý")
        st.markdown("Bất kỳ thiết bị nào mang vào môi trường nguy hiểm đều tuyệt đối không được phát ra tia lửa điện. Quá trình kiểm tra khả năng này sinh ra các tiêu chuẩn sau:")
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            with st.container(border=True):
                st.markdown("#### 🇪🇺 ATEX (Của Châu Âu)")
                st.markdown("**Nó là gì?** Viết tắt của *ATmosphères EXplosibles* (Bầu không khí dễ nổ).\n\n**Đặc điểm:** Đây là **Đạo luật bắt buộc** của Liên minh Châu Âu (EU). Bất kỳ máy móc nào muốn được bán và lắp đặt tại khu vực nguy hiểm ở Châu Âu đều phải có chứng chỉ này.\n\n**Nhận diện:** Biểu tượng hình lục giác màu vàng, có chữ 'Ex' bên trong.")
            
            with st.container(border=True):
                st.markdown("#### 🇺🇸 UL, FM, CSA (Của Bắc Mỹ)")
                st.markdown("Mỹ và Canada không dùng hệ ATEX/IECEx mà có luật riêng (phân loại Class/Division thay vì Zone).\n\n- **UL (Underwriters Laboratories):** Công ty kiểm định lớn nhất Mỹ. 'UL Listed' là bảo chứng vàng tại thị trường Mỹ.\n- **FM (Factory Mutual):** Thiết bị có dấu 'FM Approved' đã trải qua các bài test cực kỳ khắc nghiệt.\n- **CSA:** Tiêu chuẩn tương đương nhưng dành cho Canada.")

        with col2:
            with st.container(border=True):
                st.markdown("#### 🌍 IECEx (Toàn cầu)")
                st.markdown("**Nó là gì?** Hệ thống chứng nhận của Ủy ban Kỹ thuật Điện Quốc tế (IEC).\n\n**Đặc điểm:** Được lập ra với tham vọng trở thành **Tiêu chuẩn Quốc tế chung**. Rất nhiều quốc gia ngoài EU (Úc, Châu Á, Trung Đông) chấp nhận IECEx.\n\n**Sự khác biệt:** ATEX mang tính chất *pháp lý khu vực*, còn IECEx mang tính chất *kỹ thuật toàn cầu*. Máy Riken Keiki thường làm luôn cả 2 chứng chỉ này cùng lúc.")
            
        st.markdown("---")
        
        col3, col4 = st.columns(2, gap="large")
        with col3:
            st.subheader("Nhóm 2: Tiêu chuẩn hàng hải")
            with st.container(border=True):
                st.markdown("#### ⚓ MED (Marine Equipment Directive)")
                st.markdown("**Nó là gì?** Chỉ thị Thiết bị Hàng hải của Châu Âu.\n\n**Giải thích:** Môi trường tàu biển rất khắc nghiệt (muối mặn, rung lắc). Máy dùng tốt trên đất liền chưa chắc mang lên tàu đã thọ được. Máy đo khí muốn lắp trên tàu thủy quốc tế phải đạt chứng chỉ MED.\n\n**Nhận diện:** Biểu tượng **Bánh lái tàu (Wheelmark)**.")

        with col4:
            st.subheader("Nhóm 3: Chứng chỉ Độ tin cậy hệ thống")
            with st.container(border=True):
                st.markdown("#### 🛡️ SIL (Safety Integrity Level)")
                st.markdown("**Nó là gì?** Mức độ Toàn vẹn An toàn.\n\n**Giải thích:** SIL không đánh giá việc chống cháy nổ, mà chấm điểm **SỰ ĐÁNG TIN CẬY**. Khi khí xì ra, xác suất máy 'bị đơ' không báo động là bao nhiêu? SIL chia từ 1 đến 4 (Càng cao càng xịn).\n- **SIL 2:** Rất phổ biến, xác suất lỗi cực thấp (SD-3 đạt SIL 2).\n- **SIL 3:** Siêu an toàn, thường phải chạy 2 máy song song.\n- **SIL 4:** Dành cho điện hạt nhân, tàu vũ trụ.")
                
        
    with tab_expo:
        st.subheader("Nhóm Thuật ngữ Phơi nhiễm Khí độc")
        st.markdown("Khí độc không giết người ngay mà tích tụ qua đường hô hấp. Do đó, các tiêu chuẩn an toàn đặt ra các mức báo động dựa trên thời gian tiếp xúc.")
        
        col5, col6 = st.columns(2, gap="large")
        
        with col5:
            with st.container(border=True):
                st.markdown("#### ⏳ TWA (Time-Weighted Average)")
                st.markdown("**Trung bình gia quyền theo thời gian.**\n\nĐây là nồng độ khí độc trung bình mà một người lao động có thể tiếp xúc liên tục trong một ca làm việc tiêu chuẩn (8 giờ/ngày, 40 giờ/tuần) mà không gặp tác dụng phụ có hại nào. Thường được dùng làm mức **Báo động 1 (Alarm 1)** trên máy đo khí.")
            
            with st.container(border=True):
                st.markdown("#### ⏱️ STEL (Short-Term Exposure Limit)")
                st.markdown("**Giới hạn phơi nhiễm ngắn hạn.**\n\nLà nồng độ tối đa mà người lao động có thể chịu đựng trong một khoảng thời gian ngắn (thường là **15 phút**), tối đa 4 lần/ngày. Thường được dùng làm mức **Báo động 2 (Alarm 2)**.")

        with col6:
            with st.container(border=True):
                st.markdown("#### ☠️ IDLH (Immediately Dangerous to Life or Health)")
                st.markdown("**Nguy hiểm tức thời đến tính mạng hoặc sức khỏe.**\n\nĐây là mức nồng độ khí độc cực kỳ nguy hiểm. Môi trường đạt ngưỡng IDLH yêu cầu người lao động phải sơ tán khẩn cấp hoặc phải đeo mặt nạ dưỡng khí độc lập để sinh tồn.")
            
            with st.container(border=True):
                st.markdown("#### 📏 TLV (Threshold Limit Value)")
                st.markdown("**Giá trị giới hạn ngưỡng.**\n\nMột thuật ngữ chung (do hiệp hội ACGIH của Mỹ ban hành) chỉ nồng độ của một chất trong không khí mà hầu hết người lao động có thể tiếp xúc hàng ngày mà không bị ảnh hưởng xấu. TWA và STEL chính là 2 loại của TLV.")
