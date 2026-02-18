def test_filename_for_target(target: str) -> str:
    safe = target.replace(":", "_").replace(".", "_").replace("/", "_")
    return f"test_{safe}.py"
