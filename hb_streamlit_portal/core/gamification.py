from __future__ import annotations

from datetime import datetime
from typing import List, Sequence

from .models import LevelSnapshot, MissionProgress, MissionTask, TaskProgress, Trainee, TraineeBadge
from .storage import BaseStorage

XP_THRESHOLDS: Sequence[int] = [0, 100, 250, 500, 1000, 1500, 2500]


def compute_level(xp: int) -> int:
    level = 1
    for threshold in XP_THRESHOLDS:
        if xp >= threshold:
            level = XP_THRESHOLDS.index(threshold) + 1
    return level


def recalculate_levels(trainee: Trainee) -> LevelSnapshot:
    return LevelSnapshot(
        overall_level=compute_level(trainee.overall_xp),
        kitchen_level=compute_level(trainee.kitchen_xp),
        stall_ops_level=compute_level(trainee.stall_ops_xp),
        life_mindset_level=compute_level(trainee.life_mindset_xp),
    )


def award_task_xp(trainee: Trainee, task: MissionTask) -> Trainee:
    trainee.overall_xp += task.xp_reward
    if task.track == "kitchen":
        trainee.kitchen_xp += task.xp_reward
    if task.track == "stall_ops":
        trainee.stall_ops_xp += task.xp_reward
    if task.track == "life_mindset":
        trainee.life_mindset_xp += task.xp_reward
    return trainee


def evaluate_badges(storage: BaseStorage, trainee: Trainee) -> List[TraineeBadge]:
    earned: List[TraineeBadge] = []
    mission_progress = storage.list_mission_progress_for_trainee(trainee.id)
    completed_missions = [p for p in mission_progress if p.status == "completed"]

    if len(completed_missions) >= 1:
        earned.append(TraineeBadge(trainee_id=trainee.id, badge_id="badge-1"))
    if len(completed_missions) >= 5:
        earned.append(TraineeBadge(trainee_id=trainee.id, badge_id="badge-2"))

    orientation_completed = any(
        storage.get_mission(p.mission_id).stage == "Orientation" and p.status == "completed"
        for p in completed_missions
        if storage.get_mission(p.mission_id)
    )
    if orientation_completed:
        earned.append(TraineeBadge(trainee_id=trainee.id, badge_id="badge-3"))

    for badge in earned:
        storage.award_badge(badge)
    return earned


def record_task_completion(
    storage: BaseStorage, trainee: Trainee, task: MissionTask, requires_approval: bool
) -> TaskProgress:
    existing = storage.task_progress.get((trainee.id, task.id)) if hasattr(storage, "task_progress") else None
    if existing and existing.status == "completed":
        return existing

    status = "pending_approval" if requires_approval else "completed"
    progress = TaskProgress(
        trainee_id=trainee.id,
        task_id=task.id,
        status=status,
        completed_at=datetime.utcnow() if not requires_approval else None,
    )
    storage.save_task_progress(progress)
    if status == "completed":
        trainee = award_task_xp(trainee, task)
        storage.save_trainee(trainee)
        storage._update_mission_progress(trainee.id, task.mission_id)  # type: ignore[attr-defined]
        evaluate_badges(storage, trainee)
    return progress


def complete_task_with_approval(storage: BaseStorage, trainee: Trainee, task: MissionTask, approver: str) -> None:
    progress = TaskProgress(
        trainee_id=trainee.id,
        task_id=task.id,
        status="completed",
        completed_at=datetime.utcnow(),
        approved_by=approver,
    )
    storage.save_task_progress(progress)
    award_task_xp(trainee, task)
    storage.save_trainee(trainee)
    storage._update_mission_progress(trainee.id, task.mission_id)  # type: ignore[attr-defined]
    evaluate_badges(storage, trainee)


__all__ = [
    "XP_THRESHOLDS",
    "award_task_xp",
    "recalculate_levels",
    "compute_level",
    "evaluate_badges",
    "record_task_completion",
    "complete_task_with_approval",
]
