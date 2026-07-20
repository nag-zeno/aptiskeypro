# AptisKey – Hệ Thống Ôn Luyện Thi Aptis Thông Minh

AptisKey là một hệ thống ôn luyện thi Aptis toàn diện tích hợp Trí tuệ Nhân tạo (AI) giúp chấm điểm tự động các phần tự luận (Writing, Speaking) và hỗ trợ luyện tập trực tuyến các phần thi trắc nghiệm (Reading, Listening, Grammar). Giao diện người dùng được đồng bộ theo phong cách thiết kế hiện đại **Neumorphism (Soft UI)**.

---

## 🚀 Tính Năng Nổi Bật

1. **Luyện thi toàn diện 4 kỹ năng:**
   * **Nghe, Đọc, Ngữ pháp & Từ vựng:** So khớp đáp án tự động (Objective), trả về điểm số và phân loại trình độ tức thì.
   * **Viết & Nói:** Tích hợp **Google Gemini API** (`gemini-2.0-flash`) làm giám khảo ảo để chấm điểm theo tiêu chuẩn British Council, cung cấp điểm số quy đổi (Band A1 - C) kèm nhận xét chi tiết.
2. **Hệ thống VIP & Cổng thanh toán:**
   * Phân quyền bài thi VIP và thường.
   * Tích hợp cổng thanh toán **PayOS** và kích hoạt tài khoản VIP tự động thông qua Webhook.
3. **Thiết kế giao diện Neumorphism hiện đại:**
   * Giao diện sáng dịu, đổ bóng kép tạo khối mềm mịn, tăng trải nghiệm người dùng.
4. **Xác thực an toàn:**
   * Xác thực phân quyền dựa trên JWT Token lưu tại `localStorage`.

---

## 🛠️ Công Nghệ Sử Dụng

### Backend
* **FastAPI** – Framework web Python hiệu năng cao.
* **SQLAlchemy ORM** & **Alembic** – Quản lý cơ sở dữ liệu và migrations.
* **Pydantic v2** – Xác thực và kiểm soát dữ liệu đầu vào/ra.
* **Google GenAI SDK** – Tích hợp Gemini chấm điểm tự động.
* **SQLite** (Development) & **PostgreSQL** (Production).

### Frontend
* **HTML5 / CSS3 / Vanilla JS** – Giao diện gọn nhẹ, độc lập và tối ưu tốc độ.
* **Neumorphic Custom CSS System** – Hệ thống tokens màu sắc và bóng đổ thống nhất.
* **Bootstrap Icons** – Bộ icons đồng bộ và trực quan.

---

## 📂 Cấu Trúc Thư Mục

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
└── docker-compose.yml        # Cấu hình chạy dự án bằng Docker (PostgreSQL & API)
```

---

## ⚙️ Hướng Dẫn Khởi Động Dự Án

### Cách 1: Khởi chạy thủ công (Phù hợp khi phát triển/dev)

Do backend FastAPI được cấu hình để phục vụ cả API lẫn giao diện tĩnh, bạn chỉ cần chạy server backend:

1. **Di chuyển vào thư mục backend:**
   ```bash
   cd backend
   ```

2. **Khởi tạo môi trường ảo (Khuyên dùng):**
   * **Trên Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * **Trên macOS/Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Cài đặt thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Thiết lập biến môi trường:**
   Tạo file `.env` từ file mẫu `.env.example` và điền đầy đủ các thông tin:
   * `GEMINI_API_KEY`: API Key của Google Gemini.
   * `PAYOS_CLIENT_ID`, `PAYOS_API_KEY`, `PAYOS_CHECKSUM_KEY`: Cấu hình tích hợp cổng thanh toán PayOS.

5. **Khởi chạy ứng dụng:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

---

### Cách 2: Khởi chạy bằng Docker Compose (Production / Test Nhanh)

Đảm bảo bạn đã cài đặt Docker và chạy lệnh sau từ thư mục gốc của dự án:
```bash
docker-compose up --build -d
```
Lệnh này sẽ khởi chạy database PostgreSQL cùng backend API tự động liên kết với nhau.

---

## 🔗 Liên Kết Truy Cập Hệ Thống

Khi ứng dụng đã chạy trên cổng `8001`:

* **Trang chủ hệ thống:** [http://localhost:8001/](http://localhost:8001/) (FastAPI phục vụ nội dung của `crawled_data/`).
* **Trang Đăng nhập / Đăng ký:** [http://localhost:8001/frontend/auth.html](http://localhost:8001/frontend/auth.html).
* **Tài liệu API Swagger:** [http://localhost:8001/docs](http://localhost:8001/docs) *(yêu cầu `DEBUG=True` trong file `.env`)*.

---

## 🔑 Tài Khoản Thử Nghiệm

Hệ thống đi kèm cơ sở dữ liệu mẫu chứa các tài khoản test sau:

* **Tài khoản Quản trị (Admin):**
  * Email: `admin@aptiskey.com`
  * Mật khẩu: `admin123`
* **Cơ sở dữ liệu mẫu:** Gồm **78 đề thi** được nạp sẵn để test giới hạn lượt làm bài, đề thi VIP và thường.

---

## 🎨 Quy Ước Thiết Kế (Neumorphism Design Tokens)

Khi phát triển giao diện mới, luôn tuân thủ các quy tắc trong [neumorphism.css](file:///g:/My%20Drive/code/aptiskey/crawled_data/css/neumorphism.css):
* **Màu nền chính:** `#e0e5ec`
* **Hiệu ứng nổi khối (Outset Card):** `box-shadow: 6px 6px 16px #a3b1c6, -6px -6px 16px #ffffff;`
* **Hiệu ứng lõm (Inset Input):** `box-shadow: inset 4px 4px 10px #a3b1c6, inset -4px -4px 10px #ffffff;`
* **Màu nhấn (Accent):** `#4f8ef7` (Xanh dương) và `#6c63ff` (Tím).
