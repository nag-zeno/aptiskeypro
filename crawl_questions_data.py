import os
import time
import json
from auth import get_authenticated_session
from config import BASE_URL, OUTPUT_DIR, REQUEST_DELAY
from scraper import clean_bom_and_load_json, scan_and_download_audio_from_json

ENDPOINTS = {
    "reading": [
        ("reading-question1-data", "question1.json"),
        ("reading-question2-data", "question2.json"),
        ("reading-question4-data", "question4.json"),
        ("reading-question5-data", "question5.json"),
    ],
    "listening": [
        ("listening-question1-13-data", "question1_13.json"),
        ("listening-question14-data", "question14.json"),
        ("listening-question15-data", "question15.json"),
        ("listening-question16-17-data", "question16_17.json"),
    ]
}

def crawl_questions():
    print("=" * 60)
    print("      APTISKEY QUESTIONS DATA CRAWLER - START")
    print("=" * 60)
    
    session = get_authenticated_session()
    
    for skill, items in ENDPOINTS.items():
        skill_dir = os.path.join(OUTPUT_DIR, skill)
        os.makedirs(skill_dir, exist_ok=True)
        
        for api_name, filename in items:
            time.sleep(REQUEST_DELAY)
            url = f"{BASE_URL}/api/{api_name}"
            local_path = os.path.join(skill_dir, filename)
            
            try:
                print(f"[{skill.upper()}] Calling: {url} -> {filename}")
                res = session.get(url, timeout=15)
                
                if res.status_code == 200:
                    content_type = res.headers.get("content-type", "")
                    if "application/json" not in content_type and not res.text.strip().startswith(('\ufeff', '{', '[')):
                        print(f"[{skill.upper()}] [Loi] Response does not appear to be JSON. Pls check session/login.")
                        continue
                        
                    data = clean_bom_and_load_json(res.text)
                    with open(local_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"[{skill.upper()}] Saved successfully: {filename}")
                    
                    if skill == "listening":
                        print(f"[{skill.upper()}] Scanning and downloading audio files...")
                        scan_and_download_audio_from_json(session, data)
                else:
                    print(f"[{skill.upper()}] [Loi] Status {res.status_code} when calling {api_name}")
            except Exception as e:
                print(f"[{skill.upper()}] [Loi] Exception during crawl {api_name}: {e}")
                
    print("=" * 60)
    print("      APTISKEY QUESTIONS DATA CRAWLER - COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    crawl_questions()
