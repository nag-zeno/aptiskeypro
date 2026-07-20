"""
Seed Script – AptisPro
======================
Đọc toàn bộ dữ liệu từ thư mục crawled_data/ và nạp vào cơ sở dữ liệu
thông qua SQLAlchemy models (Test + Question).

Cách chạy (từ thư mục backend/):
    python seed_data.py                  # nạp tất cả kỹ năng
    python seed_data.py --skill grammar  # chỉ nạp Grammar
    python seed_data.py --skill reading
    python seed_data.py --skill listening
    python seed_data.py --skill writing
    python seed_data.py --skill speaking
    python seed_data.py --reset          # xóa sạch DB rồi nạp lại

Lưu ý: Script phải được chạy từ thư mục backend/ để đường dẫn hoạt động đúng.
"""

import os
import sys
import json
import argparse

# Thêm backend root vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.exam import Test, Question, Skill, QuestionType
from app.models.payment import Transaction

# ─── Đường dẫn ────────────────────────────────────────────────────────────────
BACKEND_DIR  = os.path.dirname(os.path.abspath(__file__))
CRAWLED_DIR  = os.path.join(BACKEND_DIR, "..", "crawled_data")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_json(path: str) -> dict | list | None:
    """Đọc file JSON, trả None nếu lỗi."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  [!] Không đọc được {os.path.basename(path)}: {e}")
        return None


def _add_test(db, skill: Skill, title: str, description: str = "", is_vip: int = 0) -> Test:
    test = Test(skill=skill, title=title, description=description, is_vip=is_vip)
    db.add(test)
    db.flush()          # lấy test.id ngay mà không cần commit
    return test


def _add_question(
    db,
    test: Test,
    order_num: int,
    q_type: QuestionType,
    content: str,
    options: list | None = None,
    correct_answer: str | None = None,
    explanation: str | None = None,
    audio_url: str | None = None,
) -> Question:
    q = Question(
        test_id=test.id,
        order_num=order_num,
        question_type=q_type,
        content=content,
        options=options,
        correct_answer=correct_answer,
        explanation=explanation,
        audio_url=audio_url,
    )
    db.add(q)
    return q


# ─── GRAMMAR ──────────────────────────────────────────────────────────────────

def seed_grammar(db):
    """
    Mỗi file test_XXX.json = 1 bộ đề Grammar gồm nhiều phần:
      question1_list : điền từ (fill_blank) — đáp án đúng là question_answer[0]
      question2–6    : matching (chọn synonym / collocations)
    """
    skill_dir = os.path.join(CRAWLED_DIR, "grammar")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Grammar] Tìm thấy {len(files)} file đề thi.")

    for file_name in files:
        data = load_json(os.path.join(skill_dir, file_name))
        if not data:
            continue

        test_num = int(file_name.replace("test_", "").replace(".json", ""))
        test = _add_test(db, Skill.grammar, f"Grammar Test #{test_num:02d}",
                         "Bộ đề Grammar tổng hợp – Aptis")
        order = 1

        # Part 1: fill_blank (question1_list) — đáp án đúng là phần tử đầu tiên
        for item in data.get("question1_list", []):
            opts = item.get("question_answer", [])
            correct = opts[0] if opts else None
            _add_question(db, test, order, QuestionType.fill_blank,
                          item.get("question_ask", ""),
                          options=opts,
                          correct_answer=correct)
            order += 1

        # Part 2–6: matching (synonym / collocation)
        for part_key in ("question2_list", "question3_list", "question4_list",
                         "question5_list", "question6_list"):
            for item in data.get(part_key, []):
                # Một số part có question_orginal, một số có question_start + question_end
                if "question_orginal" in item:
                    content = item["question_orginal"]
                elif "question_start" in item:
                    content = (item.get("question_start", "") + " ___ " +
                               item.get("question_end", "")).strip()
                else:
                    content = str(item)

                opts = item.get("question_answer", [])
                correct = item.get("correct_answer")
                _add_question(db, test, order, QuestionType.matching,
                              content,
                              options=opts,
                              correct_answer=correct)
                order += 1

        db.commit()
        print(f"  ✔ {file_name}  →  {order - 1} câu hỏi")

    print(f"[Grammar] Hoàn tất – {len(files)} bộ đề.")


# ─── READING ──────────────────────────────────────────────────────────────────

def seed_reading(db):
    """
    Mỗi file test_XXX.json = 1 bộ đề Reading gồm 5 phần (Q1-Q5).
    """
    skill_dir = os.path.join(CRAWLED_DIR, "reading")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Reading] Tìm thấy {len(files)} file đề thi.")

    for file_name in files:
        data = load_json(os.path.join(skill_dir, file_name))
        if not data:
            continue

        test_num = int(file_name.replace("test_", "").replace(".json", ""))
        test = _add_test(db, Skill.reading, f"Reading Test #{test_num:02d}",
                         data.get("label", f"Bộ đề Reading #{test_num:02d}"))
        order = 1

        # Q1: fill_blank (questionStart + answerOptions + questionEnd)
        for item in data.get("questions1", []):
            content = (item.get("questionStart", "") + " ___ " +
                       item.get("questionEnd", "")).strip()
            opts = item.get("answerOptions", [])
            _add_question(db, test, order, QuestionType.fill_blank,
                          content, options=opts,
                          correct_answer=item.get("correctAnswer"))
            order += 1

        # Q2: sắp xếp câu (matching – trình tự đúng)
        q2_topic = data.get("question2Topic", "Ordering")
        q2_items = data.get("question2Content", [])
        if q2_items:
            # Lưu từng câu như 1 câu hỏi sắp xếp (nội dung = danh sách các câu)
            sentences_text = "\n".join(f"{i+1}. {it['text']}" for i, it in enumerate(q2_items))
            content = f"[Sắp xếp câu – {q2_topic}]\n{sentences_text}"
            # Không có đáp án chuẩn cố định trong JSON gốc → lưu essay để AI chấm
            _add_question(db, test, order, QuestionType.essay,
                          content)
            order += 1

        # Q3: sắp xếp đoạn (tương tự Q2)
        q3_topic = data.get("question3Topic", "Ordering")
        q3_items = data.get("question3Content", [])
        if q3_items:
            sentences_text = "\n".join(f"{i+1}. {it['text']}" for i, it in enumerate(q3_items))
            content = f"[Sắp xếp câu – {q3_topic}]\n{sentences_text}"
            _add_question(db, test, order, QuestionType.essay, content)
            order += 1

        # Q4: 4 người (A/B/C/D) – trắc nghiệm chọn người
        q4_questions = data.get("question4Content", [])
        q4_texts = data.get("question4Text", [])
        passage_html = " ".join(q4_texts)
        for item in q4_questions:
            content = passage_html + "\n\n" + item.get("question", "")
            opts = [o for o in item.get("options", []) if o]  # bỏ phần tử rỗng
            _add_question(db, test, order, QuestionType.multiple_choice,
                          content, options=opts,
                          correct_answer=item.get("answer"))
            order += 1

        # Q5: chọn tiêu đề phù hợp cho đoạn văn (matching)
        q5_topic   = data.get("question5Topic", "")
        q5_paras   = data.get("paragraph_question5", [])
        q5_options = data.get("options", [])
        # Mỗi đoạn văn → 1 câu hỏi matching
        for i, para in enumerate(q5_paras):
            _add_question(db, test, order, QuestionType.matching,
                          f"[{q5_topic}] Đoạn {i+1}: {para}",
                          options=[o for o in q5_options if o])
            order += 1

        db.commit()
        print(f"  ✔ {file_name}  →  {order - 1} câu hỏi")

    print(f"[Reading] Hoàn tất – {len(files)} bộ đề.")


# ─── LISTENING ────────────────────────────────────────────────────────────────

def seed_listening(db):
    """
    Mỗi file test_XXX.json = 1 bộ đề Listening gồm 3 phần:
      q1_13 : 13 câu multiple_choice (kèm audioUrl)
      q14   : 1 câu matching chọn person (A/B/C/D)
      q15   : câu Agree/Disagree (Man/Woman/Both)
      q16_17: 2 đoạn nghe, mỗi đoạn 2 câu multiple_choice
    """
    skill_dir = os.path.join(CRAWLED_DIR, "listening")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Listening] Tìm thấy {len(files)} file đề thi.")

    for file_name in files:
        data = load_json(os.path.join(skill_dir, file_name))
        if not data:
            continue

        test_num = int(file_name.replace("test_", "").replace(".json", ""))
        test = _add_test(db, Skill.listening, f"Listening Test #{test_num:02d}",
                         "Bộ đề Listening tổng hợp – Aptis")
        order = 1

        # Q1-13: multiple_choice kèm audio
        for item in data.get("q1_13", []):
            _add_question(db, test, order, QuestionType.multiple_choice,
                          item.get("question", ""),
                          options=item.get("options", []),
                          correct_answer=item.get("correctAnswer"),
                          explanation=item.get("transcript"),
                          audio_url=item.get("audioUrl"))
            order += 1

        # Q14: matching – chọn người phát biểu
        q14 = data.get("q14", {})
        if q14:
            opts = q14.get("options", [])
            content = (f"[{q14.get('topic', 'Q14')}]\n"
                       f"Nghe và chọn người phát biểu phù hợp.\n"
                       f"Options: {', '.join(o for o in opts if o)}\n"
                       f"Transcript:\n{q14.get('transcript', '')}")
            _add_question(db, test, order, QuestionType.matching,
                          content,
                          options=[o for o in opts if o],
                          audio_url=q14.get("audioUrl"),
                          explanation=q14.get("transcript"))
            order += 1

        # Q15: Man / Woman / Both
        q15 = data.get("q15", {})
        if q15:
            questions_list = q15.get("questions", [])
            correct_list   = q15.get("correctAnswer", [])
            for i, q_text in enumerate(questions_list):
                correct = correct_list[i] if i < len(correct_list) else None
                _add_question(db, test, order, QuestionType.multiple_choice,
                              f"[{q15.get('topic', 'Q15')}] {q_text}",
                              options=["Man", "Woman", "Both"],
                              correct_answer=correct,
                              audio_url=q15.get("audioUrl"),
                              explanation=q15.get("transcript"))
                order += 1

        # Q16-17: 2 đoạn, mỗi đoạn 2 câu
        for passage in data.get("q16_17", []):
            audio_url  = passage.get("audioUrl")
            transcript = passage.get("transcript", "")
            topic      = passage.get("topic", "")
            for q_item in passage.get("questions", []):
                _add_question(db, test, order, QuestionType.multiple_choice,
                              f"[{topic}] {q_item.get('question', '')}",
                              options=q_item.get("options", []),
                              audio_url=audio_url,
                              explanation=transcript)
                order += 1

        db.commit()
        print(f"  ✔ {file_name}  →  {order - 1} câu hỏi")

    print(f"[Listening] Hoàn tất – {len(files)} bộ đề.")


# ─── WRITING ──────────────────────────────────────────────────────────────────

def seed_writing(db):
    """
    Mỗi file test_XXX.json = 1 bộ đề Writing gồm 4 tasks (Q1-Q4).
    Tất cả đều là essay (chấm bằng AI).
    """
    skill_dir = os.path.join(CRAWLED_DIR, "writing")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Writing] Tìm thấy {len(files)} file đề thi.")

    for file_name in files:
        data = load_json(os.path.join(skill_dir, file_name))
        if not data:
            continue

        test_num = int(file_name.replace("test_", "").replace(".json", ""))
        club_name = data.get("club_name", "")
        test = _add_test(db, Skill.writing,
                         f"Writing Test #{test_num:02d}" + (f" – {club_name}" if club_name else ""),
                         "Bộ đề Writing Aptis – bao gồm 4 tasks (short answers, paragraph, emails, & formal email)")
        order = 1

        # Q1: 5 câu trả lời ngắn (short answers – lưu chung 1 câu essay)
        q1_dict = data.get("questions1", {})
        q1_answers = data.get("questions1_answer", {})
        if q1_dict:
            questions_text = "\n".join(f"• {v}" for v in q1_dict.values())
            sample_answers = "\n".join(f"• {v}" for v in q1_answers.values())
            content = f"[Q1 – Short Answers]\n{questions_text}"
            _add_question(db, test, order, QuestionType.essay,
                          content, explanation=f"Gợi ý trả lời:\n{sample_answers}")
            order += 1

        # Q2: paragraph (viết 1 đoạn)
        q2_dict = data.get("questions2", {})
        q2_answers = data.get("questions2_answer", {})
        if q2_dict:
            content = f"[Q2 – Paragraph] {list(q2_dict.values())[0] if q2_dict else ''}"
            sample = list(q2_answers.values())[0] if q2_answers else ""
            _add_question(db, test, order, QuestionType.essay,
                          content, explanation=f"Gợi ý trả lời:\n{sample}")
            order += 1

        # Q3: 3 câu hỏi (viết đoạn trả lời tình huống)
        q3_dict = data.get("questions3", {})
        q3_answers = data.get("questions3_answer", {})
        for key, question_text in q3_dict.items():
            sample = q3_answers.get(key + "_answer", "")
            _add_question(db, test, order, QuestionType.essay,
                          f"[Q3] {question_text}",
                          explanation=f"Gợi ý: {sample}")
            order += 1

        # Q4: 2 email tasks (informal + formal)
        main_prompt = data.get("questions4_main", "")
        q4_1 = data.get("question4_1_text", "")
        q4_2 = data.get("question4_2_text", "")
        q4_1_answer = data.get("question4_1_text_answer", "")
        q4_2_answer = data.get("question4_2_text_answer", "")

        if q4_1:
            content = f"[Q4a – Informal Email]\n{main_prompt}\n\nYêu cầu: {q4_1}"
            _add_question(db, test, order, QuestionType.essay,
                          content, explanation=f"Gợi ý:\n{q4_1_answer}")
            order += 1

        if q4_2:
            content = f"[Q4b – Formal Email]\n{main_prompt}\n\nYêu cầu: {q4_2}"
            _add_question(db, test, order, QuestionType.essay,
                          content, explanation=f"Gợi ý:\n{q4_2_answer}")
            order += 1

        db.commit()
        print(f"  ✔ {file_name}  →  {order - 1} câu hỏi")

    print(f"[Writing] Hoàn tất – {len(files)} bộ đề.")


# ─── SPEAKING ─────────────────────────────────────────────────────────────────

def seed_speaking(db):
    """
    4 file JSON, mỗi file = 1 Part Speaking.
    Mỗi phần tử = 1 câu hỏi nói (audio_response).
    Đáp án mẫu (answer1, answer2) lưu vào explanation.
    """
    skill_dir = os.path.join(CRAWLED_DIR, "speaking")
    part_files = [
        ("speaking_part_1.json", 1, "Câu hỏi và trả lời cá nhân (Personal questions)"),
        ("speaking_part_2.json", 2, "Mô tả ảnh / Hỏi-đáp (Describe & Discuss)"),
        ("speaking_part_3.json", 3, "Thảo luận chủ đề xã hội (Topic Discussion)"),
        ("speaking_part_4.json", 4, "Thảo luận chuyên sâu (In-depth Discussion)"),
    ]
    print(f"\n[Speaking] Tìm thấy 4 file Part Speaking.")

    for file_name, part_num, description in part_files:
        path = os.path.join(skill_dir, file_name)
        if not os.path.exists(path):
            print(f"  [!] Không tìm thấy {file_name}, bỏ qua.")
            continue

        data = load_json(path)
        if not data or not isinstance(data, list):
            continue

        test = _add_test(db, Skill.speaking,
                         f"Speaking Part {part_num}",
                         description)
        order = 1

        for item in data:
            # Part 1 & 4: dùng key "question" + "answer1"/"answer2"
            if "question" in item:
                question_text = item.get("question", "")
                if not question_text:
                    continue
                sample_parts = []
                if item.get("answer1"):
                    sample_parts.append(f"Mẫu 1: {item['answer1']}")
                if item.get("answer2"):
                    sample_parts.append(f"Mẫu 2: {item['answer2']}")
                explanation = "\n\n".join(sample_parts) if sample_parts else None
                image_url = item.get("urlpic1") or item.get("urlpic")
                _add_question(db, test, order, QuestionType.audio_response,
                              question_text,
                              explanation=explanation,
                              audio_url=image_url)   # tái dùng trường audio_url để lưu image URL
                order += 1

            # Part 2 & 3: mỗi item có urlpic1 + question1/question2/question3
            elif any(f"question{i}" in item for i in range(1, 5)):
                image_url = item.get("urlpic1") or item.get("urlpic2") or ""
                for q_idx in range(1, 5):
                    q_key  = f"question{q_idx}"
                    ans_key = f"question{q_idx}_answer"
                    if q_key not in item:
                        continue
                    question_text = item[q_key]
                    sample_answer = item.get(ans_key, "")
                    explanation = f"Gợi ý: {sample_answer}" if sample_answer else None
                    # Chỉ câu hỏi đầu tiên mới kèm ảnh
                    _add_question(db, test, order, QuestionType.audio_response,
                                  question_text,
                                  explanation=explanation,
                                  audio_url=image_url if q_idx == 1 else None)
                    order += 1

        db.commit()
        print(f"  ✔ {file_name}  →  {order - 1} câu hỏi")

    print(f"[Speaking] Hoàn tất – 4 Part.")


# ─── RESET ────────────────────────────────────────────────────────────────────

def reset_database():
    """Xóa sạch tất cả dữ liệu câu hỏi / đề thi (giữ nguyên Users và Transactions)."""
    db = SessionLocal()
    try:
        print("[Reset] Đang xóa dữ liệu cũ...")
        db.query(Question).delete()
        db.query(Test).delete()
        db.commit()
        print("[Reset] Xóa xong toàn bộ Tests và Questions.")
    finally:
        db.close()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AptisPro – Seed dữ liệu câu hỏi vào database")
    parser.add_argument("--skill", choices=["grammar", "reading", "listening", "writing", "speaking"],
                        help="Chỉ nạp kỹ năng cụ thể (mặc định: tất cả)")
    parser.add_argument("--reset", action="store_true",
                        help="Xóa sạch Tests/Questions trước khi nạp lại")
    args = parser.parse_args()

    # Tạo bảng nếu chưa có
    Base.metadata.create_all(bind=engine)

    if args.reset:
        reset_database()

    db = SessionLocal()
    try:
        skill_map = {
            "grammar":   seed_grammar,
            "reading":   seed_reading,
            "listening": seed_listening,
            "writing":   seed_writing,
            "speaking":  seed_speaking,
        }

        if args.skill:
            runners = {args.skill: skill_map[args.skill]}
        else:
            runners = skill_map

        print("=" * 60)
        print("       AptisPro – BẮT ĐẦU SEED DỮ LIỆU")
        print("=" * 60)

        for skill_name, fn in runners.items():
            fn(db)

        # Tổng kết
        total_tests     = db.query(Test).count()
        total_questions = db.query(Question).count()
        print("\n" + "=" * 60)
        print("       AptisPro – SEED HOÀN THÀNH!")
        print(f"       Tổng số bộ đề  : {total_tests}")
        print(f"       Tổng số câu hỏi: {total_questions}")
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"\n[LỖI] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
