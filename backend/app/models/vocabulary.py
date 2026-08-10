from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Vocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    phonetic = Column(String, nullable=True)                  # Ký hiệu IPA, ví dụ: /əˌkɒm.əˈdeɪ.ʃən/
    pos = Column(String, nullable=True, index=True)           # Từ loại: noun, verb, adjective, adverb, phrase, collocation
    meaning_vi = Column(Text, nullable=False)                 # Nghĩa tiếng Việt
    cefr_level = Column(String, nullable=False, index=True, default="B1")  # Cấp độ: A1, A2, B1, B2, C1
    skill = Column(String, nullable=True, index=True)         # Kỹ năng thi: reading, listening, writing, speaking, grammar, general
    category = Column(String, nullable=True, index=True)      # Chủ đề: Travel, Work, Education, Daily Life, Technology, Health, Environment, Collocations, Grammar
    example_en = Column(Text, nullable=True)                  # Câu ví dụ tiếng Anh trong đề thi Aptis
    example_vi = Column(Text, nullable=True)                  # Dịch câu ví dụ sang tiếng Việt
    synonyms = Column(String, nullable=True)                  # Từ đồng nghĩa (ví dụ: schedule, lodging)
    antonyms = Column(String, nullable=True)                  # Từ trái nghĩa
    audio_url = Column(String, nullable=True)                 # Đồng dẫn file âm thanh (nếu có)
    occurrences = Column(Integer, default=1)                  # Tần suất xuất hiện trong bộ đề câu hỏi
    created_at = Column(DateTime, default=datetime.utcnow)

    user_states = relationship("UserVocabulary", back_populates="vocabulary", cascade="all, delete-orphan")


class UserVocabulary(Base):
    __tablename__ = "user_vocabularies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vocabulary_id = Column(Integer, ForeignKey("vocabularies.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="learning")  # "learning", "mastered", "bookmarked"
    review_count = Column(Integer, default=0)
    last_reviewed = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    vocabulary = relationship("Vocabulary", back_populates="user_states")
