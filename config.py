import os

# Cấu hình chung cho crawler
BASE_URL = "https://aptiskey.com"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawled_data")

# Đường dẫn file lưu session cookie
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session_cookies.json")

# Tài khoản đăng nhập được cung cấp
USERNAME = "hienminn"
PASSWORD = "daQzyZ"

# Headers mặc định để giả lập trình duyệt tránh bị chặn
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/grammar_bode.html"
}

# Khoảng nghỉ (giây) giữa các request để mô phỏng người dùng thật và tránh rate limit / block IP
REQUEST_DELAY = 2.5
