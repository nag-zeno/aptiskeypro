#!/bin/bash
# ==============================================================================
# Script Cài đặt Máy chủ Ubuntu trên Google Compute Engine (GCE VM) cho AptisKey
# ==============================================================================

set -e

echo "======================================================"
echo "   🚀 CÀI ĐẶT MÔI TRƯỜNG CHẠY APTISKEY TRÊN UBUNTU VM"
echo "======================================================"

# 1. Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt các gói tiện ích cơ bản
sudo apt install -y curl git ufw nginx certbot python3-certbot-nginx

# 3. Cài đặt Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Đang cài đặt Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# 4. Cài đặt Docker Compose
sudo apt install -y docker-compose-plugin

# 5. Cấu hình Tường lửa (UFW)
echo "🛡️ Cấu hình UFW Firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo ""
echo "======================================================"
echo "   ✅ CÀI ĐẶT MÔI TRƯỜNG HOÀN TẤT!"
echo "======================================================"
echo "Các bước tiếp theo:"
echo "1. Clone hoặc copy mã nguồn AptisKey vào VM: git clone <repo_url> aptiskey"
echo "2. Vào thư mục: cd aptiskey"
echo "3. Cấu hình file backend/.env với GEMINI_API_KEY và SECRET_KEY"
echo "4. Khởi chạy: docker compose up -d"
echo "5. Cấu hình Nginx reverse proxy với file deploy/nginx.conf"
echo "6. Cấp chứng chỉ SSL: sudo certbot --nginx -d yourdomain.com"
