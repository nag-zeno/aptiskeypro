import os
import time
import requests
from auth import get_authenticated_session
from config import BASE_URL, OUTPUT_DIR, REQUEST_DELAY

# Danh sach cac trang HTML can download de tao giao dien offline
PAGES_LIST = [
    # Trang chu va cac trang dieu huong chinh
    "home.html",
    "grammar_bode.html",
    
    "reading_question.html",
    "reading_bode.html",
    "reading_meo.html",
    
    # Cac trang reading question
    "reading_question1.html",
    "reading_question2.html",
    "reading_question4.html",
    "reading_question5.html",
    
    "listening_question.html",
    "listening_bode.html",
    "listening_meo.html",
    
    # Cac trang listening question
    "listening_question1_13.html",
    "listening_question14.html",
    "listening_question15.html",
    "listening_question16_17.html",
    
    "writing_bode.html",
    "writing_meo.html",
    
    "speaking_question.html",
    "speaking_meo.html",
    
    # Cac trang speaking total & practice
    "speaking_question1.html",
    "speaking_question1_practice",
    "speaking_question1_total",
    
    "speaking_question2.html",
    "speaking_question2_practice",
    "speaking_question2_total",
    
    "speaking_question3.html",
    "speaking_question3_practice",
    "speaking_question3_total",
    
    "speaking_question4.html",
    "speaking_question4_practice",
    "speaking_question4_total",
]

# Them cac trang de thi cua tung ky nang
# 1. Grammar tests 1..5
for i in range(1, 6):
    PAGES_LIST.append(f"grammar_test{i:03d}.html")

# 2. Reading tests 1..14
for i in range(1, 15):
    PAGES_LIST.append(f"reading{i:03d}.html")

# 3. Listening tests 1..15
for i in range(1, 16):
    PAGES_LIST.append(f"listeningkey{i:03d}.html")

# 4. Writing tests 1..40
for i in range(1, 41):
    PAGES_LIST.append(f"writingkey{i:03d}.html")

def download_pages():
    print("=" * 60)
    print("        APTISKEY PAGES DOWNLOADER - BAT DAU")
    print("=" * 60)
    
    session = get_authenticated_session()
    downloaded = 0
    errors = 0
    
    for page_name in PAGES_LIST:
        time.sleep(REQUEST_DELAY)
        
        url = f"{BASE_URL}/{page_name}"
        
        # Tao file path luu tru
        # Neu page khong co duoi, ta se luu chuoi .html de server phuc vu thuan tien
        file_name = page_name
        if not file_name.endswith(".html") and not file_name.endswith(".htm"):
            file_name += ".html"
            
        local_path = os.path.join(OUTPUT_DIR, file_name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            print(f"[Tai trang] Dang tai: {url} -> {os.path.basename(local_path)}")
            res = session.get(url, timeout=10)
            
            if res.status_code == 200:
                with open(local_path, "w", encoding="utf-8") as f:
                    f.write(res.text)
                downloaded += 1
            else:
                print(f"[Loi] Khong tai duoc {page_name} - Status: {res.status_code}")
                errors += 1
        except Exception as e:
            print(f"[Loi] Xay ra loi khi tai {page_name}: {e}")
            errors += 1
            
    print("-" * 60)
    print(f"Hoan thanh tai trang HTML: Tai thanh cong {downloaded}/{len(PAGES_LIST)} trang.")
    print("=" * 60)

if __name__ == "__main__":
    download_pages()
