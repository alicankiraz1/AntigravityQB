from .repository import save_lease


def renew_task_lease(task_id: str) -> str:
    save_lease(task_id)
    return "renewed"
