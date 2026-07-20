import os
import time
import requests
from auth import get_authenticated_session
from config import BASE_URL, OUTPUT_DIR, REQUEST_DELAY

ASSETS_LIST = [
    "js/grammar/grammar_test.js",
    "js/reading/reading_test.js",
    "js/listening/listening_test.js",
    "js/writing/writing_test.js",
    "js/home.js",
    
    # Scripts cho phan hoc theo cau hoi
    "js/reading_question/reading_question1.js",
    "js/reading_question/reading_question2.js",
    "js/reading_question/reading_question4.js",
    "js/reading_question/reading_question5.js",
    
    "js/listening_question/listening_question1_13.js",
    "js/listening_question/listening_question14.js",
    "js/listening_question/listening_question15.js",
    "js/listening_question/listening_question16_17.js",
    
    "css/readingkey.css",
    "css/listeningkey.css",
    "css/writingkey.css",
    "css/speakingkey.css",
    "css/grammar.css",
]

def download_assets():
    print("=" * 60)
    print("    APTISKEY ASSETS DOWNLOADER - START")
    print("=" * 60)
    
    session = get_authenticated_session()
    downloaded = 0
    
    for asset_path in ASSETS_LIST:
        time.sleep(REQUEST_DELAY)
        
        url = f"{BASE_URL}/{asset_path}"
        local_path = os.path.join(OUTPUT_DIR, *asset_path.split("/"))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            print(f"[Tai file] Dang tai: {url} -> {asset_path}")
            res = session.get(url, timeout=10)
            if res.status_code == 200:
                with open(local_path, "w", encoding="utf-8") as f:
                    f.write(res.text)
                downloaded += 1
            else:
                print(f"[Loi] Status {res.status_code} khi tai {asset_path}")
        except Exception as e:
            print(f"[Loi] Gap su co khi tai {asset_path}: {e}")
            
    print("-" * 60)
    print(f"Hoan thanh tai assets: {downloaded}/{len(ASSETS_LIST)} tep.")
    print("=" * 60)

if __name__ == "__main__":
    download_assets()
