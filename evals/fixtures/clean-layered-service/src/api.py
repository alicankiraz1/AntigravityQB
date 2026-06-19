from .service import renew_task_lease


def handle_renew(task_id: str) -> dict[str, str]:
    return {"status": renew_task_lease(task_id)}
