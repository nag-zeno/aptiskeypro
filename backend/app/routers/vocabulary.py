import math
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, asc, desc

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.user import User
from app.models.vocabulary import Vocabulary, UserVocabulary
from app.schemas.vocabulary import (
    VocabularyRead,
    VocabularyListResponse,
    VocabularyStatsResponse,
    UserVocabStatusUpdate,
    UserVocabStatusResponse,
)
from app.services.vocabulary_seed_data import seed_vocabulary_data

router = APIRouter(prefix="/api/vocabulary", tags=["Vocabulary"])


@router.get("", response_model=VocabularyListResponse)
def get_vocabularies(
    query: Optional[str] = None,
    skill: Optional[str] = None,
    cefr_level: Optional[str] = None,
    category: Optional[str] = None,
    pos: Optional[str] = None,
    status_filter: Optional[str] = None,
    sort: Optional[str] = "freq_desc",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Lấy danh sách từ vựng kèm bộ lọc nâng cao (Search, Skill, CEFR Level, Category, Từ loại, Trạng thái đã học).
    """
    # Tự động nạp dữ liệu từ vựng mẫu nếu DB trống
    if db.query(Vocabulary).count() == 0:
        seed_vocabulary_data(db)

    db_query = db.query(Vocabulary)

    # Lọc theo từ khóa tìm kiếm
    if query and query.strip():
        q_str = f"%{query.strip()}%"
        db_query = db_query.filter(
            or_(
                Vocabulary.word.ilike(q_str),
                Vocabulary.meaning_vi.ilike(q_str),
                Vocabulary.example_en.ilike(q_str),
            )
        )

    # Lọc theo Kỹ năng
    if skill and skill.strip() and skill.lower() != "all":
        db_query = db_query.filter(func.lower(Vocabulary.skill) == skill.strip().lower())

    # Lọc theo Cấp độ CEFR
    if cefr_level and cefr_level.strip() and cefr_level.upper() != "ALL":
        db_query = db_query.filter(func.upper(Vocabulary.cefr_level) == cefr_level.strip().upper())

    # Lọc theo Chủ đề
    if category and category.strip() and category.lower() != "all":
        db_query = db_query.filter(func.lower(Vocabulary.category) == category.strip().lower())

    # Lọc theo Từ loại (POS)
    if pos and pos.strip() and pos.lower() != "all":
        db_query = db_query.filter(func.lower(Vocabulary.pos) == pos.strip().lower())

    # Lọc theo Trạng thái học viên (Mastered, Bookmarked, Learning)
    user_status_map: Dict[int, str] = {}
    if current_user:
        user_states = db.query(UserVocabulary).filter(UserVocabulary.user_id == current_user.id).all()
        for us in user_states:
            user_status_map[us.vocabulary_id] = us.status

    if status_filter and status_filter.strip() and status_filter.lower() != "all":
        if not current_user:
            # Nếu chưa đăng nhập thì không thể lọc trạng thái cá nhân
            return VocabularyListResponse(total=0, page=page, limit=limit, total_pages=0, items=[])

        s_val = status_filter.strip().lower()
        subq = (
            db.query(UserVocabulary.vocabulary_id)
            .filter(UserVocabulary.user_id == current_user.id, UserVocabulary.status == s_val)
            .subquery()
        )
        db_query = db_query.filter(Vocabulary.id.in_(subq))

    # Sắp xếp
    if sort == "word_asc":
        db_query = db_query.order_by(asc(Vocabulary.word))
    elif sort == "level_asc":
        db_query = db_query.order_by(asc(Vocabulary.cefr_level), desc(Vocabulary.occurrences))
    else:  # freq_desc
        db_query = db_query.order_by(desc(Vocabulary.occurrences), asc(Vocabulary.word))

    total = db_query.count()
    total_pages = math.ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    items_raw = db_query.offset(offset).limit(limit).all()

    items = []
    for v in items_raw:
        st = user_status_map.get(v.id)
        items.append(
            VocabularyRead(
                id=v.id,
                word=v.word,
                phonetic=v.phonetic,
                pos=v.pos,
                meaning_vi=v.meaning_vi,
                cefr_level=v.cefr_level,
                skill=v.skill,
                category=v.category,
                example_en=v.example_en,
                example_vi=v.example_vi,
                synonyms=v.synonyms,
                antonyms=v.antonyms,
                audio_url=v.audio_url,
                occurrences=v.occurrences or 1,
                user_status=st,
            )
        )

    return VocabularyListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        items=items,
    )


@router.get("/stats", response_model=VocabularyStatsResponse)
def get_vocabulary_stats(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Thống kê tổng thể dữ liệu từ vựng theo CEFR, Category, Skill và tiến trình học viên."""
    if db.query(Vocabulary).count() == 0:
        seed_vocabulary_data(db)

    total_words = db.query(Vocabulary).count()

    # Phân bố theo CEFR Level
    level_counts = (
        db.query(Vocabulary.cefr_level, func.count(Vocabulary.id))
        .group_by(Vocabulary.cefr_level)
        .all()
    )
    by_level = {lvl: count for lvl, count in level_counts if lvl}

    # Phân bố theo Category
    cat_counts = (
        db.query(Vocabulary.category, func.count(Vocabulary.id))
        .group_by(Vocabulary.category)
        .all()
    )
    by_category = {cat: count for cat, count in cat_counts if cat}

    # Phân bố theo Skill
    skill_counts = (
        db.query(Vocabulary.skill, func.count(Vocabulary.id))
        .group_by(Vocabulary.skill)
        .all()
    )
    by_skill = {sk: count for sk, count in skill_counts if sk}

    # Tiến trình cá nhân học viên
    mastered_count = 0
    bookmarked_count = 0
    learning_count = 0

    if current_user:
        mastered_count = (
            db.query(UserVocabulary)
            .filter(UserVocabulary.user_id == current_user.id, UserVocabulary.status == "mastered")
            .count()
        )
        bookmarked_count = (
            db.query(UserVocabulary)
            .filter(UserVocabulary.user_id == current_user.id, UserVocabulary.status == "bookmarked")
            .count()
        )
        learning_count = (
            db.query(UserVocabulary)
            .filter(UserVocabulary.user_id == current_user.id, UserVocabulary.status == "learning")
            .count()
        )

    return VocabularyStatsResponse(
        total_words=total_words,
        by_level=by_level,
        by_category=by_category,
        by_skill=by_skill,
        user_mastered_count=mastered_count,
        user_bookmarked_count=bookmarked_count,
        user_learning_count=learning_count,
    )


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Lấy danh sách các chủ đề và kỹ năng hiện có."""
    if db.query(Vocabulary).count() == 0:
        seed_vocabulary_data(db)

    categories = [
        row[0]
        for row in db.query(Vocabulary.category).distinct().all()
        if row[0]
    ]
    skills = [
        row[0]
        for row in db.query(Vocabulary.skill).distinct().all()
        if row[0]
    ]
    levels = ["A1", "A2", "B1", "B2", "C1"]

    return {
        "categories": categories,
        "skills": skills,
        "levels": levels,
    }


@router.post("/{vocab_id}/status", response_model=UserVocabStatusResponse)
def update_vocab_status(
    vocab_id: int,
    payload: UserVocabStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật hoặc hủy trạng thái học từ vựng (learning, mastered, bookmarked, none)."""
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Không tìm thấy từ vựng")

    user_vocab = (
        db.query(UserVocabulary)
        .filter(UserVocabulary.user_id == current_user.id, UserVocabulary.vocabulary_id == vocab_id)
        .first()
    )

    if payload.status == "none":
        if user_vocab:
            db.delete(user_vocab)
            db.commit()
        return UserVocabStatusResponse(vocabulary_id=vocab_id, status=None, message="Đã xóa trạng thái từ vựng")

    if not user_vocab:
        user_vocab = UserVocabulary(
            user_id=current_user.id,
            vocabulary_id=vocab_id,
            status=payload.status,
            review_count=1,
        )
        db.add(user_vocab)
    else:
        user_vocab.status = payload.status
        user_vocab.review_count += 1

    db.commit()
    return UserVocabStatusResponse(
        vocabulary_id=vocab_id,
        status=payload.status,
        message=f"Đã cập nhật trạng thái từ vựng thành '{payload.status}'",
    )


@router.post("/seed")
def seed_vocabulary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """(Admin / Utility) Khởi tạo lại bộ từ vựng chuẩn Aptis."""
    seed_vocabulary_data(db, force=True)
    return {"status": "success", "message": "Đã khởi tạo xong dữ liệu Từ vựng Aptis!"}
