import os
import re

DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawled_data")

# Cac cap gia tri can thay the
REPLACEMENTS = {
    # Thuong hieu chuoi viet thuong va viet hoa
    "AptisKey.com": "AptisPro.com",
    "aptiskey.com": "aptispro.com",
    "AptisKey": "AptisPro",
    "Aptiskey": "AptisPro",
    "aptiskey": "aptispro",
    "APTISKEY": "APTISPRO",
    
    # Cac tieu de va ban quyen footer
    "Copyright © 2026 Aptiskey.com": "Copyright © 2026 AptisPro.com",
    "Nội dung do AptisKey biên soạn độc lập để hỗ trợ ôn luyện": "Nội dung do AptisPro biên soạn độc lập để hỗ trợ ôn luyện",
    
    # Cac bien the "Aptis keys" / "Aptis Keys" / "Aptis Key"
    "Aptis Keys": "AptisPro",
    "Aptis keys": "AptisPro",
    "Aptis key": "AptisPro",
    "Aptis Key": "AptisPro",
    "Aptis Team": "AptisPro Team",
    
    # Cac tieu de trang con
    "Aptis grammar keys": "AptisPro Grammar",
    "Aptis listening keys": "AptisPro Listening",
    "Aptis reading keys": "AptisPro Reading",
    "Aptis writing keys": "AptisPro Writing",
    "Aptis keys - Mẹo viết thư": "AptisPro - Mẹo viết thư",
    "APTIS KEY 2026": "APTISPRO 2026",
    
    # Meta SEO
    "https://aptiskey.com": "http://localhost:8000",
}

# The logo can thay the
OLD_LOGO_IMG = """<img
              src="./images/assets/img/AdminLTELogo.png"
              alt="AdminLTE Logo"
              class="brand-image opacity-75 shadow"
            />"""
NEW_LOGO_ICON = """<i class="bi bi-mortarboard-fill text-white fs-4 me-2 ms-3"></i>"""

def rebrand_file(filepath):
    # Chi rebrand cac file text nhu html, js, css, json
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".html", ".htm", ".js", ".css", ".json"):
        return False
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        
        # 1. Thuc hien thay the thuong hieu
        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)
            
        # Thay the logo hinh anh bang logo bieu tuong
        content = content.replace(OLD_LOGO_IMG, NEW_LOGO_ICON)
        # Giup phong tranh xuong dong khac nhau trong Windows/Linux
        content = content.replace(OLD_LOGO_IMG.replace("\n", "\r\n"), NEW_LOGO_ICON)
            
        # 2. Xoa cac link facebook hoac cac code chat widget lien ket ngoai neu co
        # Vi du: href="https://www.facebook.com/aptiskey" -> href="#"
        content = re.sub(r'href="https://www\.facebook\.com/[a-zA-Z0-9_.]+"', 'href="#"', content)
        content = re.sub(r'href="https://zalo\.me/[0-9]+"', 'href="#"', content)
        
        # 3. Thay the logo PNG cu bang mot Logo CSS dang chu dep neu phat hien
        
        # 4. Tiem font Roboto va CSS material_you.css vao head cua cac file HTML
        if filepath.endswith(".html") or filepath.endswith(".htm"):
            if "material_you.css" not in content:
                head_inject = """    <!-- begin::Material You Theme Integration -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="./css/material_you.css" />
    <!-- end::Material You Theme Integration -->
"""
                content = content.replace("</head>", f"{head_inject}</head>")
                
            if "md-bg-shape" not in content:
                body_inject = """
    <!-- begin::Material You Background Elements -->
    <div class="md-bg-shape md-bg-shape-primary"></div>
    <div class="md-bg-shape md-bg-shape-tertiary"></div>
    <!-- end::Material You Background Elements -->
"""
                content = re.sub(r'(<body[^>]*>)', r'\1' + body_inject, content, count=1)
        
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"[Loi] Khong the rebrand file {filepath}: {e}")
    return False

def rebrand_all():
    print("=" * 60)
    print("      APTISKEY TO APTISPRO REBRANDING - BAT DAU")
    print("=" * 60)
    
    rebranded_count = 0
    total_files = 0
    
    for root, dirs, files in os.walk(DIRECTORY):
        for file in files:
            filepath = os.path.join(root, file)
            total_files += 1
            if rebrand_file(filepath):
                print(f"[Rebrand] Da lam sach: {os.path.relpath(filepath, DIRECTORY)}")
                rebranded_count += 1
                
    print("-" * 60)
    print(f"Hoan thanh Rebranding! Da lam sach {rebranded_count}/{total_files} tep trong crawled_data.")
    print("=" * 60)

if __name__ == "__main__":
    rebrand_all()
