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
        "☣️ Kiến Thức: Phân Loại Khí",
        "📟 Phân Loại Thiết Bị"
    ])
    st.markdown("---")
    st.info("💡 **Gợi ý:** Hãy hoàn thành đọc hiểu các phần lý thuyết trước khi làm bài kiểm tra hội nhập nhé!")

# ==========================================
# NỘI DUNG TỪNG TRANG
# ==========================================

# ---------------- TRANG 1: ĐÀO TẠO HỘI NHẬP ----------------
if app_mode == "🎓 Cổng Đào Tạo Hội Nhập":
    # MÃ NGUỒN TRANG 1 (GIỮ NGUYÊN)
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
    # MÃ CSS TRANG 2 GIỮ NGUYÊN 
    st.markdown("""
    <style>
    @keyframes pulse-red { 0% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 78, 80, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 78, 80, 0); } }
    .alert-box { background: linear-gradient(45deg, #ff4e50, #f9d423); padding: 15px; border-radius: 8px; color: white; animation: pulse-red 2s infinite; margin-bottom: 15px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .toxic-glow { background-color: #1a1a1a; padding: 15px; border-radius: 8px; border-left: 5px solid #a8ff78; color: #a8ff78; margin-bottom: 15px; font-weight: bold; }
    .special-glow { background: linear-gradient(90deg, #2c003e, #4c0070); padding: 15px; border-radius: 8px; border-left: 5px solid #d400ff; color: #f8e5ff; margin-bottom: 15px; font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    .ppm-container { width: 100%; background-color: #e9ecef; border-radius: 5px; margin: 10px 0 25px 0; border: 1px solid #ccc; position: relative; height: 35px; box-shadow: inset 0 1px 3px rgba(0,0,0,.1); }
    .ppm-bar { height: 100%; border-radius: 5px 0 0 5px; display: flex; align-items: center; justify-content: flex-end; padding-right: 5px; color: white; font-weight: bold; font-size: 12px; }
    .ppb-bar { height: 100%; border-radius: 5px; display: flex; align-items: center; justify-content: flex-start; padding-left: 10px; color: white; font-weight: bold; font-size: 13px; background: linear-gradient(90deg, #d400ff, #8a2be2); box-shadow: 0 0 10px #d400ff; }
    @keyframes blink { 50% { opacity: 0.5; } }
    .oxy-bg { background-color: #222; border-radius: 6px; width: 100%; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .oxy-bar { height: 32px; border-radius: 6px; color: white; text-align: right; padding-right: 15px; font-weight: bold; line-height: 32px; font-size: 14px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); transition: width 1s ease-in-out; }
    .danger-blink { animation: blink 1s linear infinite; }
    .custom-table { width: 100%; min-width: 350px; border-collapse: collapse; margin-top: 5px; margin-bottom: 15px; background-color: #ffffff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
    .custom-table th { background-color: #0056b3; color: #ffffff; padding: 12px; text-align: center; font-size: 15px; white-space: nowrap; border-bottom: 2px solid #004494; }
    .custom-table td { padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: center; font-size: 14px; color: #212529 !important; } 
    .custom-table tr:nth-child(even) td { background-color: #f8f9fa; }
    .custom-table tr:hover td { background-color: #e2e6ea; }
    .highlight-red { color: #dc3545 !important; font-weight: bold; }
    .scroll-wrapper { width: 100%; overflow-x: auto; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)
    st.title("☣️ Kiến Thức Cơ Bản Về Các Loại Khí Nguy Hiểm")
    st.markdown("Trong môi trường công nghiệp, rủi ro về khí là những **'Kẻ thù vô hình'**.")
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 1. Khí dễ cháy", "☠️ 2. Khí độc", "💨 3. Thiếu oxy & Ngạt khí", "🏥 4. Y tế & Khử trùng"])

    with tab1:
        st.header("🔥 Khí dễ cháy (Combustible gases)")
        st.markdown('<div class="alert-box"><b>⚠️ ĐỊNH NGHĨA:</b> Khí có thể gây cháy hoặc nổ nếu hòa trộn với oxy ở nồng độ nhất định và gặp nguồn cháy.</div>', unsafe_allow_html=True)
        html_lel_uel = """<div style="width: 100%; background-color: #f1f3f4; border-radius: 8px; position: relative; height: 40px; margin-bottom: 30px; display: flex; text-align: center; color: white; font-weight: bold; line-height: 40px; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="width: 25%; background-color: #28a745; border-radius: 8px 0 0 8px;">Quá loãng (Chưa thể cháy)</div><div style="width: 45%; background-color: #dc3545; position: relative;"><span style="position: absolute; top: -30px; left: 0; color: #dc3545; font-size: 16px;">▼ LEL</span>🔥 VÙNG CHÁY NỔ (NGUY HIỂM) 🔥<span style="position: absolute; top: -30px; right: 0; color: #dc3545; font-size: 16px;">UEL ▼</span></div><div style="width: 30%; background-color: #ffc107; border-radius: 0 8px 8px 0; color: #333;">Quá đặc (Thiếu Oxy)</div></div>"""
        st.markdown(html_lel_uel, unsafe_allow_html=True)
        col1, col2 = st.columns([1.2, 1], gap="medium")
        with col1:
            gas_table_html = """<div class="scroll-wrapper"><table class="custom-table"><tr><th>Tên Khí (Công thức)</th><th>LEL (%)</th><th>UEL (%)</th></tr><tr><td><b>Methane (CH4)</b></td><td class="highlight-red">5.0</td><td>15.0</td></tr><tr><td><b>Hydrogen (H2)</b></td><td class="highlight-red">4.0</td><td>75.6</td></tr><tr><td><b>Propane (C3H8)</b></td><td class="highlight-red">2.1</td><td>9.5</td></tr><tr><td><b>Iso-butane (i-C4H10)</b></td><td class="highlight-red">1.8</td><td>8.4</td></tr><tr><td><b>Carbon Monoxide (CO)</b></td><td class="highlight-red">12.5</td><td>74.0</td></tr></table></div>"""
            st.markdown(gas_table_html, unsafe_allow_html=True)
        with col2:
            st.markdown("""<div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #0056b3; height: 100%;"><h4 style="color: #0056b3; margin-top: 0;">💡 Tiêu chuẩn An toàn</h4><p style="color: #333; font-size: 15px;">Điểm báo động (Alarm) <b>KHÔNG ĐƯỢC PHÉP</b> vượt quá <b>1/4 (25%) mức LEL</b>.<br><br>Ví dụ: Methane (CH4) có LEL = 5.0%. Máy Riken Keiki sẽ báo động ngay khi đạt <b>1.25%</b> thể tích.</p></div>""", unsafe_allow_html=True)

    with tab2:
        st.header("☠️ Khí độc (Toxic gases)")
        st.markdown('<div class="toxic-glow">☢️ ĐỊNH NGHĨA: Gây hại cho sức khỏe con người. Đánh giá qua "nồng độ cho phép".</div>', unsafe_allow_html=True)
        col_conv1, col_conv2 = st.columns([1.2, 1], gap="medium")
        with col_conv1:
            st.markdown("### 🔄 Quy đổi % Thể tích (%vol) sang Phần triệu (PPM)")
            conversion_html = """<div class="scroll-wrapper"><table class="custom-table"><tr><th>% Thể tích (% vol)</th><th>Phần triệu (ppm)</th><th>Ví dụ</th></tr><tr><td class="highlight-red">1 %</td><td class="highlight-red">10,000 ppm</td><td>Chết người</td></tr><tr><td>0.1 %</td><td>1,000 ppm</td><td>Báo động nghiêm trọng</td></tr><tr><td>0.01 %</td><td>100 ppm</td><td>Ngưỡng phơi nhiễm</td></tr><tr><td>0.001 %</td><td>10 ppm</td><td>Mức báo động (H2S)</td></tr></table></div>"""
            st.markdown(conversion_html, unsafe_allow_html=True)
        with col_conv2:
            st.markdown("### 🔬 Trực quan tỷ lệ giết người:")
            html_ppm = """<div class="ppm-container"><div class="ppm-bar" style="width: 1.28%; background-color: #dc3545;">1.28%</div><span style="position:absolute; left: 2%; top: 7px; color: #333; font-weight: bold;">CO: 12,800 ppm (Tử vong trong 1-3 phút)</span></div><div class="ppm-container"><div class="ppm-bar" style="width: 0.5%; background-color: #8b0000;">0.5%</div><span style="position:absolute; left: 1%; top: 7px; color: #333; font-weight: bold;">H2S: 5,000 ppm (Tử vong NGAY LẬP TỨC)</span></div>"""
            st.markdown(html_ppm, unsafe_allow_html=True)

    with tab3:
        st.header("💨 Tình trạng thiếu oxy và ngạt khí (Anoxia)")
        st.markdown("Tình trạng 'thiếu oxy' được xác định khi nồng độ oxy trong không khí **giảm xuống dưới 18%**.")
        html_oxy = """<div class="oxy-bg"><div class="oxy-bar" style="width: 100%; background: linear-gradient(90deg, #11998e, #38ef7d);">20.93% - BÌNH THƯỜNG</div></div><div class="oxy-bg"><div class="oxy-bar" style="width: 86%; background: linear-gradient(90deg, #f2c94c, #f2994a); color: #000;">Dưới 18% - THIẾU OXY</div></div><div class="oxy-bg"><div class="oxy-bar" style="width: 67%; background: linear-gradient(90deg, #e65c00, #F9D423);">16% ~ 12% - Thở gấp, buồn nôn</div></div><div class="oxy-bg"><div class="oxy-bar danger-blink" style="width: 15%; background: linear-gradient(90deg, #cb2d3e, #ef473a);">≤ 6% - TỬ VONG NGAY LẬP TỨC</div></div>"""
        st.markdown(html_oxy, unsafe_allow_html=True)

    with tab4:
        st.header("🏥 Khí đặc thù: Y tế, Khử trùng & Hun trùng")
        st.markdown('<div class="special-glow">☣️ CẢNH BÁO NGHIÊM NGẶT: Nhóm khí y tế/khử trùng có độc tính cực mạnh, giới hạn an toàn tính bằng ppb.</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1.2, 1], gap="large")
        with col1:
            st.markdown("### 1. Khí Khử trùng / Hun trùng (Fumigation)")
            st.write("VD: Phosphine (PH3) có giới hạn cho phép cực nhỏ là **0.05 ppm** (tương đương 50 ppb).")
            html_ppb = """<div class="ppm-container" style="height: 40px;"><div class="ppb-bar" style="width: 5%;">50 ppb (Báo động PH3)</div><span style="position:absolute; right: 10px; top: 10px; color: #777; font-size: 12px;">1 Tỷ hạt không khí</span></div>"""
            st.markdown(html_ppb, unsafe_allow_html=True)
        with col2:
            st.markdown("### 🛡️ Thiết bị đo chuyên dụng RIKEN KEIKI")
            st.markdown("""<div style="background-color: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 10px;"><h5 style="color: #d400ff; margin-top: 0;">📟 SP-230 (TYPE FUM)</h5><p style="font-size: 14px; color: #555; margin-bottom: 0;">Dò rò rỉ di động kiểu bơm hút. Hỗ trợ tới <b>7 loại khí khử trùng</b>.</p></div><div style="background-color: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px;"><h5 style="color: #d400ff; margin-top: 0;">📼 FP-300 / FP-301</h5><p style="font-size: 14px; color: #555; margin-bottom: 0;">Hệ thống phát hiện <b>siêu nhạy</b> bằng cassette, đo mức ppb chuyên cho PH3.</p></div>""", unsafe_allow_html=True)

# ---------------- TRANG 3: PHÂN LOẠI THIẾT BỊ (MỚI) ----------------
elif app_mode == "📟 Phân Loại Thiết Bị":
    st.markdown("""
    <style>
    .product-card {
        background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .product-card:hover {
        transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); border-color: #0056b3;
    }
    .product-title { color: #0056b3; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }
    .product-tag { display: inline-block; background-color: #e9ecef; color: #495057; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-right: 5px; margin-bottom: 8px; font-weight: bold;}
    .tag-blue { background-color: #cce5ff; color: #004085; }
    .tag-green { background-color: #d4edda; color: #155724; }
    .tag-red { background-color: #f8d7da; color: #721c24; }
    .tag-yellow { background-color: #fff3cd; color: #856404; }
    </style>
    """, unsafe_allow_html=True)

    st.title("📟 Showroom Sản Phẩm: Thiết Bị Đo Khí Cầm Tay")
    st.markdown("Thiết bị đo khí cầm tay (Portable) được chia thành 2 nhánh chính. Hãy cùng khám phá các dòng máy chiến lược của hãng RIKEN KEIKI nhé!")
    st.markdown("---")

    tab_diff, tab_pump, tab_fixed = st.tabs(["💨 1. Loại Khuếch tán (Diffusion)", "🧲 2. Loại Bơm hút (Pump Suction)", "🏭 3. Hệ thống Cố định (Fixed)"])

    with tab_diff:
        st.subheader("💨 Loại Khuếch Tán (Diffusion Type)")
        st.info("Đặc điểm: Không có bơm bên trong. Khí tự nhiên len lỏi vào cảm biến. Thiết kế siêu nhỏ gọn, nhẹ, tiết kiệm pin, thường kẹp trên cổ áo/mũ bảo hộ để giám sát liên tục vùng thở của kỹ sư.")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            if os.path.exists("gx-3r.png"): st.image("gx-3r.png", use_container_width=True)
            else: st.info("Hình ảnh: Cắt từ PDF lưu tên gx-3r.png")
            st.markdown('<div class="product-title">GX-3R</div>', unsafe_allow_html=True)
            st.markdown('<span class="product-tag tag-blue">4 Loại Khí</span> <span class="product-tag tag-green">Nhẹ nhất TG</span>', unsafe_allow_html=True)
            st.markdown("- Thiết kế siêu nhỏ gọn, không gây vướng víu.\n- Đo đồng thời: LEL, O2, H2S, CO.\n- Bảo hành cảm biến 3 năm.\n- Chống nước IP66/68.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_d2:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            if os.path.exists("gx-3r-pro.png"): st.image("gx-3r-pro.png", use_container_width=True)
            else: st.info("Hình ảnh: Cắt từ PDF lưu tên gx-3r-pro.png")
            st.markdown('<div class="product-title">GX-3R Pro</div>', unsafe_allow_html=True)
            st.markdown('<span class="product-tag tag-blue">5 Loại Khí</span> <span class="product-tag tag-red">Bluetooth</span>', unsafe_allow_html=True)
            st.markdown("- Dòng máy High-spec hỗ trợ Bluetooth.\n- Có thể đo thêm khí thứ 5 (CO2, SO2...).\n- Quản lý dữ liệu qua app điện thoại.\n- Chống nước IP66/68.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_d3:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            if os.path.exists("04-series.png"): st.image("04-series.png", use_container_width=True)
            else: st.info("Hình ảnh: Cắt từ PDF lưu tên 04-series.png")
            st.markdown('<div class="product-title">04 Series & GW-3</div>', unsafe_allow_html=True)
            st.markdown('<span class="product-tag tag-yellow">1-2 Loại Khí</span> <span class="product-tag tag-green">Đeo cổ tay</span>', unsafe_allow_html=True)
            st.markdown("- Máy đo đơn khí hoặc 2 khí (CO/H2S).\n- Cực kỳ nhẹ, có thể đeo như đồng hồ (GW-3).\n- Tuổi thọ pin siêu dài (hàng nghìn giờ).\n- Chống nước IP66/68.")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_pump:
        st.subheader("🧲 Loại Bơm Hút (Pump Suction Type)")
        st.warning("Đặc điểm: Tích hợp bơm hút mạnh mẽ bên trong. Kết hợp với ống nối dài để hút thử mẫu khí từ không gian hạn hẹp (hầm, cống, bồn chứa) trước khi kỹ sư bước vào.")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            if os.path.exists("gx-force.png"): st.image("gx-force.png", use_container_width=True)
            else: st.info("Hình ảnh: Cắt từ PDF lưu tên gx-force.png")
            st.markdown('<div class="product-title">GX-Force</div>', unsafe_allow_html=True)
            st.markdown('<span class="product-tag tag-blue">4 Loại Khí</span> <span class="product-tag tag-yellow">Pin 30 giờ</span>', unsafe_allow_html=True)
            st.markdown("- Máy bơm hút thế hệ mới gọn nhẹ (300g).\n- Hoạt động liên tục 30 tiếng, không lo hết pin.\n- Chịu va đập rơi từ độ cao 3 mét.\n- Chuyển đổi đo 27 loại khí cháy khác nhau.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_p2:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            if os.path.exists("gx-9000.png"): st.image("gx-9000.png", use_container_width=True)
            else: st.info("Hình ảnh: Cắt từ PDF lưu tên gx-9000.png")
            st.markdown('<div class="product-title">GX-9000 / SC-9000</div>', unsafe_allow_html=True)
            st.markdown('<span class="product-tag tag-red">Tối đa 6 Khí</span> <span class="product-tag tag-blue">Đa năng</span>', unsafe_allow_html=True)
            st.markdown("- Dòng cao cấp thay thế máy đo truyền thống.\n- SC-9000 đo được 3 loại khí độc (3-in-1).\n- Hỗ trợ Bluetooth và có ứng dụng quản lý.\n- Thiết kế cực kỳ hầm hố và bền bỉ.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_p3:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            if os.path.exists("gx-6000.png"): st.image("gx-6000.png", use_container_width=True)
            else: st.info("Hình ảnh: Cắt từ PDF lưu tên gx-6000.png")
            st.markdown('<div class="product-title">GX-6000 / GX-2012</div>', unsafe_allow_html=True)
            st.markdown('<span class="product-tag tag-red">Đo VOC</span> <span class="product-tag tag-green">Báo động lớn</span>', unsafe_allow_html=True)
            st.markdown("- GX-6000: Lý tưởng để đo hóa chất, VOC.\n- GX-2012: Dòng tiêu chuẩn huyền thoại.\n- Tích hợp chức năng đèn pin LED rọi sáng.\n- Nút bấm lớn dễ thao tác khi đeo găng tay.")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_fixed:
        st.subheader("🏭 Nhánh 2: Hệ thống Cố định (Sẽ cập nhật sau)")
        st.info("Trang này tạm thời tập trung hiển thị sâu cho các thiết bị cầm tay. Khi nào bạn có tài liệu của Fixed Systems, chúng ta sẽ xây dựng tiếp giao diện cho khu vực này nhé!")
