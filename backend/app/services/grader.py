"""
Service chấm điểm tự động cho các bài thi Aptis.
- Objective (Reading, Listening, Grammar): Chấm tự động bằng so sánh đáp án.
- Subjective (Writing, Speaking): Gọi Gemini API để nhận xét và chấm điểm.
"""
import json
from typing import Tuple, Optional, Dict
from app.models.exam import Test, Question, QuestionType, Skill


def _score_to_aptis_band(score: float, skill: str) -> str:
    """Quy đổi điểm phần trăm sang Band Aptis (theo thang điểm British Council)."""
    # Thang quy đổi tham khảo - có thể điều chỉnh theo skill
    if score >= 85:
        return "C"
    elif score >= 70:
        return "B2"
    elif score >= 55:
        return "B1"
    elif score >= 40:
        return "A2"
    else:
        return "A1"


def _grade_objective(questions: list, answers: Dict[str, str]) -> Tuple[float, int, int]:
    """Chấm điểm các câu trắc nghiệm/điền chỗ trống."""
    correct = 0
    total = 0

    for q in questions:
        if q.question_type in (QuestionType.multiple_choice, QuestionType.fill_blank, QuestionType.matching):
            if q.correct_answer is None:
                continue
            total += 1
            user_ans = answers.get(str(q.id), "").strip().lower()
            correct_ans = q.correct_answer.strip().lower()
            if user_ans == correct_ans:
                correct += 1

    return correct, total


def auto_grade(test: Test, answers: Dict[str, str]) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Chấm điểm bài thi và trả về (score, aptis_band, ai_feedback).
    """
    questions = test.questions

    # Phân loại câu hỏi khách quan và chủ quan
    objective_qs = [
        q for q in questions
        if q.question_type in (QuestionType.multiple_choice, QuestionType.fill_blank, QuestionType.matching)
    ]
    subjective_qs = [
        q for q in questions
        if q.question_type in (QuestionType.essay, QuestionType.audio_response)
    ]

    score = None
    aptis_band = None
    ai_feedback = None

    # --- Chấm điểm khách quan ---
    if objective_qs:
        correct, total = _grade_objective(objective_qs, answers)
        if total > 0:
            score = round((correct / total) * 100, 1)
            aptis_band = _score_to_aptis_band(score, test.skill.value)

    # --- Chấm điểm chủ quan (Writing / Speaking) ---
    if subjective_qs:
        try:
            ai_feedback = _grade_with_ai(test, subjective_qs, answers)
        except Exception as e:
            ai_feedback = f"[Không thể kết nối AI chấm điểm: {str(e)}]"

    return score, aptis_band, ai_feedback


def _generate_content_with_fallback(client, prompt: str) -> str:
    """Gọi Gemini API với danh sách model dự phòng linh hoạt nếu model chính gặp lỗi 503/429."""
    from app.core.config import settings

    models_to_try = [settings.GEMINI_MODEL, "gemini-2.0-flash", "gemini-1.5-flash"]
    seen = set()
    candidate_models = [m for m in models_to_try if not (m in seen or seen.add(m))]

    last_error = None
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            last_error = e

    if last_error:
        raise last_error
    return ""


def _grade_with_ai(test: Test, questions: list, answers: Dict[str, str]) -> str:
    """Gọi Google Gemini API để chấm điểm Writing/Speaking."""
    from google import genai
    from app.core.config import settings

    if not settings.GEMINI_API_KEY:
        return "Chức năng chấm điểm AI chưa được cấu hình. Vui lòng liên hệ admin."

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Xây dựng prompt chấm điểm
    prompt_parts = [
        f"""Bạn là giám khảo chấm thi Aptis (British Council) chuyên nghiệp.
Kỹ năng được chấm: **{test.skill.value.upper()}**
Bài thi: **{test.title}**

Hãy đánh giá bài làm của học viên theo các tiêu chí sau:
1. **Nội dung** (Content): Có trả lời đúng yêu cầu đề bài không?
2. **Ngôn ngữ** (Language): Ngữ pháp, từ vựng, cấu trúc câu có phù hợp không?
3. **Tổ chức** (Organisation): Cấu trúc bài có rõ ràng, mạch lạc không?
4. **Phong cách** (Register): Văn phong có phù hợp với loại bài không?

Cuối cùng, hãy:
- Đưa ra **Band điểm ước tính** (A1 / A2 / B1 / B2 / C) theo thang Aptis
- Đưa ra **điểm số** từ 0-100
- Đưa ra **nhận xét cụ thể** bằng tiếng Việt, chỉ ra điểm mạnh và điểm cần cải thiện

---
**Câu hỏi và bài làm của học viên:**
"""
    ]

    for q in questions:
        user_answer = answers.get(str(q.id), "(Học viên không trả lời)")
        prompt_parts.append(f"\n**Câu hỏi:** {q.content}")
        prompt_parts.append(f"\n**Bài làm:** {user_answer}\n")

    prompt_parts.append("\n---\n**Nhận xét và chấm điểm của giám khảo:**")

    return _generate_content_with_fallback(client, "".join(prompt_parts))


def analyze_result_with_ai(result, test: Test, questions: list) -> str:
    """
    Gọi Gemini API để phân tích chi tiết kết quả làm bài của học viên.
    Trả về HTML nhận xét sạch.
    """
    from google import genai
    from app.core.config import settings

    if not settings.GEMINI_API_KEY:
        return "<div class='alert alert-warning'>Chức năng AI chưa được cấu hình API Key. Vui lòng liên hệ admin.</div>"

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    # Phân biệt kỹ năng trắc nghiệm và tự luận
    is_objective = test.skill in (Skill.reading, Skill.listening, Skill.grammar)
    
    if is_objective:
        # Xây dựng báo cáo kết quả trắc nghiệm chi tiết để gửi cho AI
        prompt_parts = [
            f"""Bạn là một chuyên gia giáo dục và giám khảo thi tiếng Anh Aptis chuyên nghiệp của British Council.
Hãy phân tích kết quả bài thi **{test.title}** (Kỹ năng: **{test.skill.value.upper()}**) của học viên.
Điểm số đạt được: **{result.score}/100** (Band Aptis: **{result.aptis_band}**).
Thời gian làm bài: {f"{result.time_taken_seconds} giây" if result.time_taken_seconds else "Không ghi nhận"}.

Dưới đây là chi tiết từng câu hỏi trong bài làm của học viên:
"""
        ]
        
        # Sắp xếp các câu hỏi theo order_num
        sorted_qs = sorted(questions, key=lambda q: q.order_num)
        
        for q in sorted_qs:
            user_ans = (result.answers or {}).get(str(q.id)) or (result.answers or {}).get(q.id) or ""
            correct_ans = q.correct_answer or ""
            
            # Format đáp án để hiển thị
            user_ans_str = str(user_ans).strip()
            correct_ans_str = str(correct_ans).strip()
            
            is_correct = "ĐÚNG" if user_ans_str.lower() == correct_ans_str.lower() else "SAI"
            if not user_ans_str:
                user_ans_str = "(Học viên không trả lời)"
                is_correct = "SAI (Bỏ qua)"
                
            prompt_parts.append(f"""
---
- **Câu số {q.order_num}**:
  - **Nội dung câu hỏi**: {q.content}
  - **Đáp án đúng**: {correct_ans_str}
  - **Học viên chọn**: {user_ans_str} -> Kết quả: **{is_correct}**
  - **Giải thích**: {q.explanation or 'Chưa có giải thích'}
""")
            
        prompt_parts.append(f"""
---
Nhiệm vụ của bạn:
Hãy phân tích kết quả bài làm trên của học viên và viết một bài nhận xét chi tiết bằng tiếng Việt, bao gồm:
1. **Đánh giá tổng quan**: Nhận xét về kết quả chung của học viên (tỷ lệ đúng/sai, điểm mạnh, điểm yếu nổi bật, tốc độ làm bài).
2. **Phân tích chi tiết lỗi sai**: Chỉ ra những lỗi sai phổ biến hoặc những câu học viên trả lời sai. Giải thích rõ tại sao đáp án của học viên lại sai và tại sao đáp án đúng mới là chính xác (giải thích chi tiết về mặt ngữ pháp, cấu trúc câu, từ vựng hoặc kỹ năng đọc/nghe hiểu tương ứng). Chỉ ra bẫy hoặc nhầm lẫn phổ biến trong đề (nếu có).
3. **Lời khuyên học tập & Lộ trình khắc phục**: Đưa ra các gợi ý cụ thể để học viên cải thiện kỹ năng này, các mảng kiến thức ngữ pháp/từ vựng/kỹ năng cần ôn tập thêm dựa trên các câu trả lời sai.

Yêu cầu định dạng phản hồi:
- Trả về kết quả dưới dạng **đoạn mã HTML sạch**, không bao gồm bất kỳ phần bọc nào như ```html hoặc ``` ở đầu và cuối.
- Sử dụng các thẻ HTML cơ bản như `<p>`, `<ul>`, `<li>`, `<strong>`, `<br>`, `<span class='text-danger'>` cho câu sai/lỗi/nhược điểm, `<span class='text-success'>` cho câu đúng/lưu ý tốt/ưu điểm để định dạng kết quả hiển thị thật đẹp mắt trên trang web.
""")
    else:
        # Đối với Tự luận (Writing / Speaking)
        prompt_parts = [
            f"""Bạn là giám khảo chấm thi {test.skill.value.upper()} tiếng Anh Aptis chuyên nghiệp của British Council.
Hãy phân tích và nhận xét chi tiết bài làm dưới đây của học viên bằng tiếng Việt.

Tên bài thi: **{test.title}**
Kỹ năng: **{test.skill.value.upper()}**
Điểm số đạt được: **{result.score if result.score is not None else '–'}/100** (Band: **{result.aptis_band or '–'}**)

Bài làm của học viên:
"""
        ]
        
        for key, val in (result.answers or {}).items():
            prompt_parts.append(f"\n[{key}]:\n{val}\n")
            
        prompt_parts.append("""
---
Nhiệm vụ của bạn:
Hãy phân tích cặn kẽ bài làm và viết nhận xét chi tiết bằng tiếng Việt, bao gồm:
1. **Đánh giá chi tiết theo tiêu chí**: Đánh giá dựa trên 4 tiêu chí chuẩn của British Council (Nội dung - Content, Ngôn ngữ - Grammar & Vocabulary, Tổ chức - Cohesion & Coherence, Phong cách - Register).
2. **Phân tích lỗi sai chi tiết**: Chỉ ra các lỗi ngữ pháp, từ vựng, diễn đạt chưa chuẩn, giải thích tại sao chưa chuẩn và cung cấp câu gợi ý sửa lại (rewrite) tối ưu hơn.
3. **Lời khuyên cải thiện**: Đưa ra lời khuyên cụ thể để học viên có thể nâng cao band điểm.

Yêu cầu định dạng phản hồi:
- Trả về kết quả dưới dạng **đoạn mã HTML sạch**, không bao gồm bất kỳ phần bọc nào như ```html hoặc ``` ở đầu và cuối.
- Sử dụng các thẻ HTML cơ bản như `<p>`, `<ul>`, `<li>`, `<strong>`, `<br>`, `<span class='text-danger'>` cho lỗi sai/khuyết điểm, `<span class='text-success'>` cho câu đúng/gợi ý chuẩn/ưu điểm để định dạng kết quả hiển thị thật đẹp mắt trên trang web.
""")

    ai_response_text = _generate_content_with_fallback(client, "".join(prompt_parts))
    
    # Dọn dẹp các ký tự bao bọc nếu AI tự ý thêm vào
    if ai_response_text.startswith("```html"):
        ai_response_text = ai_response_text.split("```html")[1].split("```")[0].strip()
    elif ai_response_text.startswith("```"):
        ai_response_text = ai_response_text.split("```")[1].split("```")[0].strip()
        
    return ai_response_text
