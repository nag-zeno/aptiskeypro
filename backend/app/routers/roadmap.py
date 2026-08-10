from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.user import User
from app.models.roadmap import RoadmapStage, RoadmapNode, UserRoadmapProgress, UserLearningProfile, ProgressStatus
from app.models.exam import UserResult, Test
from app.schemas.roadmap import (
    RoadmapTreeResponse,
    RoadmapStageRead,
    RoadmapNodeRead,
    UserProgressUpdate,
    UserProgressResponse,
    LearningProfileUpdate,
    NodeRecommendationBadge,
    AIRecommendationSummary,
)

router = APIRouter(prefix="/api/roadmap", tags=["Roadmap"])


def _ensure_user_profile_and_progress(user_id: int, db: Session) -> UserLearningProfile:
    """Đảm bảo user có profile học tập và tiến trình khởi tạo cho bài đầu tiên."""
    profile = db.query(UserLearningProfile).filter(UserLearningProfile.user_id == user_id).first()
    if not profile:
        profile = UserLearningProfile(
            user_id=user_id,
            target_band="B1",
            streak_days=1,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Đảm bảo bài đầu tiên trong chặng 1 được unlock nếu user chưa có tiến trình nào
    first_node = (
        db.query(RoadmapNode)
        .join(RoadmapStage)
        .order_by(RoadmapStage.order_num.asc(), RoadmapNode.order_num.asc())
        .first()
    )

    if first_node:
        existing = db.query(UserRoadmapProgress).filter(
            UserRoadmapProgress.user_id == user_id,
            UserRoadmapProgress.node_id == first_node.id,
        ).first()
        if not existing:
            first_progress = UserRoadmapProgress(
                user_id=user_id,
                node_id=first_node.id,
                status=ProgressStatus.unlocked,
            )
            db.add(first_progress)
            db.commit()

    return profile


def _analyze_user_weaknesses(user_id: int, db: Session):
    """Hàm helper phân tích lịch sử làm bài thi & tiến trình lộ trình để tìm điểm yếu của học viên."""
    recommendations_map = {}
    skill_scores = {}
    weak_skills = []
    
    # 1. Thống kê kết quả từ bảng user_results
    results = db.query(UserResult).filter(UserResult.user_id == user_id).all()
    
    if results:
        skill_totals = {}
        skill_counts = {}
        
        for r in results:
            # Lấy skill của test liên quan
            test = db.query(Test).filter(Test.id == r.test_id).first()
            if test and test.skill and r.score is not None:
                sk = test.skill.value
                skill_totals[sk] = skill_totals.get(sk, 0.0) + r.score
                skill_counts[sk] = skill_counts.get(sk, 0) + 1
        
        for sk, total in skill_totals.items():
            cnt = skill_counts[sk]
            avg = round(total / cnt, 1)
            skill_scores[sk] = avg
            if avg < 70.0:
                weak_skills.append(sk)

    # 2. Thống kê tiến trình các RoadmapNode của user
    user_progs = db.query(UserRoadmapProgress).filter(UserRoadmapProgress.user_id == user_id).all()
    prog_map = {p.node_id: p for p in user_progs}

    nodes = db.query(RoadmapNode).all()
    recommended_node_ids = []

    for node in nodes:
        prog = prog_map.get(node.id)
        # Nếu đã làm và điểm < target_pass_score -> Cần củng cố gấp
        if prog and prog.highest_score > 0 and prog.highest_score < node.target_pass_score:
            recommendations_map[node.id] = NodeRecommendationBadge(
                is_recommended=True,
                priority="high",
                reason=f"Kết quả bài làm gần nhất của bạn ({prog.highest_score}%) chưa đạt điểm chuẩn ({node.target_pass_score}%)."
            )
            recommended_node_ids.append(node.id)
        # Hoặc nếu thuộc kỹ năng mà học viên làm kém nhất
        elif node.skill in weak_skills and (not prog or prog.status.value != "completed"):
            avg_score = skill_scores.get(node.skill, 0.0)
            recommendations_map[node.id] = NodeRecommendationBadge(
                is_recommended=True,
                priority="medium",
                reason=f"Tỷ lệ làm đúng kỹ năng {node.skill.upper()} của bạn chỉ đạt {avg_score}%. Hãy ôn tập bài này!"
            )
            if node.id not in recommended_node_ids:
                recommended_node_ids.append(node.id)

    # Đảm bảo có ít nhất 1-2 bài đề xuất nếu chưa có bài nào bị cờ
    if not recommended_node_ids and nodes:
        # Đề xuất bài học unlocked tiếp theo
        for n in nodes:
            prog = prog_map.get(n.id)
            if not prog or prog.status.value != "completed":
                recommendations_map[n.id] = NodeRecommendationBadge(
                    is_recommended=True,
                    priority="medium",
                    reason="Bài học tiếp theo được AI đề xuất cho lộ trình của bạn."
                )
                recommended_node_ids.append(n.id)
                break

    # Tạo câu tư vấn AI
    if weak_skills:
        skill_str = ", ".join([s.upper() for s.prefix in weak_skills for s in [s.prefix]]) if False else ", ".join([s.upper() for s in weak_skills])
        ai_advice = f"🤖 AI Assistant: Phân tích lịch sử bài làm cho thấy bạn đang gặp thử thách ở kỹ năng {skill_str}. Hãy ưu tiên làm các bài tập bên dưới để tăng tốc băng điểm!"
    elif results:
        ai_advice = "🤖 AI Assistant: Phong độ học tập của bạn rất tốt! Hãy tiếp tục duy trì bài học theo lộ trình để chinh phục các chặng cao hơn."
    else:
        ai_advice = "🤖 AI Assistant: Chào mừng bạn! Hãy bắt đầu với bài kiểm tra đầu vào 15 phút hoặc hoàn thành Bài Học Nền Tảng đầu tiên để AI có dữ liệu phân tích điểm yếu nhé!"

    return {
        "recommendations_map": recommendations_map,
        "recommended_node_ids": recommended_node_ids,
        "skill_scores": skill_scores,
        "weak_skills": weak_skills,
        "ai_advice": ai_advice,
        "has_data": bool(results or user_progs)
    }


@router.get("/tree", response_model=RoadmapTreeResponse)
def get_roadmap_tree(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Lấy toàn bộ cây sơ đồ lộ trình học tập (dành cho cả Học viên và Khách trải nghiệm)."""
    target_band = "B1"
    streak_days = 1
    current_stage_id = None
    user_progress_map = {}

    rec_analysis = {"recommendations_map": {}}
    if current_user:
        profile = _ensure_user_profile_and_progress(current_user.id, db)
        target_band = profile.target_band
        streak_days = profile.streak_days
        current_stage_id = profile.current_stage_id

        progress_records = db.query(UserRoadmapProgress).filter(UserRoadmapProgress.user_id == current_user.id).all()
        for p in progress_records:
            user_progress_map[p.node_id] = p
            
        rec_analysis = _analyze_user_weaknesses(current_user.id, db)

    # Nếu DB chưa có dữ liệu lộ trình, tự động seed mẫu
    stages_count = db.query(RoadmapStage).count()
    if stages_count == 0:
        seed_roadmap_data(db)

    stages = db.query(RoadmapStage).order_by(RoadmapStage.order_num.asc()).all()
    
    total_nodes = 0
    completed_nodes = 0
    total_stars = 0
    stages_data = []
    is_first_node = True

    for stage in stages:
        nodes_data = []
        for node in stage.nodes:
            total_nodes += 1
            prog = user_progress_map.get(node.id)

            if prog:
                status_val = prog.status.value
                score_val = prog.highest_score
                stars_val = prog.stars
            else:
                # Nếu là khách hoặc chưa làm: bài đầu tiên được unlock để học thử, còn lại locked
                if is_first_node:
                    status_val = "unlocked"
                    is_first_node = False
                else:
                    status_val = "locked"
                score_val = 0.0
                stars_val = 0

            if status_val == "completed":
                completed_nodes += 1
                total_stars += stars_val

            recom_badge = rec_analysis["recommendations_map"].get(node.id)

            nodes_data.append(
                RoadmapNodeRead(
                    id=node.id,
                    stage_id=node.stage_id,
                    skill=node.skill,
                    part_name=node.part_name,
                    title=node.title,
                    description=node.description,
                    theory_content=node.theory_content,
                    practice_url=node.practice_url,
                    test_id=node.test_id,
                    target_pass_score=node.target_pass_score,
                    is_vip=node.is_vip,
                    order_num=node.order_num,
                    icon=node.icon,
                    user_status=status_val,
                    highest_score=score_val,
                    stars=stars_val,
                    recommendation=recom_badge,
                )
            )

        stages_data.append(
            RoadmapStageRead(
                id=stage.id,
                title=stage.title,
                target_band=stage.target_band,
                description=stage.description,
                order_num=stage.order_num,
                icon=stage.icon,
                nodes=nodes_data,
            )
        )

    progress_percentage = (completed_nodes / total_nodes * 100.0) if total_nodes > 0 else 0.0

    return RoadmapTreeResponse(
        target_band=target_band,
        current_stage_id=current_stage_id,
        streak_days=streak_days,
        total_nodes=total_nodes,
        completed_nodes=completed_nodes,
        total_stars=total_stars,
        progress_percentage=round(progress_percentage, 1),
        stages=stages_data,
    )


@router.get("/nodes/{node_id}", response_model=RoadmapNodeRead)
def get_node_detail(
    node_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy chi tiết lý thuyết & mẹo thi cho 1 bài học."""
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài học")

    prog = db.query(UserRoadmapProgress).filter(
        UserRoadmapProgress.user_id == current_user.id,
        UserRoadmapProgress.node_id == node.id,
    ).first()

    status_val = prog.status.value if prog else "locked"
    score_val = prog.highest_score if prog else 0.0
    stars_val = prog.stars if prog else 0

    return RoadmapNodeRead(
        id=node.id,
        stage_id=node.stage_id,
        skill=node.skill,
        part_name=node.part_name,
        title=node.title,
        description=node.description,
        theory_content=node.theory_content,
        practice_url=node.practice_url,
        test_id=node.test_id,
        target_pass_score=node.target_pass_score,
        is_vip=node.is_vip,
        order_num=node.order_num,
        icon=node.icon,
        user_status=status_val,
        highest_score=score_val,
        stars=stars_val,
    )


@router.post("/nodes/{node_id}/complete", response_model=UserProgressResponse)
def complete_node(
    node_id: int,
    payload: UserProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật điểm bài làm, tính sao và tự động mở khóa bài học tiếp theo."""
    node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài học")

    # Lấy hoặc tạo progress cho node này
    prog = db.query(UserRoadmapProgress).filter(
        UserRoadmapProgress.user_id == current_user.id,
        UserRoadmapProgress.node_id == node.id,
    ).first()

    if not prog:
        prog = UserRoadmapProgress(
            user_id=current_user.id,
            node_id=node.id,
            status=ProgressStatus.unlocked,
        )
        db.add(prog)

    # Cập nhật điểm số cao nhất
    if payload.score > prog.highest_score:
        prog.highest_score = payload.score

    # Tính sao
    score = payload.score
    stars = 0
    if score >= 95.0:
        stars = 3
    elif score >= 85.0:
        stars = 2
    elif score >= 70.0:
        stars = 1

    if stars > prog.stars:
        prog.stars = stars

    unlocked_next_id = None
    passed = score >= node.target_pass_score

    if passed:
        prog.status = ProgressStatus.completed
        prog.completed_at = datetime.utcnow()

        # Tìm node tiếp theo để unlock
        # Mở khóa node tiếp theo trong cùng stage hoặc stage kế tiếp
        all_nodes = (
            db.query(RoadmapNode)
            .join(RoadmapStage)
            .order_by(RoadmapStage.order_num.asc(), RoadmapNode.order_num.asc())
            .all()
        )

        current_idx = -1
        for idx, n in enumerate(all_nodes):
            if n.id == node.id:
                current_idx = idx
                break

        if current_idx != -1 and current_idx + 1 < len(all_nodes):
            next_node = all_nodes[current_idx + 1]
            unlocked_next_id = next_node.id

            next_prog = db.query(UserRoadmapProgress).filter(
                UserRoadmapProgress.user_id == current_user.id,
                UserRoadmapProgress.node_id == next_node.id,
            ).first()

            if not next_prog:
                next_prog = UserRoadmapProgress(
                    user_id=current_user.id,
                    node_id=next_node.id,
                    status=ProgressStatus.unlocked,
                )
                db.add(next_prog)
            elif next_prog.status == ProgressStatus.locked:
                next_prog.status = ProgressStatus.unlocked

    db.commit()
    db.refresh(prog)

    msg = f"Chúc mừng! Bạn đã hoàn thành xuất sắc với {score}% điểm ({stars} sao)!" if passed else f"Điểm của bạn là {score}%. Cần đạt từ {node.target_pass_score}% để qua bài."

    return UserProgressResponse(
        node_id=node.id,
        status=prog.status.value,
        highest_score=prog.highest_score,
        stars=prog.stars,
        unlocked_next_node_id=unlocked_next_id,
        message=msg,
    )


@router.post("/profile")
def update_profile(
    payload: LearningProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật mục tiêu Band điểm học viên."""
    profile = db.query(UserLearningProfile).filter(UserLearningProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserLearningProfile(user_id=current_user.id, target_band=payload.target_band)
        db.add(profile)
    else:
        profile.target_band = payload.target_band
    db.commit()
    return {"status": "success", "target_band": payload.target_band}


@router.post("/seed")
def seed_roadmap_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """(Admin / Utility) Khởi tạo lại dữ liệu các chặng và bài học chuẩn format Aptis."""
    seed_roadmap_data(db, force=True)
    return {"status": "success", "message": "Đã khởi tạo xong dữ liệu Lộ trình chuẩn Aptis mới!"}


def seed_roadmap_data(db: Session, force: bool = False):
    """Hàm helper khởi tạo dữ liệu 20 bài học chuyên sâu toàn diện chuẩn format Aptis."""
    if force:
        db.query(UserRoadmapProgress).delete()
        db.query(RoadmapNode).delete()
        db.query(RoadmapStage).delete()
        db.commit()
    elif db.query(RoadmapStage).count() > 0:
        return

    # =========================================================================
    # CHẶNG 1: FOUNDATION (TARGET A1 - A2) - 6 BÀI HỌC
    # =========================================================================
    s1 = RoadmapStage(
        title="Chặng 1: Nền Tảng Vững Chắc (Target A1 - A2)",
        target_band="A1-A2",
        description="Xây dựng nền tảng từ vựng, ngữ pháp cốt lõi và làm quen các dạng câu hỏi căn bản của đề thi Aptis.",
        order_num=1,
        icon="bi-building-fill-gear",
    )
    db.add(s1)
    db.flush()

    n1_1 = RoadmapNode(
        stage_id=s1.id,
        skill="grammar",
        part_name="Grammar Core 1",
        title="Ngữ pháp cốt lõi: 5 Thì Động Từ Thường Gặp nhất trong đề Aptis",
        description="Nắm vững Hiện tại đơn, Quá khứ đơn, Hiện tại hoàn thành, Tương lai đơn và Dấu hiệu nhận biết thời gian.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-primary mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-star-fill text-warning me-2"></i>Tổng hợp các dạng Thì Động Từ trong bộ đề Grammar Test 001 - 005</h5>
    <p class="mb-0 small">Mẹo nhận biết từ chìa khóa (Keywords) để chọn đáp án đúng ngay trong 3 giây.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Hiện tại hoàn thành (Present Perfect) vs Quá khứ đơn (Past Simple)</h4>
  <p><b>Dấu hiệu phân biệt:</b></p>
  <ul>
    <li><b>Past Simple:</b> Xảy ra và kết thúc hoàn toàn tại thời điểm xác định (<i>yesterday, in 1998, ago, last month, when I was young</i>).</li>
    <li><b>Present Perfect:</b> Nhấn mạnh kết quả hoặc trải nghiệm kéo dài đến hiện tại (<i>already, yet, since, for, twice, so far, recently</i>).</li>
  </ul>
  <div class="p-3 bg-light rounded mb-3 border-start border-4 border-primary">
    <p class="mb-1 fw-bold">Ví dụ từ đề thi thực tế (Grammar Test 1):</p>
    <p class="mb-1"><i>"She _______ to Japan twice this year."</i></p>
    <p class="mb-0 text-success fw-bold">-> Đáp án: <u>has been</u> (trải nghiệm "đã đến Japan 2 lần")</p>
  </div>
</div>
""",
        practice_url="/grammar_test001.html",
        target_pass_score=70.0,
        order_num=1,
        icon="bi-journal-check",
    )

    n1_2 = RoadmapNode(
        stage_id=s1.id,
        skill="grammar",
        part_name="Grammar Core 2",
        title="Ngữ pháp cốt lõi: Câu Bị Động, Đại Từ Quan Hệ & Câu Điều Kiện 2",
        description="Chiến thuật xử lý câu bị động có mốc thời gian, đại từ sở hữu whose và giả định loại 2.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-primary mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-check-circle-fill me-2"></i>3 Dạng Ngữ Pháp Xuất Hiện 100% Trong Đề Thi</h5>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Câu Bị Động (Passive Voice)</h4>
  <p><b>Công thức:</b> <code>S + BE + V3/ed (+ by O)</code></p>
  <div class="p-3 bg-light rounded mb-3 border-start border-4 border-primary">
    <p class="mb-1 fw-bold">Ví dụ thực tế trong đề:</p>
    <p class="mb-1"><i>"The bridge _______ in 1998."</i></p>
    <p class="mb-0 text-success fw-bold">-> Đáp án: <u>was built</u> (Cây cầu được xây năm 1998)</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">2. Đại Từ Quan Hệ (Relative Pronouns)</h4>
  <table class="table table-bordered table-sm mb-3">
    <thead class="table-primary">
      <tr><th>Đại từ</th><th>Chức năng</th><th>Ví dụ thực tế</th></tr>
    </thead>
    <tbody>
      <tr><td><b>who</b></td><td>Chỉ người (Chủ ngữ)</td><td>The man <u>who</u> called you is my boss.</td></tr>
      <tr><td><b>whose</b></td><td>Chỉ tính chất Sở Hữu</td><td>The man <u>whose</u> car was stolen called the police.</td></tr>
      <tr><td><b>which</b></td><td>Chỉ vật / sự việc</td><td>The report <u>which</u> I submitted was approved.</td></tr>
    </tbody>
  </table>

  <h4 class="fw-bold text-primary mt-3">3. Câu Điều Kiện Loại 2 (If Type 2)</h4>
  <p>Giả định không có thật ở hiện tại: <code>If + S + V2/were, S + would/could + V-bare</code></p>
  <div class="p-3 bg-light rounded mb-3 border-start border-4 border-primary">
    <p class="mb-1 fw-bold">Ví dụ thực tế trong đề:</p>
    <p class="mb-1"><i>"If I _______ more time, I would learn a new language."</i></p>
    <p class="mb-0 text-success fw-bold">-> Đáp án: <u>had</u> (Mệnh đề If chia V2)</p>
  </div>
</div>
""",
        practice_url="/grammar_test001.html",
        target_pass_score=70.0,
        order_num=2,
        icon="bi-journal-code",
    )

    n1_3 = RoadmapNode(
        stage_id=s1.id,
        skill="reading",
        part_name="Reading Part 1",
        title="Reading Part 1: Hoàn thành câu ngắn & Nhận biết Từ loại",
        description="Mẹo phân biệt Danh từ, Tính từ, Trạng từ để điền từ đúng ngữ cảnh trong tin nhắn ngắn.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-info mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-search me-2"></i>Bí quyết đọc lướt & Phân tích Từ Loại (Part-of-Speech)</h5>
    <p class="mb-0 small">Reading Part 1 gồm 5 câu điền từ trong đoạn văn ngắn 50-70 từ.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Quy tắc vị trí Từ Loại</h4>
  <ul>
    <li><b>Điền Tính từ (Adj):</b> Đứng trước Danh từ (<i>a <u>beautiful</u> garden</i>) hoặc sau To be / Linking verbs.</li>
    <li><b>Điền Trạng từ (Adv):</b> Bổ nghĩa cho động từ thường (<i>walk <u>quickly</u></i>).</li>
    <li><b>Điền Danh từ / V-ing:</b> Đứng sau các giới từ (<i>interested in <u>learning</u></i>, <i>thanks for your <u>help</u></i>).</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Vốn từ vựng hay xuất hiện nhất trong Part 1</h4>
  <table class="table table-striped table-sm mb-3">
    <thead class="table-info">
      <tr><th>Từ vựng</th><th>Nghĩa tiếng Việt</th><th>Ngữ cảnh sử dụng</th></tr>
    </thead>
    <tbody>
      <tr><td><b>appointment</b></td><td>Cuộc hẹn</td><td>Đặt lịch khám bệnh / gặp đối tác</td></tr>
      <tr><td><b>available</b></td><td>Có sẵn / Rảnh rỗi</td><td>Thông báo lịch làm việc / phòng trống</td></tr>
      <tr><td><b>delayed</b></td><td>Bị hoãn / Chậm trễ</td><td>Thông báo chuyến bay / tàu xe</td></tr>
      <tr><td><b>discount</b></td><td>Giảm giá</td><td>Tin nhắn khuyến mãi mua sắm</td></tr>
      <tr><td><b>confirm</b></td><td>Xác nhận</td><td>Xác nhận đặt chỗ / tham gia sự kiện</td></tr>
    </tbody>
  </table>
</div>
""",
        practice_url="/reading_question1.html",
        target_pass_score=70.0,
        order_num=3,
        icon="bi-book-half",
    )

    n1_4 = RoadmapNode(
        stage_id=s1.id,
        skill="listening",
        part_name="Listening Part 1",
        title="Listening Part 1: Nhận diện thông tin ngắn & Mẹo né bẫy đính chính",
        description="Chiến thuật nghe số điện thoại, giá tiền, mốc thời gian và cách bắt từ khóa né bẫy đổi ý.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-warning mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-headphones me-2"></i>Kỹ thuật làm bài Listening Part 1 (Q1 - Q13)</h5>
    <p class="mb-0 small">Bắt chính xác thông tin con số, thời gian và địa điểm trong đoạn thoại 15-30 giây.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Cảnh giác bẫy đính chính (Correction Trap)</h4>
  <p>Người nói thường đưa ra thông tin ban đầu, sau đó dùng từ nối đổi ý để sửa lại đáp án:</p>
  <ul>
    <li><i>"Oh wait, actually..."</i> (Ồ khoan đã, thực ra là...)</li>
    <li><i>"On second thought, I'd prefer..."</i> (Nghĩ lại thì tôi thích...)</li>
    <li><i>"Sorry, I made a mistake, it's..."</i> (Xin lỗi, tôi nhầm, đúng ra là...)</li>
  </ul>
  <div class="p-3 bg-light rounded mb-3 border-start border-4 border-warning">
    <p class="mb-1 fw-bold">Ví dụ bẫy hội thoại trong đề thi:</p>
    <p class="mb-1"><i>Speaker: "The meeting is at 3 PM today... Oh wait, the manager just rescheduled it to 4 PM."</i></p>
    <p class="mb-0 text-success fw-bold">-> Đáp án đúng: <u>4 PM</u> (Không chọn 3 PM)</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">2. Phân biệt các cặp số dễ gây nhầm lẫn</h4>
  <table class="table table-bordered table-sm mb-3">
    <thead class="table-warning">
      <tr><th>Nhóm đuôi -teen (Nhấn âm 2)</th><th>Nhóm đuôi -ty (Nhấn âm 1)</th></tr>
    </thead>
    <tbody>
      <tr><td>Thir<b>TEEN</b> (13)</td><td><b>THIR</b>ty (30)</td></tr>
      <tr><td>Four<b>TEEN</b> (14)</td><td><b>FOR</b>ty (40)</td></tr>
      <tr><td>Fif<b>TEEN</b> (15)</td><td><b>FIF</b>ty (50)</td></tr>
    </tbody>
  </table>
</div>
""",
        practice_url="/listening_question1_13.html",
        target_pass_score=70.0,
        order_num=4,
        icon="bi-headphones",
    )

    n1_5 = RoadmapNode(
        stage_id=s1.id,
        skill="writing",
        part_name="Writing Part 1 & 2",
        title="Writing Part 1 & 2: Điền thông tin form & Viết đoạn văn về bản thân",
        description="Quy tắc viết đúng số từ, sử dụng chính tả chuẩn xác và bài mẫu 20-30 từ đạt điểm tuyệt đối.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-success mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-pencil-fill me-2"></i>Chiến thuật ghi điểm Writing Part 1 & Part 2</h5>
    <p class="mb-0 small">Phần thi khởi động đòi hỏi độ chính xác tuyệt đối về chính tả và cấu trúc câu ngắn.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Writing Part 1: Trả lời 5 câu hỏi thông tin ngắn (1-5 từ)</h4>
  <ul>
    <li>Viết câu trả lời ngắn gọn, không cần viết nguyên câu đầy đủ.</li>
    <li><b>Ví dụ:</b> <i>What is your favorite food?</i> -> <u>Fresh seafood and pizza</u></li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Writing Part 2: Viết đoạn văn ngắn (20 - 30 từ)</h4>
  <p><b>Công thức 3 câu chuẩn mực:</b></p>
  <ol>
    <li><b>Câu 1:</b> Trả lời trực tiếp lý do gia nhập câu lạc bộ / sở thích.</li>
    <li><b>Câu 2:</b> Nêu chi tiết tần suất hoặc hoạt động yêu thích.</li>
    <li><b>Câu 3:</b> Cảm xúc hoặc kỳ vọng của bạn.</li>
  </ol>

  <div class="p-3 bg-light rounded border-start border-4 border-success mb-3">
    <h6 class="fw-bold text-success">Đoạn văn mẫu Part 2 (Chủ đề Music Club):</h6>
    <p class="mb-0 italic">"I joined this music club because I am very passionate about playing the acoustic guitar. I usually practice playing twice a week. Playing music helps me relax and reduce stress after work." <i>(32 từ)</i></p>
  </div>
</div>
""",
        practice_url="/writing_bode.html",
        target_pass_score=70.0,
        order_num=5,
        icon="bi-pencil-square",
    )

    n1_6 = RoadmapNode(
        stage_id=s1.id,
        skill="speaking",
        part_name="Speaking Part 1",
        title="Speaking Part 1: Trả lời 3 câu hỏi cá nhân theo khung A.R.E.",
        description="Khung phản hồi A.R.E. (Answer - Reason - Example) giúp bài nói 30 giây trôi chảy, không bị ngập ngừng.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-danger mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-mic-fill me-2"></i>Khung phản hồi A.R.E. cho Speaking Part 1</h5>
    <p class="mb-0 small">Trả lời 3 câu hỏi cá nhân, mỗi câu có 30 giây nói.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Công thức A.R.E. thần thánh (30s/câu)</h4>
  <ul>
    <li><b>A - Answer (1 câu):</b> Trả lời thẳng vào câu hỏi.</li>
    <li><b>R - Reason (1 câu):</b> Đưa ra lý do sử dụng <i>because, since, as</i>.</li>
    <li><b>E - Example / Detail (1-2 câu):</b> Đưa ra ví dụ hoặc trải nghiệm cá nhân cụ thể.</li>
  </ul>

  <div class="p-3 bg-light rounded border-start border-4 border-danger mb-3">
    <h6 class="fw-bold text-danger">Ví dụ ứng dụng cho câu hỏi: "Please tell me about your hometown."</h6>
    <p class="mb-1"><b>[Answer]:</b> I come from Hanoi, which is the bustling capital city of Vietnam.</p>
    <p class="mb-1"><b>[Reason]:</b> I really love living here because it offers a perfect blend of rich history and vibrant modern lifestyle.</p>
    <p class="mb-0"><b>[Example]:</b> For instance, I enjoy walking around the West Lake with my close friends every weekend.</p>
  </div>
</div>
""",
        practice_url="/speaking_question1_practice.html",
        target_pass_score=70.0,
        order_num=6,
        icon="bi-mic-fill",
    )

    db.add_all([n1_1, n1_2, n1_3, n1_4, n1_5, n1_6])

    # =========================================================================
    # CHẶNG 2: BREAKTHROUGH (TARGET B1) - 7 BÀI HỌC
    # =========================================================================
    s2 = RoadmapStage(
        title="Chặng 2: Bứt Phá Kỹ Năng (Target B1)",
        target_band="B1",
        description="Phát triển kỹ năng ghép nối logic, phân tích quan điểm và phản hồi tương tác chuẩn format B1.",
        order_num=2,
        icon="bi-rocket-takeoff-fill",
    )
    db.add(s2)
    db.flush()

    n2_1 = RoadmapNode(
        stage_id=s2.id,
        skill="grammar",
        part_name="Grammar & Vocabulary B1",
        title="Ngữ pháp & Từ vựng B1: Cặp từ Đồng nghĩa & Cụm Collocations",
        description="Bảng ghép cặp từ vựng đồng nghĩa chuẩn đề Aptis và cấu trúc Make vs Do thường gặp trong bài thi.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-primary mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-spellcheck me-2"></i>Bảng từ vựng đồng nghĩa (Synonyms) rút từ bộ đề thi thực tế</h5>
    <p class="mb-0 small">Xuất hiện 100% trong phần thi Vocabulary Matching của Aptis</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Cặp từ đồng nghĩa hay gặp nhất trong đề thi</h4>
  <table class="table table-hover table-bordered table-sm mb-3">
    <thead class="table-primary">
      <tr><th>Từ đề bài</th><th>Từ đồng nghĩa chuẩn</th><th>Nghĩa tiếng Việt</th></tr>
    </thead>
    <tbody>
      <tr><td><b>itinerary</b></td><td>schedule</td><td>Lịch trình chuyến đi</td></tr>
      <tr><td><b>accommodation</b></td><td>lodging</td><td>Nơi ở, chỗ lưu trú</td></tr>
      <tr><td><b>souvenir</b></td><td>keepsake</td><td>Quà lưu niệm</td></tr>
      <tr><td><b>luggage</b></td><td>baggage</td><td>Hành lý</td></tr>
      <tr><td><b>applicant</b></td><td>candidate</td><td>Ứng viên xin việc</td></tr>
      <tr><td><b>annual</b></td><td>yearly</td><td>Hàng năm</td></tr>
      <tr><td><b>commence</b></td><td>begin / start</td><td>Bắt đầu</td></tr>
    </tbody>
  </table>

  <h4 class="fw-bold text-primary mt-3">2. Phân biệt Cụm từ đi liền Collocations: MAKE vs DO</h4>
  <div class="row g-3 mb-3">
    <div class="col-md-6">
      <div class="p-3 bg-light rounded border-start border-4 border-primary">
        <h6 class="fw-bold text-primary">Cụm đi với MAKE (Tạo ra cái mới)</h6>
        <ul class="mb-0 small">
          <li>make a decision (đưa ra quyết định)</li>
          <li>make progress (tiến bộ)</li>
          <li>make an appointment (hẹn gặp)</li>
          <li>make a mistake (phạm lỗi)</li>
        </ul>
      </div>
    </div>
    <div class="col-md-6">
      <div class="p-3 bg-light rounded border-start border-4 border-info">
        <h6 class="fw-bold text-info">Cụm đi với DO (Thực hiện nhiệm vụ)</h6>
        <ul class="mb-0 small">
          <li>do business (kinh doanh)</li>
          <li>do research (nghiên cứu)</li>
          <li>do homework (làm bài tập)</li>
          <li>do household chores (làm việc nhà)</li>
        </ul>
      </div>
    </div>
  </div>
</div>
""",
        practice_url="/grammar_test002.html",
        target_pass_score=75.0,
        order_num=1,
        icon="bi-spellcheck",
    )

    n2_2 = RoadmapNode(
        stage_id=s2.id,
        skill="grammar",
        part_name="Grammar B1 Special",
        title="Ngữ pháp B1 Chuyên đề: Liên Từ & Từ Nối Logic (Linking Words)",
        description="Mẹo phân biệt Although / Despite, However / Therefore xuất hiện liên tục trong bài thi Grammar & Reading.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-primary mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-diagram-2-fill me-2"></i>Bí quyết phân biệt Liên Từ Chỉ Nhượng Bộ & Nguyên Nhân</h5>
    <p class="mb-0 small">Xuất hiện trong các câu hỏi phân loại B1/B2 của bài thi Grammar</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Phân biệt Although / Even though vs Despite / In spite of</h4>
  <table class="table table-bordered table-sm mb-3">
    <thead class="table-primary">
      <tr><th>Cấu trúc</th><th>Công thức đi kèm</th><th>Ví dụ thực tế trong đề</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Although / Even though</b></td>
        <td><code>+ Subject + Verb</code> (Mệnh đề)</td>
        <td><i><u>Although</u> it rained heavily, we went out.</i></td>
      </tr>
      <tr>
        <td><b>Despite / In spite of</b></td>
        <td><code>+ Noun / V-ing / the fact that</code></td>
        <td><i><u>Despite</u> the heavy rain, we went out.</i></td>
      </tr>
    </tbody>
  </table>

  <h4 class="fw-bold text-primary mt-3">2. Liên từ nối 2 mệnh đề độc lập: However, Therefore, Consequently</h4>
  <ul>
    <li><b>However (Tuy nhiên):</b> Nối 2 vế đối lập. <i>"The exam was hard. <u>However</u>, she passed."</i></li>
    <li><b>Therefore / Consequently (Vì vậy):</b> Chỉ kết quả kéo theo. <i>"He didn't study. <u>Therefore</u>, he failed."</i></li>
  </ul>
</div>
""",
        practice_url="/grammar_test003.html",
        target_pass_score=75.0,
        order_num=2,
        icon="bi-link-45deg",
    )

    n2_3 = RoadmapNode(
        stage_id=s2.id,
        skill="reading",
        part_name="Reading Part 2",
        title="Reading Part 2: Sắp xếp đoạn văn Logic & Dấu hiệu liên kết thời gian",
        description="Phương pháp xác định câu mở đầu và cách liên kết các sự kiện theo trình tự thời gian.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-info mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-sort-numeric-down me-2"></i>Chiến thuật giải quyết Reading Part 2 (Text Cohesion)</h5>
    <p class="mb-0 small">Sắp xếp 5-6 câu văn rời rạc thành một bài tiểu sử hoặc câu chuyện hoàn chỉnh.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Quy tắc tìm câu mở đầu (Sentence 1)</h4>
  <ul>
    <li>Câu mở đầu là câu chứa danh từ riêng hoặc giới thiệu nhân vật chính.</li>
    <li><b>KHÔNG chọn:</b> Các câu bắt đầu bằng <i>He, She, They, It, This, However, But, So</i>.</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Chuỗi từ nối chỉ trình tự thời gian</h4>
  <p><b>First -> Then / Next -> Afterwards -> In the end / Finally</b></p>
</div>
""",
        practice_url="/reading_question2.html",
        target_pass_score=75.0,
        order_num=3,
        icon="bi-sort-alpha-down",
    )

    n2_4 = RoadmapNode(
        stage_id=s2.id,
        skill="reading",
        part_name="Reading Part 3",
        title="Reading Part 3: Ghép quan điểm 4 người & Kỹ thuật Paraphrasing",
        description="Kỹ thuật tìm từ đồng nghĩa đối chiếu 7 câu hỏi với bài đọc của 4 nhân vật Person A, B, C, D.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-info mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-card-checklist me-2"></i>Bí quyết Reading Part 3 (Opinion Matching)</h5>
    <p class="mb-0 small">Đọc ý kiến 4 người về cùng một chủ đề (du lịch, công việc, thói quen) và chọn nhân vật phù hợp.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">Quy trình 2 bước làm bài nhanh:</h4>
  <ol>
    <li>Đọc 7 câu hỏi và <b>gạch chân từ khóa chính</b> (Keywords).</li>
    <li>Quét bài đọc từng người (Scan) để tìm <b>từ đồng nghĩa (Paraphrasing)</b> thay vì tìm từ giống hệt 100%.</li>
  </ol>
</div>
""",
        practice_url="/reading_question5.html",
        target_pass_score=75.0,
        order_num=4,
        icon="bi-card-checklist",
    )

    n2_5 = RoadmapNode(
        stage_id=s2.id,
        skill="listening",
        part_name="Listening Part 2 & 3",
        title="Listening Part 2 & 3: Phân tích ý kiến Man / Woman / Both",
        description="Dấu hiệu từ vựng nhận biết sự đồng ý hoặc phản đối giữa 2 người đối thoại trong Part 3.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-warning mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-headphones me-2"></i>Bắt từ khóa phân định quan điểm Người Nam / Nữ / Cả hai</h5>
    <p class="mb-0 small">Listening Part 3 yêu cầu xác định ai là người có ý kiến được đề cập.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Dấu hiệu CẢ HAI CÙNG ĐỒNG Ý (Both)</h4>
  <ul>
    <li><i>"I couldn't agree more!"</i> (Tôi hoàn toàn đồng ý)</li>
    <li><i>"You can say that again."</i> (Chắc chắn rồi)</li>
    <li><i>"That's exactly what I think."</i> (Đó chính là điều tôi nghĩ)</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Dấu hiệu BẤT ĐỒNG / CHỈ MỘT NGƯỜI ĐỒNG Ý</h4>
  <ul>
    <li><i>"I'm not so sure about that."</i> -> Người nói phản đối.</li>
    <li><i>"On the other hand, I believe..."</i> -> Đưa ra ý kiến trái ngược.</li>
  </ul>
</div>
""",
        practice_url="/listening_question15.html",
        target_pass_score=75.0,
        order_num=5,
        icon="bi-headphones",
    )

    n2_6 = RoadmapNode(
        stage_id=s2.id,
        skill="writing",
        part_name="Writing Part 3",
        title="Writing Part 3: Chat nhóm câu lạc bộ (Social Club Chat)",
        description="Cách trả lời 3 câu hỏi chat với các thành viên câu lạc bộ (30-40 từ/câu) dùng văn phong Semi-formal.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-success mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-chat-dots-fill me-2"></i>Kỹ thuật viết Writing Part 3 (Club Chat Room)</h5>
    <p class="mb-0 small">Viết 3 câu trả lời ngắn (30-40 từ mỗi câu) tương tác với 3 thành viên khác nhau.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Nguyên tắc văn phong Chat nhóm</h4>
  <ul>
    <li>Sử dụng văn phong <b>Friendly & Semi-formal</b> (Thân thiện, tự nhiên nhưng lịch sự).</li>
    <li>Đảm bảo đủ độ dài <b>30 - 40 từ</b> mỗi câu trả lời.</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Cụm từ mở đầu nêu ý kiến ấn tượng</h4>
  <ul>
    <li><i>"Hi everyone! In my opinion, ..."</i></li>
    <li><i>"Personally speaking, I reckon that ..."</i></li>
    <li><i>"From my perspective, ..."</i></li>
  </ul>

  <div class="p-3 bg-light rounded border-start border-4 border-success mb-3">
    <h6 class="fw-bold text-success">Bài mẫu thực tế (Chủ đề Gardening Club):</h6>
    <p class="mb-1"><b>Q:</b> <i>"Welcome to the Gardening Club! Why did you join?"</i></p>
    <p class="mb-0"><b>Ans:</b> <i>"Hello everyone! I joined this club because I am really enthusiastic about growing organic vegetables and flowers at home. I hope to learn helpful gardening techniques from experienced members and share my passion!"</i> (36 từ)</p>
  </div>
</div>
""",
        practice_url="/writingkey001.html",
        target_pass_score=75.0,
        order_num=6,
        icon="bi-chat-dots-fill",
    )

    n2_7 = RoadmapNode(
        stage_id=s2.id,
        skill="speaking",
        part_name="Speaking Part 2 & 3",
        title="Speaking Part 2 & 3: Miêu tả & So sánh bức ảnh (45s/câu)",
        description="Bộ từ vựng vị trí không gian và liên từ so sánh hai bức ảnh trôi chảy trong 45 giây.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-danger mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-images me-2"></i>Cấu trúc nói miêu tả & so sánh ảnh (Speaking P2 & P3)</h5>
    <p class="mb-0 small">Part 2: Miêu tả 1 ảnh (45s) + 2 câu hỏi. Part 3: So sánh 2 ảnh (45s) + 2 câu hỏi.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Từ vựng chỉ vị trí không gian trong ảnh</h4>
  <ul>
    <li><b>In the center / foreground:</b> Ở trung tâm / phía trước của ảnh.</li>
    <li><b>In the background:</b> Ở phía hậu cảnh / đằng sau.</li>
    <li><b>On the left / right-hand side:</b> Ở bên tay trái / tay phải.</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Mẫu câu so sánh 2 bức ảnh (Part 3)</h4>
  <p>Sử dụng liên từ đối lập: <b>While, Whereas, In contrast, On the one hand... on the other hand</b></p>
  <div class="p-3 bg-light rounded border-start border-4 border-danger mb-3">
    <p class="mb-0 italic">"<b>While the first picture shows</b> a crowded modern office where people are working on computers, <b>the second picture depicts</b> a serene countryside farm with workers outdoors in fresh air."</p>
  </div>
</div>
""",
        practice_url="/speaking_question2_practice.html",
        target_pass_score=75.0,
        order_num=7,
        icon="bi-images",
    )

    db.add_all([n2_1, n2_2, n2_3, n2_4, n2_5, n2_6, n2_7])

    # =========================================================================
    # CHẶNG 3: MASTERY (TARGET B2 - C) - 7 BÀI HỌC
    # =========================================================================
    s3 = RoadmapStage(
        title="Chặng 3: Chinh Phục Điểm Cao (Target B2 - C)",
        target_band="B2-C",
        description="Chinh phục các phần thi dài, đòi hỏi tư duy phân tích, từ vựng nâng cao và viết email chuẩn mực.",
        order_num=3,
        icon="bi-trophy-fill",
    )
    db.add(s3)
    db.flush()

    n3_1 = RoadmapNode(
        stage_id=s3.id,
        skill="grammar",
        part_name="Grammar B2-C Special",
        title="Ngữ pháp B2-C: Modal Verbs of Deduction & Cấu trúc Used to",
        description="Mẹo suy đoán sự việc (Must be, Can't be) và phân biệt Used to + V vs Be used to + V-ing.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-primary mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-lightbulb-fill me-2"></i>Động Từ Khuyết Thiếu Suy Đoán & Thói Quên</h5>
    <p class="mb-0 small">Các câu hỏi nâng cao phân loại Band B2 - C trong bài thi Grammar</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Động từ khuyết thiếu suy đoán (Modal Verbs of Deduction)</h4>
  <ul>
    <li><b>MUST + V-bare (Suy đoán chắc chắn đúng 99%):</b> <i>She is not answering. She <u>must be</u> busy.</i></li>
    <li><b>CAN'T + V-bare (Suy đoán chắc chắn không xảy ra):</b> <i>He just ate a huge meal. He <u>can't be</u> hungry.</i></li>
    <li><b>MIGHT / MAY + V-bare (Suy đoán có thể xảy ra ~50%):</b> <i>It <u>might</u> rain later tonight.</i></li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Phân biệt USED TO vs BE USED TO</h4>
  <table class="table table-bordered table-sm mb-3">
    <thead class="table-primary">
      <tr><th>Cấu trúc</th><th>Ý nghĩa</th><th>Ví dụ</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><code>S + used to + V-bare</code></td>
        <td>Thói quen trong quá khứ (nay không còn)</td>
        <td><i>He <u>used to</u> collect stamps when he was young.</i></td>
      </tr>
      <tr>
        <td><code>S + be/get used to + V-ing/N</code></td>
        <td>Đã quen với việc gì ở hiện tại</td>
        <td><i>She is <u>used to driving</u> on the left.</i></td>
      </tr>
    </tbody>
  </table>
</div>
""",
        practice_url="/grammar_test004.html",
        target_pass_score=80.0,
        order_num=1,
        icon="bi-journal-medical",
    )

    n3_2 = RoadmapNode(
        stage_id=s3.id,
        skill="grammar",
        part_name="Vocab Advanced Topics",
        title="Từ vựng Chuyên sâu B2-C: Công việc, Môi trường & Sức khỏe",
        description="Từ vựng học thuật cao cấp rút từ các bài đọc và bài nghe chủ đề chuyên môn của Aptis.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-primary mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-book-fill me-2"></i>Bộ Từ Vựng Học Thuật B2 - C Theo Chủ Đề</h5>
    <p class="mb-0 small">Phục vụ trực tiếp bài thi Reading Part 4 & Writing Part 4</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Chủ đề Công việc & Sự nghiệp (Workplace & Career)</h4>
  <ul>
    <li><b>qualification</b> (n): Bằng cấp, năng lực chuyên môn</li>
    <li><b>curriculum vitae / resume</b> (n): Sơ yếu lý lịch</li>
    <li><b>take responsibility for</b> (v): Chịu trách nhiệm cho...</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Chủ đề Môi trường & Sức khỏe (Environment & Health)</h4>
  <ul>
    <li><b>conservation</b> (n): Sự bảo tồn thiên nhiên</li>
    <li><b>eco-friendly / sustainable</b> (adj): Thân thiện với môi trường / Bền vững</li>
    <li><b>nutritious diet</b> (n): Chế độ ăn uống giàu dinh dưỡng</li>
  </ul>
</div>
""",
        practice_url="/grammar_test005.html",
        target_pass_score=80.0,
        order_num=2,
        icon="bi-bookmark-star-fill",
    )

    n3_3 = RoadmapNode(
        stage_id=s3.id,
        skill="reading",
        part_name="Reading Part 4",
        title="Reading Part 4: Đọc hiểu bài văn dài 750 từ & Chọn Tiêu Đề",
        description="Phương pháp phân tích câu mở đầu (Topic Sentence) để chọn đúng tiêu đề cho từng đoạn văn.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-primary mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-file-earmark-text-fill me-2"></i>Kỹ thuật làm Reading Part 4 (Heading Matching)</h5>
    <p class="mb-0 small">Xử lý bài văn dài 750 từ gồm 7 đoạn văn học thuật.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Nguyên tắc Skimming xác định Topic Sentence</h4>
  <ul>
    <li>Đọc <b>2 câu đầu tiên</b> và <b>1 câu cuối cùng</b> của từng đoạn văn. Ý chính của đoạn luôn nằm ở các câu này.</li>
    <li>Chú ý các từ nối chuyển ý mang tính quyết định: <i>However, Despite this, On the contrary, Furthermore</i>.</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Tránh bẫy "Từ trùng lặp" (Word Spotting Trap)</h4>
  <p>Một tiêu đề sai thường cố tình chứa một từ chính xác có trong đoạn văn nhưng nội dung tổng thể lại không phải ý chính của đoạn.</p>
</div>
""",
        practice_url="/reading_question4.html",
        target_pass_score=80.0,
        order_num=3,
        icon="bi-file-earmark-text-fill",
    )

    n3_4 = RoadmapNode(
        stage_id=s3.id,
        skill="listening",
        part_name="Listening Part 4",
        title="Listening Part 4: Nghe bài phát biểu / Bài nói dài (Extended Speech)",
        description="Cách bắt ý chính (Gist) và theo dõi từ nối dẫn dắt cấu trúc bài thuyết trình chuyên sâu.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-warning mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-megaphone-fill me-2"></i>Kỹ năng nghe Monologue bài nói dài (Part 4)</h5>
    <p class="mb-0 small">Nghe 1 bài phát biểu / phỏng vấn chuyên sâu 2 phút và trả lời các câu hỏi chọn đáp án.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Bắt các Signposting Words (Từ đánh dấu cấu trúc)</h4>
  <ul>
    <li><b>Mở đầu:</b> <i>"To begin with...", "First of all..."</i></li>
    <li><b>Chuyển ý:</b> <i>"Moving on to the next point...", "Turning now to..."</i></li>
    <li><b>Tóm tắt kết luận:</b> <i>"In summary...", "To sum up...", "Ultimately..."</i></li>
  </ul>
</div>
""",
        practice_url="/listening_question16_17.html",
        target_pass_score=80.0,
        order_num=4,
        icon="bi-megaphone-fill",
    )

    n3_5 = RoadmapNode(
        stage_id=s3.id,
        skill="writing",
        part_name="Writing Part 4",
        title="Writing Part 4: Viết Email Thân Mật (50 từ) & Email Trang Trọng (120-150 từ)",
        description="Bảng so sánh chi tiết văn phong Informal vs Formal rút từ 40 bộ đề Writing thực tế của AptisKey.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-success mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-envelope-paper-fill me-2"></i>Bảng so sánh văn phong Email Writing Part 4 chuẩn B2-C</h5>
    <p class="mb-0 small">Rút từ kho 40 bộ đề mẫu `writingkey001.html` đến `writingkey040.html`</p>
  </div>

  <table class="table table-bordered table-striped mb-3">
    <thead class="table-success">
      <tr>
        <th>Tiêu chí</th>
        <th>Informal Email (Gửi bạn bè - ~50 từ)</th>
        <th>Formal Email (Gửi Ban Quản Lý - 120-150 từ)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Mở bài</b></td>
        <td>Hi John, / Dear Mark,</td>
        <td>Dear Sir or Madam, / Dear Mr. President,</td>
      </tr>
      <tr>
        <td><b>Viết tắt</b></td>
        <td>Được dùng (I'm, can't, don't, it's)</td>
        <td><span class="text-danger fw-bold">KHÔNG được dùng viết tắt</span> (I am, cannot, do not)</td>
      </tr>
      <tr>
        <td><b>Từ nối</b></td>
        <td>Also, Besides, Plus</td>
        <td>Furthermore, In addition, Consequently</td>
      </tr>
      <tr>
        <td><b>Cụm từ phàn nàn</b></td>
        <td>I'm really annoyed about...</td>
        <td>I am writing to express my strong dissatisfaction regarding...</td>
      </tr>
      <tr>
        <td><b>Kết bài</b></td>
        <td>Best wishes, / See you soon!</td>
        <td>Yours sincerely, / Yours faithfully,</td>
      </tr>
    </tbody>
  </table>

  <div class="p-3 bg-light rounded border-start border-4 border-success mb-3">
    <h6 class="fw-bold text-success">Mẫu câu mở đầu Formal Email ghi điểm cao:</h6>
    <p class="mb-0 italic">"I am writing this email to formally express my disappointment regarding the recent unexpected changes to our club's operating schedule..."</p>
  </div>
</div>
""",
        practice_url="/writingkey005.html",
        target_pass_score=80.0,
        order_num=5,
        icon="bi-envelope-paper-fill",
    )

    n3_6 = RoadmapNode(
        stage_id=s3.id,
        skill="writing",
        part_name="Writing Intensive",
        title="Writing Intensive: Kỹ Thuật Phàn Nàn & Đề Xuất Giải Pháp (Formal Email)",
        description="Mẫu câu phàn nàn lịch sự và cấu trúc đề xuất giải pháp đạt điểm Band C trong Formal Email.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-success mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-exclamation-square-fill me-2"></i>Mẫu câu phàn nàn lịch sự & Đề xuất giải pháp (Formal Email)</h5>
    <p class="mb-0 small">Kỹ năng quan trọng nhất trong bài thi Writing Part 4</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Cấu trúc bày tỏ sự thất vọng lịch sự</h4>
  <ul>
    <li><i>"I am writing to register my dissatisfaction with..."</i></li>
    <li><i>"I was extremely disappointed to learn that..."</i></li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Cấu trúc đưa ra giải pháp đề xuất</h4>
  <ul>
    <li><i>"I would be grateful if you could consider..."</i></li>
    <li><i>"I strongly suggest that the club should organize..."</i></li>
    <li><i>"To resolve this issue, I believe it would be beneficial to..."</i></li>
  </ul>
</div>
""",
        practice_url="/writingkey010.html",
        target_pass_score=80.0,
        order_num=6,
        icon="bi-file-earmark-post-fill",
    )

    n3_7 = RoadmapNode(
        stage_id=s3.id,
        skill="speaking",
        part_name="Speaking Part 4",
        title="Speaking Part 4: Thuyết trình quan điểm 3 câu hỏi (2 phút)",
        description="Quy trình 1 phút nháp ý chính và 2 phút trình trình bày mạch lạc chuẩn tiêu chí chấm điểm British Council.",
        theory_content="""
<div class="knowledge-content">
  <div class="alert alert-danger mb-3">
    <h5 class="fw-bold mb-1"><i class="bi bi-display-fill me-2"></i>Quy trình 1 phút chuẩn bị + 2 phút phát biểu (Speaking Part 4)</h5>
    <p class="mb-0 small">Nhìn tranh/chủ đề và 3 câu hỏi gợi ý để thực hiện bài nói thuyết trình 2 phút.</p>
  </div>

  <h4 class="fw-bold text-primary mt-3">1. Chiến thuật 1 phút suy nghĩ (Preparation Time)</h4>
  <ul>
    <li>Viết nhanh 3-4 cụm từ khóa (Keywords) ứng với 3 câu hỏi lên giấy nháp.</li>
    <li>Không ghi cả câu dài, chỉ ghi từ nối và ý chính.</li>
  </ul>

  <h4 class="fw-bold text-primary mt-3">2. Phân bổ thời gian trong 2 phút nói</h4>
  <table class="table table-bordered table-sm mb-3">
    <thead class="table-danger">
      <tr><th>Phần nói</th><th>Thời gian</th><th>Cụm từ dẫn dắt</th></tr>
    </thead>
    <tbody>
      <tr><td>Mở bài</td><td>15 giây</td><td>Today, I would like to share my perspective on...</td></tr>
      <tr><td>Thân bài (3 câu hỏi)</td><td>90 giây</td><td>First and foremost... Moving to the second question... Last but not least...</td></tr>
      <tr><td>Kết luận</td><td>15 giây</td><td>To wrap up, I firmly believe that...</td></tr>
    </tbody>
  </table>
</div>
""",
        practice_url="/speaking_question4_practice.html",
        target_pass_score=80.0,
        order_num=7,
        icon="bi-display-fill",
    )

    db.add_all([n3_1, n3_2, n3_3, n3_4, n3_5, n3_6, n3_7])
    db.commit()


@router.get("/recommendations", response_model=AIRecommendationSummary)
def get_ai_recommendations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Lấy danh sách các bài học được AI đề xuất riêng dựa trên điểm yếu của học viên."""
    if not current_user:
        # Nếu là khách chưa đăng nhập
        return AIRecommendationSummary(
            has_data=False,
            ai_advice="🤖 AI Assistant: Vui lòng đăng nhập hoặc làm bài test 15 phút để AI có dữ liệu đề xuất bài học cá nhân hóa cho bạn!",
            weak_skills=[],
            recommended_nodes=[],
            skill_scores={}
        )

    analysis = _analyze_user_weaknesses(current_user.id, db)
    rec_node_ids = analysis["recommended_node_ids"]
    
    recommended_nodes_data = []
    user_progs = {p.node_id: p for p in db.query(UserRoadmapProgress).filter(UserRoadmapProgress.user_id == current_user.id).all()}

    for node_id in rec_node_ids:
        node = db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()
        if node:
            prog = user_progs.get(node.id)
            recom_badge = analysis["recommendations_map"].get(node.id)
            status_val = prog.status.value if prog else "locked"
            score_val = prog.highest_score if prog else 0.0
            stars_val = prog.stars if prog else 0

            recommended_nodes_data.append(
                RoadmapNodeRead(
                    id=node.id,
                    stage_id=node.stage_id,
                    skill=node.skill,
                    part_name=node.part_name,
                    title=node.title,
                    description=node.description,
                    theory_content=node.theory_content,
                    practice_url=node.practice_url,
                    test_id=node.test_id,
                    target_pass_score=node.target_pass_score,
                    is_vip=node.is_vip,
                    order_num=node.order_num,
                    icon=node.icon,
                    user_status=status_val,
                    highest_score=score_val,
                    stars=stars_val,
                    recommendation=recom_badge,
                )
            )

    return AIRecommendationSummary(
        has_data=analysis["has_data"],
        ai_advice=analysis["ai_advice"],
        weak_skills=analysis["weak_skills"],
        recommended_nodes=recommended_nodes_data,
        skill_scores=analysis["skill_scores"]
    )
