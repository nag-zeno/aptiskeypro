import os
import time
import json
import re
import requests
from urllib.parse import urljoin, urlparse
from config import BASE_URL, OUTPUT_DIR, REQUEST_DELAY

def clean_bom_and_load_json(text):
    """
    Loai bo ky tu BOM va phan tich text thanh JSON
    """
    clean_text = text.lstrip('\ufeff')
    return json.loads(clean_text)

def download_binary_file(session, url, output_path):
    """
    Tai mot file nhi phan (nhu audio, hinh anh) va luu vao duong dan chi dinh
    """
    if os.path.exists(output_path):
        return True
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        print(f"[Tai file] Dang tai: {url} -> {os.path.basename(output_path)}")
        response = session.get(url, stream=True, timeout=15)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            time.sleep(1.0) # nghi 1s sau khi tai file nhi phan
            return True
        else:
            print(f"[Tai file] [Loi] Status {response.status_code} khi tai {url}")
    except Exception as e:
        print(f"[Tai file] [Loi] Gap su co khi tai {url}: {e}")
    return False

def scan_and_download_audio_from_json(session, json_data):
    """
    Duyet de quy qua JSON de tim cac link file .mp3 va tu dong tai ve
    """
    audio_urls = []
    
    def extract_urls(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "audioUrl" and v:
                    audio_urls.append(v)
                else:
                    extract_urls(v)
        elif isinstance(obj, list):
            for item in obj:
                extract_urls(item)
        elif isinstance(obj, str):
            if obj.endswith(".mp3") or "/audio/" in obj:
                audio_urls.append(obj)
                
    extract_urls(json_data)
    
    # Tien hanh tai cac file audio tim thay
    for audio_rel_url in set(audio_urls):
        # Tranh truong hop link la absolute ngoai he thong
        full_audio_url = urljoin(BASE_URL, audio_rel_url)
        
        # Tao ten file va duong dan luu tru
        parsed_url = urlparse(full_audio_url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = f"audio_{int(time.time())}.mp3"
            
        local_audio_path = os.path.join(OUTPUT_DIR, "listening", "audio", filename)
        download_binary_file(session, full_audio_url, local_audio_path)

def crawl_skill_api(session, skill_name, api_template, max_id=100):
    """
    Crawl du lieu tu API cho cac ky nang: Grammar, Reading, Listening, Writing
    """
    print(f"\n--- BAT DAU CRAWL KY NANG: {skill_name.upper()} ---")
    skill_dir = os.path.join(OUTPUT_DIR, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    
    consecutive_errors = 0
    downloaded_count = 0
    
    for item_id in range(1, max_id + 1):
        # Tranh bi block boi server, nghi nhe giua cac request
        time.sleep(REQUEST_DELAY)
        
        # Format API URL
        api_url = f"{BASE_URL}/{api_template}".replace("{id}", str(item_id))
        
        try:
            print(f"[{skill_name}] Dang goi API ID {item_id}: {api_url}")
            response = session.get(api_url, timeout=10)
            
            # Kiem tra neu bi redirect hoac server tra ve trang HTML dang nhap
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "application/json" not in content_type:
                    print(f"[{skill_name}] [Dung] Phien lam viec het han hoac da het de thi (Server tra ve HTML). Duyen ket thuc tai ID {item_id}.")
                    break
                    
                # Doc du lieu JSON sach
                data = clean_bom_and_load_json(response.text)
                
                # Kiem tra neu JSON rong hoac loi phia server
                if not data or (isinstance(data, dict) and data.get("success") is False):
                    print(f"[{skill_name}] API tra ve thong bao khong thanh cong tai ID {item_id}. Dung crawl.")
                    break
                
                # Ghi JSON vao file
                output_file = os.path.join(skill_dir, f"test_{item_id:03d}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"[{skill_name}] Luu file thanh cong: {os.path.basename(output_file)}")
                downloaded_count += 1
                consecutive_errors = 0
                
                # Quet va tai audio neu co trong file
                scan_and_download_audio_from_json(session, data)
                
            elif response.status_code == 404:
                print(f"[{skill_name}] API tra ve 404 tai ID {item_id}. Co the da het danh sach de thi.")
                break
            else:
                print(f"[{skill_name}] [Loi] API ID {item_id} tra ve Status Code: {response.status_code}")
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    print(f"[{skill_name}] Gap 3 loi lien tiep. Dung crawl.")
                    break
        except Exception as e:
            print(f"[{skill_name}] [Loi] Gap loi tai ID {item_id}: {e}")
            consecutive_errors += 1
            if consecutive_errors >= 3:
                print(f"[{skill_name}] Gap 3 loi lien tiep. Dung crawl.")
                break
                
    print(f"--- HOAN THANH KY NANG: {skill_name.upper()} | Tai duoc: {downloaded_count} de thi ---")

def extract_js_array(js_content, variable_name="questions"):
    pattern = r'(?:const|let|var)\s+' + re.escape(variable_name) + r'\s*=\s*\['
    match = re.search(pattern, js_content)
    if not match:
        return None
        
    start_idx = match.end() - 1
    bracket_count = 0
    end_idx = -1
    
    for idx in range(start_idx, len(js_content)):
        char = js_content[idx]
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_idx = idx + 1
                break
                
    if end_idx != -1:
        return js_content[start_idx:end_idx]
    return None

def tokenize_js_literal(js_str):
    tokens = []
    idx = 0
    length = len(js_str)
    
    while idx < length:
        char = js_str[idx]
        
        if char.isspace():
            idx += 1
            continue
            
        if char == '/' and idx + 1 < length and js_str[idx+1] == '/':
            idx += 2
            while idx < length and js_str[idx] != '\n':
                idx += 1
            continue
            
        if char in ('{', '}', '[', ']', ':', ',', '+'):
            tokens.append(('SEP', char))
            idx += 1
            continue
            
        if char in ('"', "'", '`'):
            quote_char = char
            idx += 1
            val_chars = []
            
            while idx < length:
                c = js_str[idx]
                if c == '\\' and idx + 1 < length:
                    val_chars.append(js_str[idx:idx+2])
                    idx += 2
                elif c == quote_char:
                    idx += 1
                    break
                else:
                    val_chars.append(c)
                    idx += 1
            
            raw_str = "".join(val_chars)
            if quote_char == '`':
                raw_str = raw_str.replace('\r', '').replace('\n', ' ')
            
            tokens.append(('STR', raw_str))
            continue
            
        if char.isdigit() or char == '-':
            start_pos = idx
            if char == '-':
                idx += 1
            while idx < length and (js_str[idx].isdigit() or js_str[idx] == '.'):
                idx += 1
            tokens.append(('NUM', js_str[start_pos:idx]))
            continue
            
        if char.isalpha() or char == '_':
            start_pos = idx
            while idx < length and (js_str[idx].isalnum() or js_str[idx] == '_'):
                idx += 1
            name = js_str[start_pos:idx]
            tokens.append(('ID', name))
            continue
            
        idx += 1
        
    return tokens

def fold_string_tokens(tokens):
    folded = []
    i = 0
    while i < len(tokens):
        if (tokens[i][0] == 'STR' and 
            i + 2 < len(tokens) and 
            tokens[i+1] == ('SEP', '+') and 
            tokens[i+2][0] == 'STR'):
            
            merged_val = tokens[i][1] + tokens[i+2][1]
            tokens[i+2] = ('STR', merged_val)
            i += 2
        else:
            folded.append(tokens[i])
            i += 1
            
    if len(folded) < len(tokens):
        return fold_string_tokens(folded)
    return folded

def parse_speaking_js_to_json(js_content):
    arr_str = extract_js_array(js_content)
    if not arr_str:
        return None
        
    tokens = tokenize_js_literal(arr_str)
    tokens = fold_string_tokens(tokens)
    
    json_parts = []
    for i in range(len(tokens)):
        tok_type, tok_val = tokens[i]
        
        if tok_type == 'SEP':
            if tok_val != '+':
                json_parts.append(tok_val)
        elif tok_type == 'STR':
            json_parts.append(json.dumps(tok_val, ensure_ascii=False))
        elif tok_type == 'NUM':
            json_parts.append(tok_val)
        elif tok_type == 'ID':
            is_key = False
            if i + 1 < len(tokens):
                next_tok_type, next_tok_val = tokens[i+1]
                if next_tok_type == 'SEP' and next_tok_val == ':':
                    is_key = True
            
            if is_key:
                json_parts.append(f'"{tok_val}"')
            else:
                if tok_val in ('true', 'false', 'null'):
                    json_parts.append(tok_val)
                else:
                    json_parts.append(f'"{tok_val}"')
                    
    json_str = "".join(json_parts)
    json_str = re.sub(r',\s*\]', ']', json_str)
    json_str = re.sub(r',\s*\}', '}', json_str)
    
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"[Speaking Parse Loi] JSON loads error: {e}")
        return None

def crawl_speaking_data(session):
    """
    Crawl ky nang Speaking tu cac file Javascript tinh
    """
    print(f"\n--- BAT DAU CRAWL KY NANG: SPEAKING ---")
    skill_dir = os.path.join(OUTPUT_DIR, "speaking")
    os.makedirs(skill_dir, exist_ok=True)
    
    downloaded_count = 0
    for part_id in range(1, 5):
        time.sleep(REQUEST_DELAY)
        js_url = f"{BASE_URL}/js/speaking/speaking_question{part_id}_practice.js"
        
        try:
            print(f"[Speaking] Dang tai file script Part {part_id}: {js_url}")
            response = session.get(js_url, timeout=10)
            if response.status_code == 200:
                js_content = response.text
                
                # 1. Luu tru file JS goc
                js_output_file = os.path.join(skill_dir, f"speaking_question{part_id}_practice.js")
                with open(js_output_file, "w", encoding="utf-8") as f:
                    f.write(js_content)
                print(f"[Speaking] Luu file JS goc thanh cong: {os.path.basename(js_output_file)}")
                
                # 2. Convert sang JSON de dung offline cau truc
                data = parse_speaking_js_to_json(js_content)
                if data:
                    json_output_file = os.path.join(skill_dir, f"speaking_part_{part_id}.json")
                    with open(json_output_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"[Speaking] Chuyen doi & luu JSON thanh cong: {os.path.basename(json_output_file)}")
                    downloaded_count += 1
                else:
                    print(f"[Speaking] [Loi] Khong phan tich duoc cau truc JavaScript cua Part {part_id}.")
            else:
                print(f"[Speaking] [Loi] Status {response.status_code} khi tai Part {part_id}")
        except Exception as e:
            print(f"[Speaking] [Loi] Gap su co khi tai Part {part_id}: {e}")
            
    print(f"--- HOAN THANH KY NANG: SPEAKING | Tai & chuyen doi thanh cong: {downloaded_count} Part ---")
