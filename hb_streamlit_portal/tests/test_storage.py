import pytest

pytest.importorskip("pydantic")

from core.storage import InMemoryStorage
from core.models import Trainee, Mission


def test_storage_round_trip():
    storage = InMemoryStorage()
    trainee = Trainee(id="t2", name="Jamie", current_stage="Orientation")
    storage.save_trainee(trainee)
    assert storage.get_trainee("t2")

    mission = Mission(id="m-new", title="New mission", description="", stage="Orientation", total_xp_reward=50)
    storage.save_mission(mission)
    missions = storage.list_missions_for_trainee("t2")
    assert any(m.id == "m-new" for m in missions)


def test_support_request_persistence():
    storage = InMemoryStorage()
    from core.models import SupportRequest

    request = SupportRequest(id="r1", trainee_id="trainee-1", message="Need help", category="Training")
    storage.save_support_request(request)
    assert storage.list_support_requests()[0].id == "r1"
