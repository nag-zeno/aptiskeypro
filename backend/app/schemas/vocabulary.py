from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class VocabularyRead(BaseModel):
    id: int
    word: str
    phonetic: Optional[str] = None
    pos: Optional[str] = None
    meaning_vi: str
    cefr_level: str
    skill: Optional[str] = None
    category: Optional[str] = None
    example_en: Optional[str] = None
    example_vi: Optional[str] = None
    synonyms: Optional[str] = None
    antonyms: Optional[str] = None
    audio_url: Optional[str] = None
    occurrences: int = 1
    user_status: Optional[str] = None

    class Config:
        from_attributes = True


class VocabularyListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: List[VocabularyRead]


class VocabularyStatsResponse(BaseModel):
    total_words: int
    by_level: Dict[str, int]
    by_category: Dict[str, int]
    by_skill: Dict[str, int]
    user_mastered_count: int = 0
    user_bookmarked_count: int = 0
    user_learning_count: int = 0


class UserVocabStatusUpdate(BaseModel):
    status: str  # "learning", "mastered", "bookmarked", "none"


class UserVocabStatusResponse(BaseModel):
    vocabulary_id: int
    status: Optional[str] = None
    message: str
