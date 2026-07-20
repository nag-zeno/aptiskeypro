import os
import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from google import genai
from google.genai import types as genai_types

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user, get_password_hash, verify_password, create_access_token
from app.models.user import User, UserRole
from app.models.exam import Test, Skill

router = APIRouter(tags=["Compatibility"])

# Đường dẫn thư mục crawled_data
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CRAWLED_DIR = os.path.join(BACKEND_DIR, "..", "crawled_data")

# ─── AUTHENTICATION ───────────────────────────────────────────────────────────

@router.post("/login")
def compat_login(
    response: Response,
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint đăng nhập tương thích với form của frontend tĩnh.
    Nhận dữ liệu dạng Form urlencoded (username là email).
    Lưu JWT Token vào HttpOnly cookie và trả về JSON hướng dẫn chuyển hướng.
    """
    user = db.query(User).filter(User.email == username.lower()).first()
    if not user or not verify_password(password, user.password_hash):
        return {
            "success": False,
            "message": "Email hoặc mật khẩu không chính xác!"
        }
        
    if not user.is_active:
        return {
            "success": False,
            "message": "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Admin."
        }

    # Tạo JWT Token
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Đặt cookie access_token để tự động gửi kèm các request sau
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )

    # Kiểm tra trạng thái hết hạn VIP
    is_expired = False
    if user.vip_expires_at:
        now = datetime.now(timezone.utc)
        if user.vip_expires_at.replace(tzinfo=timezone.utc) < now:
            is_expired = True

    return {
        "success": True,
        "message": "Đăng nhập thành công!",
        "redirect": "/home.html",
        "expired": is_expired
    }


@router.get("/logout")
def compat_logout(response: Response):
    """Đăng xuất, xóa cookie token."""
    response.delete_cookie("access_token")
    return {
        "success": True,
        "message": "Đăng xuất thành công!"
    }


@router.get("/api/me")
def compat_get_me(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin người dùng tương thích với common.js.
    """
    # Mặc định thời hạn xa xôi cho admin, hoặc ngày hết hạn VIP cho học viên
    expired_at = "2099-12-31T23:59:59.000Z"
    if current_user.role != UserRole.admin:
        if current_user.vip_expires_at:
            expired_at = current_user.vip_expires_at.replace(tzinfo=timezone.utc).isoformat()
        else:
            # Nếu chưa nâng VIP, coi như hết hạn từ năm ngoái
            expired_at = "2025-01-01T00:00:00.000Z"

    return {
        "success": True,
        "email": current_user.email,
        "fullName": current_user.full_name,
        "isAdmin": current_user.role == UserRole.admin,
        "status": "Học viên chính thức" if expired_at != "2099-12-31T23:59:59.000Z" else "Chưa nâng cấp VIP",
        "expiredAt": expired_at
    }


# ─── COMPATIBILITY DATA ENDPOINTS (Phục vụ JSON từ crawled_data) ─────────────

def get_json_response(sub_path: str) -> JSONResponse:
    """Đọc tệp JSON từ crawled_data và trả về JSONResponse."""
    full_path = os.path.join(CRAWLED_DIR, *sub_path.split("/"))
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu")
    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    from fastapi.responses import JSONResponse
    return JSONResponse(content=data)


def check_test_vip(skill: Skill, test_id: int, db: Session, user: User):
    """Kiểm tra xem bộ đề có phải VIP hay không, nếu có thì check thời hạn VIP của user."""
    # Tìm bộ đề tương ứng trong DB dựa vào skill và số thứ tự
    test = db.query(Test).filter(
        Test.skill == skill,
        Test.title.like(f"%#{test_id:02d}%") | Test.title.like(f"%#{test_id}%")
    ).first()
    
    if test and test.is_vip:
        # Kiểm tra VIP của user
        now = datetime.now(timezone.utc)
        if not user.vip_expires_at or user.vip_expires_at.replace(tzinfo=timezone.utc) < now:
            raise HTTPException(
                status_code=403,
                detail="Bộ đề này dành cho học viên VIP. Vui lòng nâng cấp tài khoản."
            )


@router.get("/api/grammar-data/{test_id}")
def get_grammar_data(test_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_test_vip(Skill.grammar, test_id, db, user)
    return get_json_response(f"grammar/test_{test_id:03d}.json")


@router.get("/api/reading-test-data/{test_id}")
def get_reading_data(test_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_test_vip(Skill.reading, test_id, db, user)
    return get_json_response(f"reading/test_{test_id:03d}.json")


@router.get("/api/listeningkey-data/{test_id}")
def get_listening_data(test_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_test_vip(Skill.listening, test_id, db, user)
    return get_json_response(f"listening/test_{test_id:03d}.json")


@router.get("/api/writingkey-data/{test_id}")
def get_writing_data(test_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    check_test_vip(Skill.writing, test_id, db, user)
    return get_json_response(f"writing/test_{test_id:03d}.json")


# ─── QUESTIONS COMPAT DATA (Học lẻ từng câu) ───────────────────────────────

@router.get("/api/reading-question1-data")
def get_reading_q1(user: User = Depends(get_current_user)): return get_json_response("reading/question1.json")

@router.get("/api/reading-question2-data")
def get_reading_q2(user: User = Depends(get_current_user)): return get_json_response("reading/question2.json")

@router.get("/api/reading-question4-data")
def get_reading_q4(user: User = Depends(get_current_user)): return get_json_response("reading/question4.json")

@router.get("/api/reading-question5-data")
def get_reading_q5(user: User = Depends(get_current_user)): return get_json_response("reading/question5.json")

@router.get("/api/listening-question1-13-data")
def get_listening_q1_13(user: User = Depends(get_current_user)): return get_json_response("listening/question1_13.json")

@router.get("/api/listening-question14-data")
def get_listening_q14(user: User = Depends(get_current_user)): return get_json_response("listening/question14.json")

@router.get("/api/listening-question15-data")
def get_listening_q15(user: User = Depends(get_current_user)): return get_json_response("listening/question15.json")

@router.get("/api/listening-question16-17-data")
def get_listening_q16_17(user: User = Depends(get_current_user)): return get_json_response("listening/question16_17.json")


# ─── WRITING AI GRADING (/ask) ────────────────────────────────────────────────

@router.post("/ask")
async def compat_ask_ai(request: Request, user: User = Depends(get_current_user)):
    """
    Endpoint chấm điểm bài viết tự động qua Gemini AI.
    """
    body = await request.json()
    question_payload = body.get("question", "")
    
    if not question_payload:
        return {"error": "Nội dung bài làm không được để trống"}

    if not settings.GEMINI_API_KEY:
        return {"answer": "<div class='alert alert-warning'>Chức năng AI chưa được cấu hình API Key. Vui lòng liên hệ Admin.</div>"}

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""Bạn là giám khảo chấm thi viết tiếng Anh Aptis (British Council) chuyên nghiệp.
Hãy phân tích, chấm điểm và nhận xét chi tiết bài làm viết dưới đây của học viên bằng tiếng Việt.

Cấu trúc bài làm gửi kèm bao gồm các phần:
- Q1 (Short Answers)
- Q2 (Paragraph)
- Q3 (Three questions)
- Q4 (Emails: Informal & Formal)

Hãy chấm điểm theo các tiêu chí:
1. **Nội dung** (Content)
2. **Ngôn ngữ** (Grammar & Vocabulary)
3. **Tổ chức** (Cohesion & Coherence)
4. **Phong cách** (Register - phù hợp thư trang trọng/thân mật)

Đưa ra:
- **Band điểm dự kiến** cho từng Task (A1, A2, B1, B2, C) và tổng điểm ước lượng (0-50).
- **Phân tích lỗi sai** (ngữ pháp, cách dùng từ) và viết lại câu gợi ý chuẩn hơn cho học viên.
- Nhận xét bằng tiếng Việt. Hãy trả về kết quả định dạng **HTML sạch** (không cần bọc trong thẻ ```html...```, chỉ dùng các thẻ <p>, <ul>, <li>, <strong>, <br>, <span class='text-danger'> để bôi đỏ lỗi, v.v.) để hiển thị đẹp mắt trên giao diện web.

Bài làm của học viên:
{question_payload}
"""
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )
        ai_response_text = response.text
        
        # Clean markdown code block wraps if model generated them
        if ai_response_text.startswith("```html"):
            ai_response_text = ai_response_text.split("```html")[1].split("```")[0].strip()
        elif ai_response_text.startswith("```"):
            ai_response_text = ai_response_text.split("```")[1].split("```")[0].strip()
            
        return {"answer": ai_response_text}
    except Exception as e:
        return {"error": f"Lỗi gọi Gemini AI: {str(e)}"}


# ─── SPEAKING JS COMPAT ROUTE (Sửa lỗi thiếu thư mục js/speaking) ─────────────

from fastapi.responses import FileResponse

@router.get("/js/speaking/{filename}")
def get_compat_speaking_js(filename: str):
    file_path = os.path.join(CRAWLED_DIR, "speaking", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Không tìm thấy tệp JS")


# ─── SAVE TEST RESULT COMPATIBILITY ENDPOINT ─────────────────────────────────

from pydantic import BaseModel
from app.models.exam import UserResult
from app.schemas.exam import ResultDetail
from app.routers.exam import _build_result_detail

class CompatSaveResultPayload(BaseModel):
    skill: str
    test_id: int
    score: float
    aptis_band: str
    answers: dict
    ai_feedback: Optional[str] = None
    time_taken_seconds: Optional[int] = None

@router.post("/api/compat/save-result", response_model=ResultDetail)
def compat_save_result(
    payload: CompatSaveResultPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lưu kết quả bài thi từ frontend gửi lên (chấm điểm sẵn).
    Tự động tìm kiếm bộ đề tương ứng trong DB bằng skill và số thứ tự test_id.
    """
    # Map tên skill sang Enum Skill
    skill_enum = None
    for sk in Skill:
        if sk.value == payload.skill.lower():
            skill_enum = sk
            break
            
    if not skill_enum:
        raise HTTPException(status_code=400, detail=f"Kỹ năng '{payload.skill}' không hợp lệ.")

    # Tìm bộ đề tương ứng
    test = db.query(Test).filter(
        Test.skill == skill_enum,
        Test.title.like(f"%#{payload.test_id:02d}%") | Test.title.like(f"%#{payload.test_id}%")
    ).first()

    db_test_id = test.id if test else 1  # dự phòng

    result = UserResult(
        user_id=current_user.id,
        test_id=db_test_id,
        score=payload.score,
        aptis_band=payload.aptis_band,
        answers=payload.answers,
        ai_feedback=payload.ai_feedback,
        time_taken_seconds=payload.time_taken_seconds
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return _build_result_detail(result, db)

