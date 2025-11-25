from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class Trainee(BaseModel):
    id: str
    name: str
    cohort: Optional[str] = None
    current_stage: str
    overall_xp: int = 0
    kitchen_xp: int = 0
    stall_ops_xp: int = 0
    life_mindset_xp: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Mission(BaseModel):
    id: str
    title: str
    description: str
    stage: Optional[str] = None
    active_from: Optional[date] = None
    active_to: Optional[date] = None
    total_xp_reward: int = 0


class MissionTask(BaseModel):
    id: str
    mission_id: str
    title: str
    description: str
    track: str
    xp_reward: int
    auto_complete: bool = False


class MissionProgress(BaseModel):
    trainee_id: str
    mission_id: str
    status: str = "not_started"


class TaskProgress(BaseModel):
    trainee_id: str
    task_id: str
    status: str = "not_started"
    completed_at: Optional[datetime] = None
    approved_by: Optional[str] = None


class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: Optional[str] = None


class TraineeBadge(BaseModel):
    trainee_id: str
    badge_id: str
    awarded_at: datetime = Field(default_factory=datetime.utcnow)


class SupportRequest(BaseModel):
    id: str
    trainee_id: str
    message: str
    category: str = "Other"
    status: str = "new"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LevelSnapshot(BaseModel):
    overall_level: int
    kitchen_level: int
    stall_ops_level: int
    life_mindset_level: int

