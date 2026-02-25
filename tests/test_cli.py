"""Integration tests for Carron CLI gating and default mode behavior."""

from pathlib import Path

import pytest

from carron.cli import build_parser, dispatch


def test_invalid_python_target_writes_no_artifacts(tmp_path: Path) -> None:
    """Invalid Python input must abort before writing any artifacts (Failure Mode B)."""
    bad = tmp_path / "bad.py"
    bad.write_text("def oops(:\n  pass\n")

    out_dir = tmp_path / "out"

    parser = build_parser()
    args = parser.parse_args(["prop", f"{bad}:oops", "--output", str(out_dir)])

    with pytest.raises(SystemExit) as exc:
        dispatch(args)

    assert exc.value.code != 0
    assert not out_dir.exists() or not any(p.is_file() for p in out_dir.rglob("*"))


def test_default_emit_generates_artifacts(tmp_path: Path) -> None:
    """Default mode 'emit' should generate and write artifacts without running tests."""
    good = tmp_path / "good.py"
    good.write_text("def ok():\n    return 1\n")

    out_dir = tmp_path / "out"

    parser = build_parser()
    args = parser.parse_args(["prop", f"{good}:ok", "--output", str(out_dir)])

    dispatch(args)

    assert out_dir.exists()
    assert any(p.is_file() and p.suffix == ".py" for p in out_dir.rglob("*"))


def test_suggest_apply_invalid_target_writes_no_artifacts(tmp_path: Path) -> None:
    """suggest --apply must enforce gating and write no artifacts on invalid Python."""
    bad = tmp_path / "bad.py"
    bad.write_text("def oops(:\n  pass\n")

    out_dir = tmp_path / "out"

    parser = build_parser()
    args = parser.parse_args(["suggest", f"{bad}:oops", "--apply", "--output", str(out_dir)])

    with pytest.raises(SystemExit) as exc:
        dispatch(args)

    assert exc.value.code != 0
    assert not out_dir.exists() or not any(p.is_file() for p in out_dir.rglob("*"))


def test_suggest_apply_default_emit_generates(tmp_path: Path) -> None:
    good = tmp_path / "good.py"
    good.write_text("def ok():\n    return 1\n")

    out_dir = tmp_path / "out"

    parser = build_parser()
    args = parser.parse_args(["suggest", f"{good}:ok", "--apply", "--output", str(out_dir)])

    dispatch(args)

    assert out_dir.exists()
    assert any(p.is_file() and p.suffix == ".py" for p in out_dir.rglob("*"))
