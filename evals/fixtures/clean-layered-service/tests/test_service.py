from src.service import renew_task_lease


def test_renew_task_lease_returns_status():
    assert renew_task_lease("task-1") == "renewed"
