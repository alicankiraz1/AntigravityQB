def save_lease(task_id: str) -> None:
    if not task_id:
        raise ValueError("task_id required")
