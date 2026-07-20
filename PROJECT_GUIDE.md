# Tài liệu Dự án AptisKey – Hướng dẫn Nhà phát triển (Developer Guide)

> [!NOTE]
> Tài liệu này được biên soạn để cung cấp cái nhìn tổng quan, cấu trúc mã nguồn, quy ước thiết kế và cách tích hợp backend/frontend của dự án **AptisKey** (Hệ thống ôn luyện thi Aptis thông minh). 
> Hãy đọc kỹ file này trước khi thực hiện bất kỳ chỉnh sửa nào.

---

## 1. Cấu trúc Thư mục Dự án

```text
aptiskey/
├── backend/                  # Mã nguồn FastAPI Backend
│   ├── app/
│   │   ├── core/             # Cấu hình hệ thống, DB (SQLAlchemy), Security (JWT)
│   │   ├── models/           # Các Model SQLAlchemy (User, Test, Question, Payment,...)
│   │   ├── schemas/          # Schema Pydantic dùng để validate dữ liệu vào/ra
│   │   ├── routers/          # FastAPI Routes (auth, exam, payment, compat,...)
│   │   ├── services/         # Logic nghiệp vụ (AI Grader chấm điểm bằng Gemini API)
│   │   └── main.py           # File khởi chạy chính của FastAPI app
│   ├── requirements.txt      # Thư viện Python phụ thuộc
│   └── aptispro_dev.db       # Database SQLite môi trường Development
│
├── frontend/                 # Giao diện tĩnh (HTML/CSS/JS) hiện đại
│   └── auth.html             # Giao diện Đăng ký / Đăng nhập Neumorphic chuẩn
│
├── crawled_data/             # Dữ liệu đề thi, bài đọc/nghe tĩnh được convert từ hệ thống cũ
│   ├── css/                  # Chứa neumorphism.css và stylesheets khác
│   ├── js/                   # Các script xử lý giao diện tĩnh
│   ├── images/               # Hình ảnh, icon của giao diện
│   └── index.html / home.html# Trang chủ của hệ thống
│
└── các script hỗ trợ/         # rebrand_platform.py, crawl_questions_data.py, scraper.py,...
```

---

## 2. Quy ước Thiết kế Giao diện (Design System - Neumorphism)

Hệ thống sử dụng phong cách **Neumorphism (Soft UI)** với bảng màu sáng nhẹ, tạo cảm giác nổi khối mịn (3D soft) dựa trên đổ bóng kép (double shadows). Tất cả các giao diện mới (như `auth.html`) hoặc nâng cấp cần tuân thủ nghiêm ngặt các tokens cấu hình từ [neumorphism.css](file:///g:/My%20Drive/code/aptiskey/crawled_data/css/neumorphism.css):

### Thiết lập màu và Bóng (Neumorphic Shadows)
- **Màu nền (Background):** `#e0e5ec` (màu xám xanh ấm).
- **Shadow Ra (Outset):** `6px 6px 16px #a3b1c6, -6px -6px 16px #ffffff` (tạo khối nổi).
- **Shadow Vào (Inset):** `inset 4px 4px 10px #a3b1c6, inset -4px -4px 10px #ffffff` (cho input hoặc trạng thái active/pressed).
- **Màu Accent:** Xanh dương `#4f8ef7` và Tím Indigo `#6c63ff` (dùng cho các gradient nút bấm, chỉ thị trạng thái).
- **Font chữ:** `Nunito` làm chủ đạo (`font-weight: 700` cho tiêu đề, nút bấm).

### Code mẫu Neumorphic CSS chuẩn:
```css
/* Khối nổi */
.nm-card {
  background-color: #e0e5ec;
  box-shadow: 6px 6px 16px #a3b1c6, -6px -6px 16px #ffffff;
  border-radius: 20px;
}

/* Trường nhập liệu chìm */
.nm-input {
  background-color: #e0e5ec;
  box-shadow: inset 4px 4px 10px #a3b1c6, inset -4px -4px 10px #ffffff;
  border: none;
  outline: none;
}
```

---

## 3. Kiến trúc Backend & API Integrations

### Database (SQLite)
Hệ thống sử dụng **SQLAlchemy ORM** để tương tác với cơ sở dữ liệu. 
- File database: `aptispro_dev.db` nằm ở `/backend/`.
- Tự động tạo bảng: Được khai báo ở `backend/app/main.py` qua `Base.metadata.create_all(bind=engine)`.

### Authentication (JWT)
- **Đăng ký:** `POST /auth/register` nhận JSON `UserRegister` (validate mật khẩu $\ge$ 8 ký tự).
- **Đăng nhập:** `POST /auth/login` nhận dữ liệu kiểu `form-urlencoded` (`username`, `password`), trả về JWT Token và thời hạn (mặc định 7 ngày).
- **Xác thực:** Header HTTP sử dụng token dạng Bearer: `Authorization: Bearer <token>`.
- Token được lưu ở Client trong `localStorage` dưới key `ak_token`.

### Tích hợp Trí tuệ nhân tạo (Gemini AI Grader)
Backend tích hợp model **Gemini (mặc định: `gemini-2.0-flash`)** để chấm điểm tự động cho các câu hỏi tự luận (Subjective):
- **Reading, Listening, Grammar:** So khớp trực tiếp đáp án (Objective).
- **Writing, Speaking:** Gửi đề bài và câu trả lời của học viên qua Gemini API kèm prompt chỉ dẫn chấm điểm theo tiêu chí thi chuẩn của British Council. Trả về điểm số quy đổi (Band A1 - C) kèm nhận xét chi tiết (Feedback).
- Cấu hình API key tại biến môi trường `GEMINI_API_KEY` ở file `backend/.env`.

---

## 4. Quy ước Phát triển dành cho Model / Trợ lý AI

Khi làm việc với dự án này, hãy đảm bảo tuân thủ các nguyên tắc sau:
1. **Không thay đổi cấu trúc gốc của DB** trừ khi có yêu cầu rõ ràng. Nếu cần sửa DB, sử dụng Alembic migrations (nếu đã cấu hình) hoặc chỉnh sửa file model tương ứng trong `backend/app/models/`.
2. **Giao diện Web:**
   - Sử dụng HTML thuần + Vanilla CSS + Vanilla JS để tối ưu hóa tính độc lập và nhẹ nhàng của các trang tĩnh.
   - Luôn sử dụng icon từ **Bootstrap Icons** thay vì dùng emoji thô sơ để giữ tính đồng nhất với giao diện AdminLTE & Neumorphism sẵn có.
   - Đảm bảo tính tương thích responsive trên Mobile.
3. **Gọi API:**
   - API Client luôn gọi tới `http://localhost:8001` (qua biến cấu hình `API_BASE` trong code frontend).
   - Hãy xử lý triệt để các trạng thái loading, báo lỗi cụ thể qua hệ thống **Toast** và thông báo lỗi ngay dưới chân của trường nhập liệu (field error).
