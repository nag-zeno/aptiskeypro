from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_vip_user
from app.models.user import User
from app.models.exam import Test, Question, UserResult, Skill, QuestionType
from app.schemas.exam import TestSummary, TestDetail, SubmitAnswer, ResultDetail
from app.services.grader import auto_grade

router = APIRouter(prefix="/api", tags=["Exam"])


@router.get("/tests", response_model=List[TestSummary])
def list_tests(
    skill: Optional[Skill] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách bộ đề. Lọc theo kỹ năng nếu có."""
    query = db.query(Test)
    if skill:
        query = query.filter(Test.skill == skill)
    tests = query.all()

    result = []
    for test in tests:
        summary = TestSummary(
            id=test.id,
            skill=test.skill,
            title=test.title,
            description=test.description,
            is_vip=test.is_vip,
            question_count=len(test.questions),
        )
        result.append(summary)
    return result


@router.get("/tests/{test_id}", response_model=TestDetail)
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy nội dung bộ đề (câu hỏi). VIP test yêu cầu tài khoản VIP còn hạn."""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ đề")

    # Kiểm tra quyền VIP
    if test.is_vip:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if not current_user.vip_expires_at or current_user.vip_expires_at.replace(tzinfo=timezone.utc) < now:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bộ đề này dành cho học viên VIP. Vui lòng nâng cấp để truy cập.",
            )

    questions_sorted = sorted(test.questions, key=lambda q: q.order_num)
    return TestDetail(
        id=test.id,
        skill=test.skill,
        title=test.title,
        description=test.description,
        is_vip=test.is_vip,
        question_count=len(test.questions),
        questions=questions_sorted,
    )


@router.post("/tests/{test_id}/submit", response_model=ResultDetail)
def submit_test(
    test_id: int,
    payload: SubmitAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Nộp bài thi, chấm điểm tự động và lưu kết quả."""
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ đề")

    score, aptis_band, ai_feedback = auto_grade(test, payload.answers)

    result = UserResult(
        user_id=current_user.id,
        test_id=test_id,
        score=score,
        aptis_band=aptis_band,
        answers=payload.answers,
        ai_feedback=ai_feedback,
        time_taken_seconds=payload.time_taken_seconds,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return ResultDetail(
        id=result.id,
        test_id=result.test_id,
        test_title=test.title,
        test_skill=test.skill.value if test.skill else None,
        score=result.score,
        aptis_band=result.aptis_band,
        answers=result.answers,
        ai_feedback=result.ai_feedback,
        time_taken_seconds=result.time_taken_seconds,
        completed_at=result.completed_at,
    )


def _build_result_detail(result: UserResult, db: Session) -> ResultDetail:
    """Helper: Xây dựng ResultDetail với thông tin tên đề và kỹ năng."""
    test = db.query(Test).filter(Test.id == result.test_id).first()
    return ResultDetail(
        id=result.id,
        test_id=result.test_id,
        test_title=test.title if test else f"Đề #{result.test_id}",
        test_skill=test.skill.value if test else None,
        score=result.score,
        aptis_band=result.aptis_band,
        answers=result.answers,
        ai_feedback=result.ai_feedback,
        time_taken_seconds=result.time_taken_seconds,
        completed_at=result.completed_at,
    )


@router.get("/results", response_model=List[ResultDetail])
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy lịch sử các bài thi đã hoàn thành của người dùng hiện tại (kèm tên đề & kỹ năng)."""
    results = (
        db.query(UserResult)
        .filter(UserResult.user_id == current_user.id)
        .order_by(UserResult.completed_at.desc())
        .all()
    )
    return [_build_result_detail(r, db) for r in results]


@router.get("/results/{result_id}", response_model=ResultDetail)
def get_result_detail(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy chi tiết một bài thi cụ thể. Chỉ học viên sở hữu bài thi mới được xem."""
    result = db.query(UserResult).filter(
        UserResult.id == result_id,
        UserResult.user_id == current_user.id,
    ).first()
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy kết quả hoặc bạn không có quyền xem.",
        )
    return _build_result_detail(result, db)


@router.post("/results/{result_id}/analyze", response_model=ResultDetail)
def analyze_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gọi AI phân tích kết quả làm bài, chỉ ra lỗi sai và đưa ra lời khuyên.
    Chỉ cho phép người dùng sở hữu bài làm hoặc Admin.
    """
    from app.models.user import UserRole
    from app.services.grader import analyze_result_with_ai

    result = db.query(UserResult).filter(UserResult.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy kết quả.",
        )

    # Kiểm tra quyền: Phải là chủ nhân bài làm hoặc Admin
    if result.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền phân tích kết quả bài thi này.",
        )

    # Lấy thông tin bài thi và danh sách câu hỏi
    test = db.query(Test).filter(Test.id == result.test_id).first()
    if not test:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông tin đề thi liên quan.",
        )

    questions = db.query(Question).filter(Question.test_id == test.id).all()

    # Gọi AI phân tích và lưu vào DB
    try:
        feedback = analyze_result_with_ai(result, test, questions)
        result.ai_feedback = feedback
        db.commit()
        db.refresh(result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi phân tích AI: {str(e)}"
        )

    return _build_result_detail(result, db)
