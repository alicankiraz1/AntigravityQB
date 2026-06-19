def write_job(job_id: str) -> None:
    if not job_id:
        raise ValueError("job_id required")
