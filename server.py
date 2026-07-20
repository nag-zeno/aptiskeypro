import os
import re
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawled_data")

class MockBackendHandler(BaseHTTPRequestHandler):
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def send_static_file(self, filepath, content_type):
        if not os.path.exists(filepath):
            # Tu dong thu tim file .html neu yeu cau duong dan khong co phan mo rong
            if not os.path.splitext(filepath)[1]:
                html_path = filepath + ".html"
                if os.path.exists(html_path):
                    return self.send_static_file(html_path, "text/html; charset=utf-8")
            
            self.send_error(404, f"File not found: {os.path.basename(filepath)}")
            return
            
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(os.path.getsize(filepath)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

    def get_content_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".html" or ext == ".htm":
            return "text/html; charset=utf-8"
        elif ext == ".css":
            return "text/css"
        elif ext == ".js":
            return "application/javascript"
        elif ext == ".png":
            return "image/png"
        elif ext == ".jpg" or ext == ".jpeg":
            return "image/jpeg"
        elif ext == ".gif":
            return "image/gif"
        elif ext == ".ico":
            return "image/x-icon"
        elif ext == ".mp3":
            return "audio/mpeg"
        elif ext == ".svg":
            return "image/svg+xml"
        return "application/octet-stream"

    def do_GET(self):
        # 1. Giai ma URL va chuan hoa path
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # 2. Xử lý các API endpoints
        # API User me
        if path == "/api/me":
            mock_user = {
                "success": True,
                "email": "hocvien@aptispro.com",
                "fullName": "Học viên AptisPro",
                "isAdmin": False,
                "status": "Học viên chính thức",
                "expiredAt": "2099-12-31T23:59:59.000Z"
            }
            return self.send_json_response(mock_user)
            
        # API Grammar data
        match_grammar = re.match(r"^/api/grammar-data/(\d+)$", path)
        if match_grammar:
            test_id = int(match_grammar.group(1))
            json_path = os.path.join(DIRECTORY, "grammar", f"test_{test_id:03d}.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self.send_json_response(data)
            return self.send_json_response({"success": False, "message": "Không tìm thấy bộ đề"}, 404)
            
        # API Reading data
        match_reading = re.match(r"^/api/reading-test-data/(\d+)$", path)
        if match_reading:
            test_id = int(match_reading.group(1))
            json_path = os.path.join(DIRECTORY, "reading", f"test_{test_id:03d}.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self.send_json_response(data)
            return self.send_json_response({"success": False, "message": "Không tìm thấy bộ đề"}, 404)

        # API Listening data
        match_listening = re.match(r"^/api/listeningkey-data/(\d+)$", path)
        if match_listening:
            test_id = int(match_listening.group(1))
            json_path = os.path.join(DIRECTORY, "listening", f"test_{test_id:03d}.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self.send_json_response(data)
            return self.send_json_response({"success": False, "message": "Không tìm thấy bộ đề"}, 404)

        # API Writing data
        match_writing = re.match(r"^/api/writingkey-data/(\d+)$", path)
        if match_writing:
            test_id = int(match_writing.group(1))
            json_path = os.path.join(DIRECTORY, "writing", f"test_{test_id:03d}.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self.send_json_response(data)
            return self.send_json_response({"success": False, "message": "Không tìm thấy bộ đề"}, 404)

        # API Question data (Học theo câu hỏi)
        QUESTION_API_MAP = {
            "/api/reading-question1-data": ("reading", "question1.json"),
            "/api/reading-question2-data": ("reading", "question2.json"),
            "/api/reading-question4-data": ("reading", "question4.json"),
            "/api/reading-question5-data": ("reading", "question5.json"),
            "/api/listening-question1-13-data": ("listening", "question1_13.json"),
            "/api/listening-question14-data": ("listening", "question14.json"),
            "/api/listening-question15-data": ("listening", "question15.json"),
            "/api/listening-question16-17-data": ("listening", "question16_17.json"),
        }
        if path in QUESTION_API_MAP:
            skill, filename = QUESTION_API_MAP[path]
            json_path = os.path.join(DIRECTORY, skill, filename)
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self.send_json_response(data)
            return self.send_json_response({"success": False, "message": "Không tìm thấy dữ liệu câu hỏi"}, 404)

        # 3. Phục vụ giao diện tĩnh (Static Files)
        # Đường dẫn mặc định sang index.html
        if path == "/" or path == "":
            path = "/index.html"
            
        # Neu la file audio (.mp3), serve tu thu muc listening/audio phang
        if path.endswith(".mp3"):
            filename = os.path.basename(path)
            filepath = os.path.join(DIRECTORY, "listening", "audio", filename)
            return self.send_static_file(filepath, "audio/mpeg")
            
        # Loai bo dau gach cheo o dau va tao filepath day du
        filepath = os.path.join(DIRECTORY, *path.lstrip("/").split("/"))
        content_type = self.get_content_type(filepath)
        
        self.send_static_file(filepath, content_type)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # Gia lap login thành công
        if path == "/login":
            response_data = {
                "success": True,
                "message": "Đăng nhập thành công! Phiên bản cục bộ thử nghiệm.",
                "redirect": "/home.html",
                "expired": False
            }
            return self.send_json_response(response_data)
            
        self.send_error(404, "Endpoint not found")

def run_server():
    server_address = ("", PORT)
    httpd = ThreadingHTTPServer(server_address, MockBackendHandler)
    print("=" * 60)
    print(f"   APTISKEY MOCK SERVER DANG CHAY TAI: http://localhost:{PORT}")
    print(f"   Thu muc giao dien: {DIRECTORY}")
    print("   Nhan Ctrl+C de dung server.")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Dung] Da dung server.")

if __name__ == "__main__":
    run_server()
