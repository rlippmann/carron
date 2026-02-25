import subprocess
from pathlib import Path


def run_pytest(path: Path, collect_only: bool = False) -> None:
    """Run pytest against a generated test file.

    Args:
        path: Path to the generated test file.
        collect_only: If True, run pytest in collection mode without executing tests.
    """
    cmd = ["pytest"]

    if collect_only:
        cmd.append("--collect-only")

    cmd.append(str(path))

    result = subprocess.run(cmd, check=False)

    if result.returncode != 0:
        raise SystemExit(result.returncode)
