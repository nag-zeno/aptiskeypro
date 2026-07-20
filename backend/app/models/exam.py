import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Skill(str, enum.Enum):
    reading = "reading"
    listening = "listening"
    writing = "writing"
    speaking = "speaking"
    grammar = "grammar"


class QuestionType(str, enum.Enum):
    multiple_choice = "multiple_choice"   # Trắc nghiệm 1 đáp án
    matching = "matching"                 # Nối từ / kéo thả
    fill_blank = "fill_blank"             # Điền vào chỗ trống
    essay = "essay"                       # Tự luận (Writing)
    audio_response = "audio_response"     # Ghi âm (Speaking)


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    skill = Column(SAEnum(Skill), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_vip = Column(Integer, default=0)  # 0 = free, 1 = VIP only
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    results = relationship("UserResult", back_populates="test")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False, index=True)
    order_num = Column(Integer, nullable=False, default=1)  # Thứ tự trong bài thi

    question_type = Column(SAEnum(QuestionType), nullable=False)
    content = Column(String, nullable=False)          # Nội dung câu hỏi (text / HTML)
    audio_url = Column(String, nullable=True)         # Đường dẫn file âm thanh (Listening)
    image_url = Column(String, nullable=True)         # Hình ảnh đính kèm
    options = Column(JSON, nullable=True)             # Danh sách lựa chọn [{"id":"A","text":"..."}]
    correct_answer = Column(String, nullable=True)    # Đáp án đúng (null nếu là essay/speaking)
    explanation = Column(String, nullable=True)       # Giải thích đáp án

    test = relationship("Test", back_populates="questions")


class UserResult(Base):
    __tablename__ = "user_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False, index=True)

    score = Column(Float, nullable=True)                   # Điểm số (0-100)
    aptis_band = Column(String, nullable=True)             # Band quy đổi (A1, A2, B1, B2, C)
    answers = Column(JSON, nullable=True)                  # {"q_id": "user_answer", ...}
    ai_feedback = Column(String, nullable=True)            # Nhận xét từ AI (Writing/Speaking)
    time_taken_seconds = Column(Integer, nullable=True)    # Thời gian làm bài (giây)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    test = relationship("Test", back_populates="results")
