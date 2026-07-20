import os
import argparse
from auth import get_authenticated_session
from scraper import crawl_skill_api, crawl_speaking_data
from config import BASE_URL, OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(description="Aptiskey Structured Data Crawler")
    parser.add_argument(
        "--skill", 
        type=str, 
        default="all", 
        choices=["all", "grammar", "reading", "listening", "writing", "speaking"],
        help="Ky nang can crawl (grammar, reading, listening, writing, speaking hoac all)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("        APTISKEY STRUCTURED CRAWLER - KHOI DONG CRAWL")
    print("=" * 60)
    print(f"Muc tieu: {args.skill.upper()}")
    print(f"Thu muc luu tru: {OUTPUT_DIR}")
    print("-" * 60)
    
    # Lay session xac thuc
    session = get_authenticated_session()
    
    # Kiem tra xem co lay duoc session xac thuc khong
    # Neu token hoac email bi khoa, phai canh bao va thoat
    # (hoac neu thieu token nhung chay duoc api van co the tip tuc kiem tra)
    
    # 5 Ky nang can crawl
    skills_map = {
        "grammar": ("grammar", "api/grammar-data/{id}"),
        "reading": ("reading", "api/reading-test-data/{id}"),
        "listening": ("listening", "api/listeningkey-data/{id}"),
        "writing": ("writing", "api/writingkey-data/{id}"),
    }
    
    try:
        if args.skill == "all":
            # Chay tat ca cac ky nang co API
            for skill_name, (name, endpoint) in skills_map.items():
                crawl_skill_api(session, name, endpoint)
            # Chay speaking
            crawl_speaking_data(session)
        elif args.skill == "speaking":
            crawl_speaking_data(session)
        else:
            name, endpoint = skills_map[args.skill]
            crawl_skill_api(session, name, endpoint)
            
        print("\n" + "=" * 60)
        print("                 CRAWL HOAN THANH!")
        print(f"Ket qua du lieu da luu tru tai: {OUTPUT_DIR}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n[Dung] Tien trinh crawl bi dung boi nguoi dung.")
    except Exception as e:
        print(f"\n[Loi] Gap su co nghiem trong khi crawl: {e}")

if __name__ == "__main__":
    main()
