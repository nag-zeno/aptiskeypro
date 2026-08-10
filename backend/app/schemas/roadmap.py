from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel


class NodeProgressRead(BaseModel):
    status: str
    highest_score: float
    stars: int
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NodeRecommendationBadge(BaseModel):
    is_recommended: bool = False
    priority: str = "medium"  # high, medium
    reason: str = ""


class RoadmapNodeRead(BaseModel):
    id: int
    stage_id: int
    skill: str
    part_name: str
    title: str
    description: Optional[str] = None
    theory_content: Optional[str] = None
    practice_url: Optional[str] = None
    test_id: Optional[int] = None
    target_pass_score: float
    is_vip: int
    order_num: int
    icon: str
    user_status: str = "locked"
    highest_score: float = 0.0
    stars: int = 0
    recommendation: Optional[NodeRecommendationBadge] = None

    class Config:
        from_attributes = True


class RoadmapStageRead(BaseModel):
    id: int
    title: str
    target_band: str
    description: Optional[str] = None
    order_num: int
    icon: str
    nodes: List[RoadmapNodeRead] = []

    class Config:
        from_attributes = True


class RoadmapTreeResponse(BaseModel):
    target_band: str
    current_stage_id: Optional[int] = None
    streak_days: int = 1
    total_nodes: int = 0
    completed_nodes: int = 0
    total_stars: int = 0
    progress_percentage: float = 0.0
    stages: List[RoadmapStageRead] = []


class UserProgressUpdate(BaseModel):
    score: float


class UserProgressResponse(BaseModel):
    node_id: int
    status: str
    highest_score: float
    stars: int
    unlocked_next_node_id: Optional[int] = None
    message: str


class LearningProfileUpdate(BaseModel):
    target_band: str


class AIRecommendationSummary(BaseModel):
    has_data: bool = False
    ai_advice: str = ""
    weak_skills: List[str] = []
    recommended_nodes: List[RoadmapNodeRead] = []
    skill_scores: Dict[str, float] = {}
