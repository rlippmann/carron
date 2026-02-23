def generated_test_filename(target: str) -> str:
    """Return the generated test filename."""
    safe = target.replace(":", "_").replace(".", "_").replace("/", "_")
    return f"test_{safe}.py"
