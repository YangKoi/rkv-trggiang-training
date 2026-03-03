import streamlit as st

# Cấu hình trang
st.set_page_config(page_title="Riken Viet - Đào tạo nội bộ", page_icon="🎓", layout="centered")

# Header
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Riken_Keiki_logo.svg/2560px-Riken_Keiki_logo.svg.png", width=200)
st.title("🎓 Cổng Đào Tạo Năng Lực & Hội Nhập")
st.markdown("---")

st.markdown("""
**Xin chào thành viên mới của Riken Viet!** 👋

Để bắt đầu hành trình của mình, bạn vui lòng dành ít phút theo dõi video giới thiệu về lịch sử, năng lực lõi và các giải pháp an toàn khí mà công ty chúng ta đang cung cấp.
""")

# Chiếu Video (Thay link YouTube của bạn vào đây)
VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Ví dụ link YouTube
st.video(VIDEO_URL)

st.markdown("---")

# Thêm tính năng tương tác của Cổng đào tạo
st.subheader("📋 Xác nhận hoàn thành nội dung")

# Checkbox xác nhận
agree = st.checkbox("Tôi đã xem hết video và nắm rõ năng lực cốt lõi của Riken Viet.")

if agree:
    st.success("✅ Cảm ơn bạn! Xác nhận của bạn đã được ghi nhận vào hệ thống. Chúc bạn một ngày làm việc tràn đầy năng lượng!")
    st.balloons() # Hiệu ứng bóng bay chúc mừng
    
    # Nút tải tài liệu đính kèm (Ví dụ: Sổ tay nhân viên)
    # st.download_button(label="📥 Tải Sổ tay nhân viên (PDF)", data="Noi dung file", file_name="SoTay_RikenViet.pdf")
