import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProgressStatus(str, enum.Enum):
    locked = "locked"
    unlocked = "unlocked"
    completed = "completed"


class TargetBand(str, enum.Enum):
    A1_A2 = "A1-A2"
    B1 = "B1"
    B2 = "B2"
    C = "C"


class RoadmapStage(Base):
    __tablename__ = "roadmap_stages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)          # VD: "Chặng 1: Nền tảng A1 - A2"
    target_band = Column(String, nullable=False)    # "A1-A2", "B1", "B2-C"
    description = Column(Text, nullable=True)
    order_num = Column(Integer, nullable=False, default=1)
    icon = Column(String, default="bi-compass")

    nodes = relationship("RoadmapNode", back_populates="stage", cascade="all, delete-orphan", order_by="RoadmapNode.order_num")


class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("roadmap_stages.id"), nullable=False, index=True)
    
    skill = Column(String, nullable=False)           # grammar, reading, listening, writing, speaking
    part_name = Column(String, nullable=False)       # VD: "Reading Part 1 - Hoàn thành câu"
    title = Column(String, nullable=False)           # VD: "Kỹ thuật chọn từ theo ngữ cảnh"
    description = Column(Text, nullable=True)
    
    theory_content = Column(Text, nullable=True)     # HTML / Markdown nội dung lý thuyết, mẹo thi
    practice_url = Column(String, nullable=True)     # Đường dẫn bài tập tĩnh hoặc tương tác
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=True) # Liên kết bài test trong DB nếu có
    
    target_pass_score = Column(Float, default=70.0)  # Điểm qua bài (%)
    is_vip = Column(Integer, default=0)              # 0: Free, 1: VIP
    order_num = Column(Integer, nullable=False, default=1)
    icon = Column(String, default="bi-journal-bookmark")

    stage = relationship("RoadmapStage", back_populates="nodes")
    user_progress = relationship("UserRoadmapProgress", back_populates="node", cascade="all, delete-orphan")


class UserRoadmapProgress(Base):
    __tablename__ = "user_roadmap_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("roadmap_nodes.id"), nullable=False, index=True)

    status = Column(SAEnum(ProgressStatus), default=ProgressStatus.locked, nullable=False)
    highest_score = Column(Float, default=0.0)
    stars = Column(Integer, default=0)                # 0, 1, 2, 3 sao
    completed_at = Column(DateTime, nullable=True)

    node = relationship("RoadmapNode", back_populates="user_progress")


class UserLearningProfile(Base):
    __tablename__ = "user_learning_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    target_band = Column(String, default="B1")        # "A2", "B1", "B2", "C"
    current_stage_id = Column(Integer, nullable=True)
    placement_score = Column(Float, nullable=True)
    streak_days = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
