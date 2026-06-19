import subprocess


def run_user_command(command: str) -> int:
    return subprocess.call(command, shell=True)
