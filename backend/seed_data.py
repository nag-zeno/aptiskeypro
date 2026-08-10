# -*- coding: utf-8 -*-
import sys
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
Seed Script â€“ AptisPro
======================
Ä á» c toÃ n bá»™ dá»¯ liá»‡u tá»« thÆ° má»¥c crawled_data/ vÃ  náº¡p vÃ o cÆ¡ sá»Ÿ dá»¯ liá»‡u
thÃ´ng qua SQLAlchemy models (Test + Question).

CÃ¡ch cháº¡y (tá»« thÆ° má»¥c backend/):
    python seed_data.py                  # náº¡p táº¥t cáº£ ká»¹ nÄƒng
    python seed_data.py --skill grammar  # chá»‰ náº¡p Grammar
    python seed_data.py --skill reading
    python seed_data.py --skill listening
    python seed_data.py --skill writing
    python seed_data.py --skill speaking
    python seed_data.py --reset          # xÃ³a sáº¡ch DB rá»“i náº¡p láº¡i

LÆ°u Ã½: Script pháº£i Ä‘Æ°á»£c cháº¡y tá»« thÆ° má»¥c backend/ Ä‘á»ƒ Ä‘Æ°á» ng dáº«n hoáº¡t Ä‘á»™ng Ä‘Ãºng.
"""

import os
import sys
import json
import argparse

# ThÃªm backend root vÃ o sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.exam import Test, Question, Skill, QuestionType
from app.models.payment import Transaction

# âââ ÄÆ°á»ng dáº«n ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
BACKEND_DIR  = os.path.dirname(os.path.abspath(__file__))
CRAWLED_DIR  = os.path.join(BACKEND_DIR, "..", "crawled_data")

# âââ Helpers ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def load_json(path: str) -> dict | list | None:
    """Äá»c file JSON, tráº£ None náº¿u lá»i."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  [!] KhÃ´ng Äá»c ÄÆ°á»£c {os.path.basename(path)}: {e}")
        return None


def _add_test(db, skill: Skill, title: str, description: str = "", is_vip: int = 0) -> Test:
    test = Test(skill=skill, title=title, description=description, is_vip=is_vip)
    db.add(test)
    db.flush()          # láº¥y test.id ngay mÃ  khÃ´ng cáº§n commit
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


# âââ GRAMMAR ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def seed_grammar(db):
    """
    Má»i file test_XXX.json = 1 bá» Äá» Grammar gá»m nhiá»u pháº§n:
      question1_list : Äiá»n tá»« (fill_blank) â ÄÃ¡p Ã¡n ÄÃºng lÃ  question_answer[0]
      question2â6    : matching (chá»n synonym / collocations)
    """
    skill_dir = os.path.join(CRAWLED_DIR, "grammar")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Grammar] TÃ¬m tháº¥y {len(files)} file Äá» thi.")

    for file_name in files:
        data = load_json(os.path.join(skill_dir, file_name))
        if not data:
            continue

        test_num = int(file_name.replace("test_", "").replace(".json", ""))
        test = _add_test(db, Skill.grammar, f"Grammar Test #{test_num:02d}",
                         "Bá» Äá» Grammar tá»ng há»£p â Aptis")
        order = 1

        # Part 1: fill_blank (question1_list) â ÄÃ¡p Ã¡n ÄÃºng lÃ  pháº§n tá»­ Äáº§u tiÃªn
        for item in data.get("question1_list", []):
            opts = item.get("question_answer", [])
            correct = opts[0] if opts else None
            _add_question(db, test, order, QuestionType.fill_blank,
                          item.get("question_ask", ""),
                          options=opts,
                          correct_answer=correct)
            order += 1

        # Part 2â6: matching (synonym / collocation)
        for part_key in ("question2_list", "question3_list", "question4_list",
                         "question5_list", "question6_list"):
            for item in data.get(part_key, []):
                # Má»t sá» part cÃ³ question_orginal, má»t sá» cÃ³ question_start + question_end
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
        print(f"  â {file_name}  â  {order - 1} cÃ¢u há»i")

    print(f"[Grammar] HoÃ n táº¥t â {len(files)} bá» Äá».")


# âââ READING ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def seed_reading(db):
    """
    Má»i file test_XXX.json = 1 bá» Äá» Reading gá»m 5 pháº§n (Q1-Q5).
    """
    skill_dir = os.path.join(CRAWLED_DIR, "reading")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Reading] TÃ¬m tháº¥y {len(files)} file Äá» thi.")

    for file_name in files:
        data = load_json(os.path.join(skill_dir, file_name))
        if not data:
            continue

        test_num = int(file_name.replace("test_", "").replace(".json", ""))
        test = _add_test(db, Skill.reading, f"Reading Test #{test_num:02d}",
                         data.get("label", f"Bá» Äá» Reading #{test_num:02d}"))
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

        # Q2: sáº¯p xáº¿p cÃ¢u (matching â trÃ¬nh tá»± ÄÃºng)
        q2_topic = data.get("question2Topic", "Ordering")
        q2_items = data.get("question2Content", [])
        if q2_items:
            # LÆ°u tá»«ng cÃ¢u nhÆ° 1 cÃ¢u há»i sáº¯p xáº¿p (ná»i dung = danh sÃ¡ch cÃ¡c cÃ¢u)
            sentences_text = "\n".join(f"{i+1}. {it['text']}" for i, it in enumerate(q2_items))
            content = f"[Sáº¯p xáº¿p cÃ¢u â {q2_topic}]\n{sentences_text}"
            # KhÃ´ng cÃ³ ÄÃ¡p Ã¡n chuáº©n cá» Äá»nh trong JSON gá»c â lÆ°u essay Äá» AI cháº¥m
            _add_question(db, test, order, QuestionType.essay,
                          content)
            order += 1

        # Q3: sáº¯p xáº¿p Äoáº¡n (tÆ°Æ¡ng tá»± Q2)
        q3_topic = data.get("question3Topic", "Ordering")
        q3_items = data.get("question3Content", [])
        if q3_items:
            sentences_text = "\n".join(f"{i+1}. {it['text']}" for i, it in enumerate(q3_items))
            content = f"[Sáº¯p xáº¿p cÃ¢u â {q3_topic}]\n{sentences_text}"
            _add_question(db, test, order, QuestionType.essay, content)
            order += 1

        # Q4: 4 ngÆ°á»i (A/B/C/D) â tráº¯c nghiá»m chá»n ngÆ°á»i
        q4_questions = data.get("question4Content", [])
        q4_texts = data.get("question4Text", [])
        passage_html = " ".join(q4_texts)
        for item in q4_questions:
            content = passage_html + "\n\n" + item.get("question", "")
            opts = [o for o in item.get("options", []) if o]  # bá» pháº§n tá»­ rá»ng
            _add_question(db, test, order, QuestionType.multiple_choice,
                          content, options=opts,
                          correct_answer=item.get("answer"))
            order += 1

        # Q5: chá»n tiÃªu Äá» phÃ¹ há»£p cho Äoáº¡n vÄn (matching)
        q5_topic   = data.get("question5Topic", "")
        q5_paras   = data.get("paragraph_question5", [])
        q5_options = data.get("options", [])
        # Má»i Äoáº¡n vÄn â 1 cÃ¢u há»i matching
        for i, para in enumerate(q5_paras):
            _add_question(db, test, order, QuestionType.matching,
                          f"[{q5_topic}] Äoáº¡n {i+1}: {para}",
                          options=[o for o in q5_options if o])
            order += 1

        db.commit()
        print(f"  â {file_name}  â  {order - 1} cÃ¢u há»i")

    print(f"[Reading] HoÃ n táº¥t â {len(files)} bá» Äá».")


# âââ LISTENING ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def seed_listening(db):
    """
    Má»i file test_XXX.json = 1 bá» Äá» Listening gá»m 3 pháº§n:
      q1_13 : 13 cÃ¢u multiple_choice (kÃ¨m audioUrl)
      q14   : 1 cÃ¢u matching chá»n person (A/B/C/D)
      q15   : cÃ¢u Agree/Disagree (Man/Woman/Both)
      q16_17: 2 Äoáº¡n nghe, má»i Äoáº¡n 2 cÃ¢u multiple_choice
    """
    skill_dir = os.path.join(CRAWLED_DIR, "listening")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Listening] TÃ¬m tháº¥y {len(files)} file Äá» thi.")

    for file_name in files:
        data = load_json(os.path.join(skill_dir, file_name))
        if not data:
            continue

        test_num = int(file_name.replace("test_", "").replace(".json", ""))
        test = _add_test(db, Skill.listening, f"Listening Test #{test_num:02d}",
                         "Bá» Äá» Listening tá»ng há»£p â Aptis")
        order = 1

        # Q1-13: multiple_choice kÃ¨m audio
        for item in data.get("q1_13", []):
            _add_question(db, test, order, QuestionType.multiple_choice,
                          item.get("question", ""),
                          options=item.get("options", []),
                          correct_answer=item.get("correctAnswer"),
                          explanation=item.get("transcript"),
                          audio_url=item.get("audioUrl"))
            order += 1

        # Q14: matching â chá»n ngÆ°á»i phÃ¡t biá»u
        q14 = data.get("q14", {})
        if q14:
            opts = q14.get("options", [])
            content = (f"[{q14.get('topic', 'Q14')}]\n"
                       f"Nghe vÃ  chá»n ngÆ°á»i phÃ¡t biá»u phÃ¹ há»£p.\n"
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

        # Q16-17: 2 Äoáº¡n, má»i Äoáº¡n 2 cÃ¢u
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
        print(f"  â {file_name}  â  {order - 1} cÃ¢u há»i")

    print(f"[Listening] HoÃ n táº¥t â {len(files)} bá» Äá».")


# âââ WRITING ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def seed_writing(db):
    """
    Má»i file test_XXX.json = 1 bá» Äá» Writing gá»m 4 tasks (Q1-Q4).
    Táº¥t cáº£ Äá»u lÃ  essay (cháº¥m báº±ng AI).
    """
    skill_dir = os.path.join(CRAWLED_DIR, "writing")
    files = sorted(f for f in os.listdir(skill_dir) if f.startswith("test_") and f.endswith(".json"))
    print(f"\n[Writing] TÃ¬m tháº¥y {len(files)} file Äá» thi.")

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


# ——— SPEAKING —————————————————————————————————————————————————————————————————

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
    print("\n[Speaking] Tìm thấy 4 file Part Speaking.")

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
                              audio_url=image_url)


# --- MAIN ---

def main():
    parser = argparse.ArgumentParser(description="AptisPro - Seed data")
    parser.add_argument("--skill", choices=["grammar", "reading", "listening", "writing", "speaking"])
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

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
        print("       AptisPro - START SEED DATA")
        print("=" * 60)

        for skill_name, fn in runners.items():
            fn(db)

        total_tests     = db.query(Test).count()
        total_questions = db.query(Question).count()
        print("\n" + "=" * 60)
        print("       AptisPro - SEED COMPLETED!")
        print(f"       Total tests    : {total_tests}")
        print(f"       Total questions: {total_questions}")
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
