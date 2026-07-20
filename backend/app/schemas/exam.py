from typing import Optional, List, Any
from pydantic import BaseModel
from app.models.exam import Skill, QuestionType


class QuestionPublic(BaseModel):
    id: int
    order_num: int
    question_type: QuestionType
    content: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    options: Optional[Any] = None
    # NOTE: correct_answer is NOT exposed here (only in results after submission)

    class Config:
        from_attributes = True


class TestSummary(BaseModel):
    id: int
    skill: Skill
    title: str
    description: Optional[str] = None
    is_vip: int
    question_count: int = 0

    class Config:
        from_attributes = True


class TestDetail(TestSummary):
    questions: List[QuestionPublic] = []


class SubmitAnswer(BaseModel):
    answers: dict  # {question_id: user_answer_string}
    time_taken_seconds: Optional[int] = None


class ResultDetail(BaseModel):
    id: int
    test_id: int
    test_title: Optional[str] = None   # Tên đề thi (join từ bảng tests)
    test_skill: Optional[str] = None   # Kỹ năng (reading/writing/...)
    score: Optional[float]
    aptis_band: Optional[str]
    answers: Optional[dict]
    ai_feedback: Optional[str]
    time_taken_seconds: Optional[int]
    completed_at: Any

    class Config:
        from_attributes = True
