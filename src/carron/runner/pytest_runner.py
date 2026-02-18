import subprocess
from pathlib import Path


def run_pytest(path: Path) -> None:
    subprocess.run(["pytest", str(path)], check=False)
