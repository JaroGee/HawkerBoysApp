from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List, Optional

from .models import (
    Badge,
    Mission,
    MissionProgress,
    MissionTask,
    SupportRequest,
    TaskProgress,
    Trainee,
    TraineeBadge,
)


class BaseStorage:
    def list_trainees(self) -> List[Trainee]:
        raise NotImplementedError

    def get_trainee(self, trainee_id: str) -> Optional[Trainee]:
        raise NotImplementedError

    def save_trainee(self, trainee: Trainee) -> None:
        raise NotImplementedError

    def list_missions_for_trainee(self, trainee_id: str) -> List[Mission]:
        raise NotImplementedError

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        raise NotImplementedError

    def save_mission(self, mission: Mission) -> None:
        raise NotImplementedError

    def list_tasks_for_mission(self, mission_id: str) -> List[MissionTask]:
        raise NotImplementedError

    def save_task(self, task: MissionTask) -> None:
        raise NotImplementedError

    def get_task(self, task_id: str) -> Optional[MissionTask]:
        raise NotImplementedError

    def save_task_progress(self, progress: TaskProgress) -> None:
        raise NotImplementedError

    def list_task_progress_for_trainee(self, trainee_id: str) -> List[TaskProgress]:
        raise NotImplementedError

    def save_mission_progress(self, progress: MissionProgress) -> None:
        raise NotImplementedError

    def list_mission_progress_for_trainee(self, trainee_id: str) -> List[MissionProgress]:
        raise NotImplementedError

    def save_support_request(self, request: SupportRequest) -> None:
        raise NotImplementedError

    def list_support_requests(self) -> List[SupportRequest]:
        raise NotImplementedError

    def add_badge(self, badge: Badge) -> None:
        raise NotImplementedError

    def list_badges(self) -> List[Badge]:
        raise NotImplementedError

    def award_badge(self, trainee_badge: TraineeBadge) -> None:
        raise NotImplementedError

    def list_badges_for_trainee(self, trainee_id: str) -> List[TraineeBadge]:
        raise NotImplementedError


class InMemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self.trainees: Dict[str, Trainee] = {}
        self.missions: Dict[str, Mission] = {}
        self.tasks: Dict[str, MissionTask] = {}
        self.mission_progress: Dict[tuple[str, str], MissionProgress] = {}
        self.task_progress: Dict[tuple[str, str], TaskProgress] = {}
        self.badges: Dict[str, Badge] = {}
        self.trainee_badges: List[TraineeBadge] = []
        self.support_requests: Dict[str, SupportRequest] = {}
        self._seed_data()

    def _seed_data(self) -> None:
        demo_trainees = [
            Trainee(
                id="trainee-1",
                name="Aisha Tan",
                cohort="Cohort Orion",
                current_stage="Skills Training",
                overall_xp=220,
                kitchen_xp=140,
                stall_ops_xp=60,
                life_mindset_xp=20,
            ),
            Trainee(
                id="trainee-2",
                name="Marcus Lim",
                cohort="Cohort Orion",
                current_stage="Orientation",
                overall_xp=80,
                kitchen_xp=40,
                stall_ops_xp=20,
                life_mindset_xp=20,
            ),
        ]
        for trainee in demo_trainees:
            self.save_trainee(trainee)

        mission_one = Mission(
            id="mission-1",
            title="Knife Skills Foundations",
            description="Practice safe handling and precision cuts for daily prep.",
            stage="Skills Training",
            active_from=date.today(),
            total_xp_reward=120,
        )
        mission_two = Mission(
            id="mission-2",
            title="Orientation Day",
            description="Meet the team, tour the kitchen, and understand safety basics.",
            stage="Orientation",
            active_from=date.today(),
            total_xp_reward=80,
        )
        for mission in (mission_one, mission_two):
            self.save_mission(mission)

        tasks = [
            MissionTask(
                id="task-1",
                mission_id="mission-1",
                title="Julienne practice",
                description="Consistent julienne cut on carrots and cucumbers.",
                track="kitchen",
                xp_reward=40,
                auto_complete=True,
            ),
            MissionTask(
                id="task-2",
                mission_id="mission-1",
                title="Knife safety review",
                description="Review safety checklist with mentor.",
                track="life_mindset",
                xp_reward=40,
                auto_complete=False,
            ),
            MissionTask(
                id="task-3",
                mission_id="mission-1",
                title="Prep station setup",
                description="Lay out tools and ingredients efficiently.",
                track="stall_ops",
                xp_reward=40,
                auto_complete=True,
            ),
            MissionTask(
                id="task-4",
                mission_id="mission-2",
                title="Kitchen tour",
                description="Walkthrough of the training kitchen with mentor.",
                track="stall_ops",
                xp_reward=40,
                auto_complete=True,
            ),
            MissionTask(
                id="task-5",
                mission_id="mission-2",
                title="Safety briefing",
                description="Learn emergency procedures and hygiene standards.",
                track="life_mindset",
                xp_reward=40,
                auto_complete=False,
            ),
        ]
        for task in tasks:
            self.save_task(task)

        badge_catalog = [
            Badge(id="badge-1", name="First Mission Complete", description="Completed a first mission."),
            Badge(id="badge-2", name="Five Missions Complete", description="Completed five missions."),
            Badge(id="badge-3", name="Orientation Complete", description="Completed the Orientation stage."),
        ]
        for badge in badge_catalog:
            self.add_badge(badge)

    def list_trainees(self) -> List[Trainee]:
        return list(self.trainees.values())

    def get_trainee(self, trainee_id: str) -> Optional[Trainee]:
        return self.trainees.get(trainee_id)

    def save_trainee(self, trainee: Trainee) -> None:
        self.trainees[trainee.id] = trainee

    def list_missions_for_trainee(self, trainee_id: str) -> List[Mission]:
        trainee = self.get_trainee(trainee_id)
        if not trainee:
            return []
        return [mission for mission in self.missions.values() if mission.stage is None or mission.stage == trainee.current_stage]

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self.missions.get(mission_id)

    def save_mission(self, mission: Mission) -> None:
        self.missions[mission.id] = mission

    def list_tasks_for_mission(self, mission_id: str) -> List[MissionTask]:
        return [task for task in self.tasks.values() if task.mission_id == mission_id]

    def save_task(self, task: MissionTask) -> None:
        self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Optional[MissionTask]:
        return self.tasks.get(task_id)

    def save_task_progress(self, progress: TaskProgress) -> None:
        key = (progress.trainee_id, progress.task_id)
        self.task_progress[key] = progress
        mission_id = self.tasks.get(progress.task_id).mission_id if progress.task_id in self.tasks else None
        if mission_id:
            self._update_mission_progress(progress.trainee_id, mission_id)

    def list_task_progress_for_trainee(self, trainee_id: str) -> List[TaskProgress]:
        return [p for key, p in self.task_progress.items() if key[0] == trainee_id]

    def save_mission_progress(self, progress: MissionProgress) -> None:
        key = (progress.trainee_id, progress.mission_id)
        self.mission_progress[key] = progress

    def list_mission_progress_for_trainee(self, trainee_id: str) -> List[MissionProgress]:
        return [p for key, p in self.mission_progress.items() if key[0] == trainee_id]

    def _update_mission_progress(self, trainee_id: str, mission_id: str) -> None:
        tasks = self.list_tasks_for_mission(mission_id)
        progress_entries = [self.task_progress.get((trainee_id, task.id)) for task in tasks]
        completed = sum(1 for item in progress_entries if item and item.status == "completed")
        status = "not_started"
        if completed:
            status = "in_progress"
        if completed == len(tasks) and tasks:
            status = "completed"
        self.save_mission_progress(
            MissionProgress(trainee_id=trainee_id, mission_id=mission_id, status=status)
        )

    def save_support_request(self, request: SupportRequest) -> None:
        self.support_requests[request.id] = request

    def list_support_requests(self) -> List[SupportRequest]:
        return sorted(self.support_requests.values(), key=lambda r: r.created_at, reverse=True)

    def add_badge(self, badge: Badge) -> None:
        self.badges[badge.id] = badge

    def list_badges(self) -> List[Badge]:
        return list(self.badges.values())

    def award_badge(self, trainee_badge: TraineeBadge) -> None:
        existing = [(tb.trainee_id, tb.badge_id) for tb in self.trainee_badges]
        key = (trainee_badge.trainee_id, trainee_badge.badge_id)
        if key not in existing:
            self.trainee_badges.append(trainee_badge)

    def list_badges_for_trainee(self, trainee_id: str) -> List[TraineeBadge]:
        return [tb for tb in self.trainee_badges if tb.trainee_id == trainee_id]


_storage_instance: Optional[BaseStorage] = None


def get_storage() -> BaseStorage:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = InMemoryStorage()
    return _storage_instance


__all__ = [
    "BaseStorage",
    "InMemoryStorage",
    "get_storage",
]
