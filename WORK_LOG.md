# AptisKey – Work Log
> Cập nhật lần cuối: 2026-07-20 22:05 (GMT+7)

---

## ✅ Công việc đã hoàn thành

### 1. Khởi động Backend Server ✅
- Chạy `python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload` từ thư mục `backend/`
- Server khởi động thành công, không có lỗi

### 2. Sửa role admin ✅
- `admin@aptiskey.com` đã có `role: "admin"`

### 3. Fix FutureWarning – Migrate google.generativeai → google.genai ✅
- `compat.py` và `grader.py` đã dùng `from google import genai`
- `requirements.txt` → `google-genai>=1.0.0`
- Package `google-genai==2.12.1` đã cài

### 4. Sửa lỗi bcrypt (Python 3.12) ✅
- Thay thế thư viện `passlib` bằng việc sử dụng trực tiếp `bcrypt` để băm và so khớp mật khẩu trong `security.py`.
- Khắc phục triệt để lỗi `ValueError: Invalid salt` khi đăng nhập hoặc đăng ký trên Python 3.12.

### 5. Phát triển tính năng Lịch sử làm bài (Exam History) & Xác minh nộp bài ✅
- **Backend**:
  - Bổ sung `test_title` và `test_skill` vào schema `ResultDetail`.
  - Cập nhật API `GET /api/results` để trả về thêm thông tin tên đề và kỹ năng (join từ bảng `tests`).
  - Thêm API mới `GET /api/results/{result_id}` để lấy chi tiết kết quả bài thi cụ thể của học viên.
  - Thêm API `POST /api/compat/save-result` để hỗ trợ frontend gửi lưu điểm số, band, nhận xét AI trực tiếp sau khi hoàn thành bài thi.
- **Frontend**:
  - Tạo trang mới `history.html` đồng bộ theo thiết kế **Neumorphism (Soft UI)** với đầy đủ các bộ lọc kỹ năng, thanh tìm kiếm theo tên đề, phân trang và stats cards tổng quan.
  - Tích hợp modal xem chi tiết kết quả (điểm, band, thời gian, nhận xét chi tiết của AI và đáp án đã chọn).
  - Thêm liên kết "Lịch sử làm bài" vào sidebar menu của tất cả các file HTML chính.
- **Xác minh**: Chạy mô phỏng nộp bài thi Reading Test #01 thành công. Kết quả lưu vào DB và hiển thị chính xác trên giao diện lịch sử của học viên.

### 6. Fix lỗi Đăng nhập lặp lại (Redirect Loop) & Lưu phiên ở trang làm đề tĩnh ✅
- **Vấn đề**: API `/auth/login` cũ không đặt cookie khiến các trang làm đề tĩnh không đính kèm được token và bị lỗi 401. Đồng thời trang chủ bị 401 thì redirect về trang đăng nhập, trang đăng nhập thấy token trong localStorage lại tự động redirect lại trang chủ, tạo ra vòng lặp vô hạn.
- **Giải pháp**:
  - Cập nhật `/auth/login` để đặt thêm HttpOnly cookie `access_token` giúp các trang tĩnh tự động gửi thông tin xác thực.
  - Cập nhật `common.js` và `auth.html` để đính kèm `credentials: 'include'` khi fetch, đồng thời xóa sạch token cũ trong localStorage khi nhận mã lỗi 401 để phá vỡ vòng lặp redirect.

### 7. Tích hợp tự động lưu kết quả thi từ Giao diện làm bài ✅
- Bổ sung hàm tự động gửi lưu kết quả vào file JS làm bài:
  - **Grammar** trong `grammar_test.js`.
  - **Reading** trong `readingtest.js`.
  - **Listening** trong `listening_test.js`.
  - **Writing** trong `writing_test.js`.

### 8. Áp dụng kỹ thuật Cache Busting ✅
- Chạy script Python tự động thêm phiên bản `?v=1.0.1` vào các file script tĩnh JS (`common.js`, `readingtest.js`, `listening_test.js`, `grammar_test.js`, `writing_test.js`) trên toàn bộ **88 file HTML** trong `crawled_data/`. Khắc phục triệt để lỗi do trình duyệt của người dùng cache file JS cũ, giúp hệ thống luôn tải phiên bản logic nộp bài mới nhất.

### 9. Xóa thông tin liên hệ Admin cá nhân ✅
- Xóa toàn bộ số điện thoại Zalo `0889 489 814` và link Facebook Admin tại tất cả 12 trang HTML chính trong thư mục `crawled_data/` để bảo mật thông tin cá nhân. Thay thế modal bằng nội dung thông báo nâng cấp kênh hỗ trợ.

### 10. Phát triển trang Quản trị hệ thống (Admin Dashboard) ✅
- **Backend API dành riêng cho Admin**:
  - `GET /api/admin/users`: Lấy danh sách toàn bộ học viên đăng ký trên hệ thống.
  - `PUT /api/admin/users/{user_id}/vip`: Gia hạn, đặt thời hạn, hoặc hủy VIP của học viên bất kỳ.
  - `GET /api/admin/results`: Lấy danh sách lịch sử nộp bài thi của tất cả các tài khoản trên hệ thống.
  - `GET /api/admin/users/{user_id}/results`: Xem lịch sử nộp bài của một học viên cụ thể.
  - Bảo mật phân quyền: Tích hợp dependency `get_current_admin` chặn 100% tài khoản học viên thường truy cập (`403 Forbidden`).
- **Giao diện quản trị Neumorphic (`admin_dashboard.html`)**:
  - Giao diện tab: Quản lý danh sách học viên (Sửa VIP nhanh, Xem lịch sử làm bài riêng) và Theo dõi lịch sử làm bài chung của toàn hệ thống (Xem lại chi tiết bài làm, nhận xét của AI).
  - Dynamic Sidebar Menu: Tự động chèn liên kết "Quản trị hệ thống" vào sidebar của tất cả các trang khi tài khoản đăng nhập là Admin.
  - Hotfix Layout: Khắc phục lỗi sidebar đè lên nội dung và khoảng trắng ở trên đầu bằng cách điều chỉnh cơ chế hiển thị sang class `.d-none` của Bootstrap 5 thay thế cho can thiệp style `display` thủ công, bảo vệ nguyên trạng CSS grid/flexbox của AdminLTE.

### 11. Sửa lỗi tăng giảm âm lượng phần ghi âm Listening ✅
- Cập nhật các file JS làm bài Listening (`listening_test.js`, `listening_question1_13.js`, `listening_question14.js`, `listening_question15.js`, `listening_question16_17.js`).
- Đấu nối sự kiện slider âm lượng (`input[type="range"]`) trực tiếp với thuộc tính `audio.volume` của trình phát bài nghe.
- Cập nhật biểu tượng loa linh hoạt theo mức âm lượng và khôi phục trạng thái khi Mute / Unmute.

### 12. Sửa cấu hình chạy ứng dụng qua Docker ✅
- Cập nhật `Dockerfile` & `docker-compose.yml` để mount đầy đủ ứng dụng và phơi cổng `8001`.
- Thêm tệp `.dockerignore` giúp tối ưu quá trình đóng gói container.

### 13. Hoàn thiện tính năng chấm điểm Speaking bằng Gemini AI ✅
- **Backend (`POST /ask-speaking`)**:
  - Thêm router `/ask-speaking` trong `compat.py` hỗ trợ chấm điểm Speaking theo chuẩn 4 tiêu chí British Council (Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Content & Task Fulfilment).
  - Tích hợp SDK `google-genai` với `GEMINI_API_KEY` có sẵn trong `.env`, trả về HTML đánh giá chi tiết kèm band điểm ước tính.
- **Frontend (`speaking_question1_practice.js` → `speaking_question4_practice.js`)**:
  - Cập nhật hàm `scoreAnswer()` truyền tham số `part`, `question`, `userAnswer`, `refAnswer` tới `/ask-speaking`.
  - Nâng cấp Modal hiển thị kết quả trong 4 trang HTML Part 1 - 4 (`modal-lg`, gradient header, cuộn scroll 70vh, hiển thị spinner loading khi đang chấm bài).

### 14. Chuẩn hóa tiêu đề các trang HTML giao diện học viên ✅
- Cập nhật các thẻ `<title>` và meta description loại bỏ cụm từ không cần thiết trên 11 trang chính thuộc `crawled_data/`.

---

## 📋 Kế hoạch công việc tiếp theo

### Ưu tiên cao
1. **Cấu hình API Key thật:** Thêm `GEMINI_API_KEY` và `PAYOS_API_KEY` vào file `.env` khi triển khai thực tế.

### Ưu tiên trung bình
2. **Security audit:** Kiểm tra CORS nâng cao, thời hạn hết hạn JWT, giới hạn rate limit.
3. **Email flow:** Test luồng gửi mail đặt lại mật khẩu (`POST /auth/forgot-password`) khi cấu hình Resend API key.

### Ưu tiên thấp
4. **Dọn dẹp mã nguồn:** Xóa các script test tạm thời trong `scratch/` (`db_check.py`, `test_webhook.py`, `test_vip.py`, `test_results_api.py`, `test_save_result.py`).

---

## 📌 Ghi chú kỹ thuật

- **Backend port:** 8001
- **Database:** SQLite tại `backend/aptispro_dev.db`
- **Lệnh chạy server:** `python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload`
- **Cơ chế xác thực:** JWT Token (lưu ở `localStorage`) & HttpOnly Cookie `access_token` (để hỗ trợ các trang luyện tập tĩnh).
- **Admin account:** `admin@aptiskey.com` / `admin123`
- **Học viên test account:** `apitest@aptispro.com` / `test123`
- **Google Gemini SDK:** `google-genai==2.12.1` (API mới)
- **Tổng số đề thi:** 78 đề thi có sẵn trong DB.
