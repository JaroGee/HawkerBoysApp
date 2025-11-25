import pytest

pytest.importorskip("pydantic")

from core import gamification
from core.models import MissionTask, Trainee
from core.storage import InMemoryStorage


def test_compute_level_thresholds():
    assert gamification.compute_level(0) == 1
    assert gamification.compute_level(120) >= gamification.compute_level(80)


def test_award_task_xp_updates_tracks():
    trainee = Trainee(id="t1", name="Test", current_stage="Orientation")
    task = MissionTask(
        id="task-1",
        mission_id="m1",
        title="Demo",
        description="",
        track="kitchen",
        xp_reward=50,
        auto_complete=True,
    )
    updated = gamification.award_task_xp(trainee, task)
    assert updated.overall_xp == 50
    assert updated.kitchen_xp == 50


def test_badge_award_on_first_mission_completion():
    storage = InMemoryStorage()
    trainee = storage.get_trainee("trainee-1")
    assert trainee
    mission = next(iter(storage.missions.values()))
    task = storage.list_tasks_for_mission(mission.id)[0]
    gamification.complete_task_with_approval(storage, trainee, task, approver="admin")
    badges = storage.list_badges_for_trainee(trainee.id)
    assert badges
