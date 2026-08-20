# Hướng Dẫn Triển Khai Website AptisKey Lên Google Cloud Platform (GCP)

Tài liệu này hướng dẫn chi tiết từng bước để đưa toàn bộ hệ thống website **AptisKey** (bao gồm FastAPI Backend, AI Chấm điểm Gemini, Giao diện Neumorphism và Database) lên **Google Cloud Platform (GCP)**.

---

## 📑 Mục Lục
1. [Lựa Chọn Phương Án Triển Khai](#1-lựa-chọn-phương-án-triển-khai)
2. [Chuẩn Bị Trước Khi Triển Khai](#2-chuẩn-bị-trước-khi-triển-khai)
3. [Phương Án 1: Triển Khai Lên Google Cloud Run (Khuyên Dùng)](#3-phương-án-1-triển-khai-lên-google-cloud-run-khuyên-dùng)
   - [Cách A: Sử dụng gcloud CLI (Nhanh nhất)](#cách-a-sử-dụng-gcloud-cli-nhanh-nhất)
   - [Cách B: Thao tác qua Giao diện GCP Console (Web)](#cách-b-thao-tác-qua-giao-diện-gcp-console-web)
   - [Cấu hình Cơ Sở Dữ Liệu PostgreSQL](#cấu-hình-cơ-sở-dữ-liệu-postgresql)
   - [Cài đặt Biến Môi Trường (Environment Variables)](#cài-đặt-biến-môi-trường-environment-variables)
4. [Phương Án 2: Triển Khai Lên Google Compute Engine (Máy Ảo VM)](#4-phương-án-2-triển-khai-lên-google-compute-engine-máy-ảo-vm)
5. [Cấu Hình Tên Miền Riêng (Custom Domain) & SSL](#5-cấu-hình-tên-miền-riêng-custom-domain--ssl)
6. [Xử Lý Lỗi Thường Gặp (Troubleshooting)](#6-xử-lý-lỗi-thường-gặp-troubleshooting)

---

## 1. Lựa Chọn Phương Án Triển Khai

| Tiêu chí | **Google Cloud Run (Serverless)** ⭐ | **Google Compute Engine (VM)** |
| :--- | :--- | :--- |
| **Độ khó** | Dễ & Tự động hoàn toàn | Trung bình (cần biết dùng Linux cơ bản) |
| **Chi phí** | Rất rẻ (Miễn phí 2 triệu requests/tháng, tự tắt về 0 khi không dùng) | Miễn phí với cấu hình `e2-micro` (Always Free tier) |
| **SSL / HTTPS** | Tự động 100% bởi Google | Cần cài Let's Encrypt / Certbot |
| **Database** | Khuyên dùng PostgreSQL Cloud (Neon / Supabase miễn phí) | Dùng trực tiếp SQLite hoặc PostgreSQL Docker |
| **Tự động cập nhật** | Tích hợp CI/CD với GitHub chỉ bằng 1 nút bấm | Cần SSH vào máy ảo để `git pull` & restart |

---

## 2. Chuẩn Bị Trước Khi Triển Khai

### 2.1. Tài khoản Google Cloud
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Đăng ký tài khoản (Nhận ngay $300 credit miễn phí trong 90 ngày cho tài khoản mới).
3. Tạo một **Project mới** (ví dụ: `aptiskey-app`). Ghi lại **Project ID**.

### 2.2. Lấy Google Gemini API Key
- Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey).
- Bấm **Create API key** và lưu lại chuỗi khóa để phục vụ tính năng AI chấm điểm tự luận.

---

## 3. Phương Án 1: Triển Khai Lên Google Cloud Run (Khuyên Dùng)

### Cách A: Sử dụng gcloud CLI (Nhanh nhất)

#### Bước 1: Cài đặt Google Cloud SDK
- Tải và cài đặt tại: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
- Mở Terminal / PowerShell và đăng nhập:
  ```bash
  gcloud auth login
  ```

#### Bước 2: Chạy Script Tự Động
Dự án đã chuẩn bị sẵn script triển khai 1-click trong thư mục `deploy/`:

- **Trên Windows (PowerShell):**
  ```powershell
  cd deploy
  .\deploy-cloudrun.ps1
  ```

- **Trên Linux / Mac / GCP Cloud Shell:**
  ```bash
  chmod +x deploy/deploy-cloudrun.sh
  ./deploy/deploy-cloudrun.sh
  ```

---

### Cách B: Thao tác qua Giao diện GCP Console (Web)

Nếu bạn không muốn cài đặt dòng lệnh, bạn có thể thực hiện trực tiếp trên trình duyệt:

#### Bước 1: Mở Cloud Shell
1. Vào [Google Cloud Console](https://console.cloud.google.com/).
2. Bấm vào biểu tượng **Activate Cloud Shell** `>_` ở góc trên cùng bên phải màn hình.
3. Clone mã nguồn dự án của bạn:
   ```bash
   git clone <URL_REPO_GITHUB_CỦA_BẠN> aptiskey
   cd aptiskey
   ```

#### Bước 2: Build Container Image
Chạy lệnh sau ngay trong Cloud Shell:
```bash
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/aptiskey:latest
```

#### Bước 3: Tạo Dịch Vụ Cloud Run
1. Trên thanh tìm kiếm GCP, gõ **Cloud Run** và chọn dịch vụ.
2. Bấm **Create Service**.
3. Chọn **Deploy one revision from an existing container image**.
4. Bấm **Select** và chọn image `aptiskey:latest` vừa build ở Bước 2.
5. Cấu hình cơ bản:
   - **Service name:** `aptiskey`
   - **Region:** `asia-southeast1 (Singapore)` (tối ưu tốc độ cho người dùng Việt Nam).
   - **Authentication:** Chọn **Allow unauthenticated invocations** (cho phép người dùng truy cập công khai).
   - **Container port:** Nhập `8001`.
6. Mở rộng phần **Container, Volumes, Networking, Security**:
   - **Memory:** `1 GiB` (hoặc 512 MiB).
   - **CPU:** `1`.
   - **Environment variables:** Xem hướng dẫn bên dưới.
7. Bấm **Create** và đợi 1-2 phút. Bạn sẽ nhận được đường link website dạng `https://aptiskey-xxxx-as.a.run.app`.

---

### Cấu hình Cơ Sở Dữ Liệu PostgreSQL

Do Cloud Run là môi trường Serverless (có thể khởi động lại hoặc co giãn đa phiên bản), bạn nên kết nối đến một Database PostgreSQL đám mây:

> [!TIP]
> **Tùy chọn Miễn Phí Tốt Nhất:** 
> Tạo 1 tài khoản miễn phí tại [Neon.tech](https://neon.tech) hoặc [Supabase.com](https://supabase.com), tạo 1 Database PostgreSQL mới và copy chuỗi kết nối dạng:
> `postgresql://user:password@ep-sample-12345.us-east-1.aws.neon.tech/neondb?sslmode=require`

---

### Cài đặt Biến Môi Trường (Environment Variables)

Tại trang quản lý Cloud Run Service `aptiskey`, chọn **Edit & Deploy New Revision** $\rightarrow$ tab **Variables & Secrets**, thêm các biến sau:

| Tên Biến | Giá Trị Mẫu | Mô Tả |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://...` | Đường dẫn kết nối PostgreSQL |
| `SECRET_KEY` | `Chuoi_Ngau_Nhien_Dai_Hon_32_Ky_Tu_Bao_Mat` | Khóa mã hóa JWT Token |
| `GEMINI_API_KEY` | `AIzaSy...` | Khóa API Google Gemini |
| `APP_NAME` | `AptisPro` | Tên hệ thống |
| `DEBUG` | `False` | Chế độ Production |
| `ADMIN_EMAIL` | `admin@aptiskey.com` | Email tài khoản quản trị khởi tạo |
| `ADMIN_PASSWORD` | `MatKhauAdmin@2026` | Mật khẩu tài khoản quản trị |

---

## 4. Phương Án 2: Triển Khai Lên Google Compute Engine (Máy Ảo VM)

Nếu bạn muốn có 1 máy ảo Ubuntu riêng, giữ nguyên file database SQLite cục bộ và toàn quyền cấu hình:

### Bước 1: Tạo VM Instance trên GCP
1. Vào **Compute Engine** $\rightarrow$ **VM instances** $\rightarrow$ **Create Instance**.
2. **Name:** `aptiskey-server`.
3. **Region:** `asia-southeast1 (Singapore)`.
4. **Machine configuration:** `e2-micro` (hoặc `e2-small`).
5. **Boot disk:** Chọn `Ubuntu 22.04 LTS` hoặc `Ubuntu 24.04 LTS` (Ổ đĩa 20-30GB SSD).
6. **Firewall:** Tích chọn cả hai ô:
   - ✅ **Allow HTTP traffic**
   - ✅ **Allow HTTPS traffic**
7. Bấm **Create**.

### Bước 2: Cài Đặt Tự Động Trên Máy Ảo
1. Bấm nút **SSH** cạnh máy ảo trên giao diện GCP để mở cửa sổ dòng lệnh.
2. Tải và chạy script cài đặt tự động của dự án:
   ```bash
   # Clone mã nguồn
   git clone <URL_REPO_GITHUB_CỦA_BẠN> aptiskey
   cd aptiskey
   
   # Chạy script setup môi trường (cài Docker, Nginx, Certbot)
   chmod +x deploy/setup-gce-vm.sh
   ./deploy/setup-gce-vm.sh
   ```

### Bước 3: Cấu Hình và Khởi Chạy
1. Tạo file cấu hình môi trường:
   ```bash
   cp .env.production.example backend/.env
   nano backend/.env
   # Điền GEMINI_API_KEY, SECRET_KEY rồi nhấn Ctrl+O (Lưu), Ctrl+X (Thoát)
   ```
2. Khởi chạy hệ thống bằng Docker Compose:
   ```bash
   docker compose up -d --build
   ```

### Bước 4: Cấu Hình Nginx & SSL
1. Copy cấu hình Nginx:
   ```bash
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/aptiskey
   sudo nano /etc/nginx/sites-available/aptiskey # Sửa yourdomain.com thành tên miền của bạn
   sudo ln -s /etc/nginx/sites-available/aptiskey /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   sudo nginx -t && sudo systemctl reload nginx
   ```
2. Kích hoạt chứng chỉ SSL Let's Encrypt tự động:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## 5. Cấu Hình Tên Miền Riêng (Custom Domain) & SSL

### Cho Google Cloud Run:
1. Vào **Cloud Run** $\rightarrow$ Chọn **Manage Custom Domains** (hoặc tab *Custom Domains*).
2. Bấm **Add Mapping** $\rightarrow$ Chọn Service `aptiskey` và nhập tên miền của bạn (ví dụ: `aptiskey.com` hoặc `app.aptiskey.com`).
3. Google sẽ cung cấp danh sách bản ghi DNS (Bản ghi `CNAME` hoặc `A / AAAA`).
4. Truy cập trang quản lý tên miền của bạn (Cloudflare, Namecheap, GoDaddy, Pavietnam, Matbao...) và thêm các bản ghi DNS tương ứng.
5. Google sẽ tự động phát hành chứng chỉ SSL Managed Certificate miễn phí trong khoảng 15-30 phút.

---

## 6. Xử Lý Lỗi Thường Gặp (Troubleshooting)

### 1. Lỗi Gemini AI không chấm điểm được:
- **Nguyên nhân:** Chưa cấu hình biến môi trường `GEMINI_API_KEY` hoặc API key bị hết hạn/giới hạn quota.
- **Khắc phục:** Kiểm tra lại biến môi trường `GEMINI_API_KEY` trên Cloud Run hoặc file `backend/.env`.

### 2. Giao diện báo lỗi CORS:
- **Nguyên nhân:** Frontend gọi API khác origin mà chưa được khai báo.
- **Khắc phục:** Thêm domain của bạn vào biến môi trường `ALLOWED_ORIGINS` dạng JSON:
  `ALLOWED_ORIGINS=["https://aptiskey.com","https://www.aptiskey.com"]`.

### 3. Container Cloud Run bị Restart hoặc Timeout khi khởi động:
- **Nguyên nhân:** Cấp phát RAM quá ít (dưới 512MB) hoặc thời gian nạp đề thi ban đầu lâu.
- **Khắc phục:** Tăng RAM lên `1 GiB` hoặc `2 GiB`, tăng **Request Timeout** lên `300s` trong cấu hình Cloud Run.

---
*Tài liệu được biên soạn và tối ưu cho dự án AptisKey.*
