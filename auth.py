import os
import json
import requests
import time
from config import BASE_URL, HEADERS, USERNAME, PASSWORD, TOKEN_FILE, REQUEST_DELAY

def verify_session(session):
    """
    Kiem tra xem session hien tai co con hoat dong hop le khong bang cach goi /api/me
    Tra ve True neu hop le, False neu nguoc lai.
    """
    try:
        url = f"{BASE_URL}/api/me"
        response = session.get(url, timeout=10)
        
        # Neu phan hoi thanh cong va kieu du lieu la JSON (khong phai trang login HTML redirect)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                data = response.json()
                if data.get("success"):
                    print("[Xac thuc] Token phien hoat dong con han. Tai su dung session.")
                    return True
        return False
    except Exception as e:
        print(f"[Xac thuc] Loi khi kiem tra phien hoat dong: {e}")
        return False

def login_and_save_session():
    """
    Thuc hien POST login va luu token cookie vao file
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    
    login_url = f"{BASE_URL}/login"
    payload = {
        "email": USERNAME,
        "password": PASSWORD
    }
    
    print(f"[Xac thuc] Dang tien hanh dang nhap he thong bang tai khoan: '{USERNAME}'...")
    try:
        response = session.post(login_url, data=payload, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    print("[Xac thuc] Dang nhap thanh cong!")
                    # Luu cookie vao file
                    cookies_dict = session.cookies.get_dict()
                    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                        json.dump(cookies_dict, f, indent=2)
                    print(f"[Xac thuc] Da ghi cookies vao file: {TOKEN_FILE}")
                    # Cho mot chut de tranh bi chong cheo request sau login
                    time.sleep(REQUEST_DELAY)
                    return session
                else:
                    error_msg = data.get("message", "Loi khong xac dinh")
                    print(f"[Xac thuc] [Loi] Dang nhap that bai: {error_msg}")
            except Exception as je:
                print(f"[Xac thuc] [Loi] Khong phan tich duoc phan hoi dang nhap: {je}. Noi dung phan hoi: {response.text[:200]}")
        elif response.status_code == 429:
            print("[Xac thuc] [Loi] Bi chan vi dang nhap qua nhieu lan (429). Vui long cho 15 phut hoac copy token thu cong vao file.")
        else:
            print(f"[Xac thuc] [Loi] Server tra ve status code: {response.status_code}")
    except Exception as e:
        print(f"[Xac thuc] [Loi] Xay ra su co khi gui yeu cau dang nhap: {e}")
        
    return None

def get_authenticated_session():
    """
    Lay session da xac thuc. Uu tien nap tu file cookie, neu hop le thi dung luon,
    neu het han thi thuc hien dang nhap lai de cap nhat phien lam viec.
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # 1. Thu nap cookie tu file cu va kiem tra
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                cookies_dict = json.load(f)
            session.cookies.update(cookies_dict)
            if verify_session(session):
                print(f"[Xac thuc] Da nap {len(cookies_dict)} cookie tu file va xac thuc thanh cong.")
                return session
            else:
                print("[Xac thuc] Cookie cu da het han hoac khong hop le. Dang nhap lai...")
        except Exception as e:
            print(f"[Xac thuc] Loi khi doc cookie tu file: {e}")
            
    # 2. Dang nhap neu file cookie chua ton tai hoac da het han
    new_session = login_and_save_session()
    if new_session:
        return new_session
        
    print("[Canh bao] Dang nhap that bai. Tra ve session rong.")
    return session
