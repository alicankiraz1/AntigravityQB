from db import write_job


def run(job_id: str) -> None:
    write_job(job_id)
