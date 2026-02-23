def generated_test_filename(target: str) -> str:
    safe = target.replace(":", "_").replace(".", "_").replace("/", "_")
    return f"test_{safe}.py"
