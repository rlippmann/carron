import argparse
import ast
import json
from pathlib import Path
from typing import Any

from carron.core.types import GenerationContext, PlannerInput
from carron.core.workflow import write_artifacts
from carron.forges.diff.forge import DiffForge
from carron.forges.prop.forge import PropForge
from carron.interfaces.forge import Forge
from carron.planner.heuristic import HeuristicPlanner
from carron.runner.pytest_runner import run_pytest


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the Carron command-line argument parser."""
    parser = argparse.ArgumentParser(prog="carron")
    sub = parser.add_subparsers(dest="command", required=True)

    suggest = sub.add_parser("suggest")
    suggest.add_argument("target")
    suggest.add_argument("--mode", choices=["check", "run"], default="check")

    test = sub.add_parser("test")
    test.add_argument("target")
    test.add_argument("--mode", choices=["check", "run"], default="check")
    test.add_argument("--output", default="tests/generated")

    prop = sub.add_parser("prop")
    prop.add_argument("target")
    prop.add_argument("--mode", choices=["check", "run"], default="check")
    prop.add_argument("--output", default="tests/generated")

    diff = sub.add_parser("diff")
    diff.add_argument("target")
    diff.add_argument("--mode", choices=["check", "run"], default="check")
    diff.add_argument("--output", default="tests/generated")

    return parser


def dispatch(args: argparse.Namespace) -> None:
    """Dispatch parsed CLI arguments to the appropriate handler."""
    if args.command == "suggest":
        handle_suggest(args)
    elif args.command == "test":
        handle_test(args)
    elif args.command == "prop":
        handle_prop(args)
    elif args.command == "diff":
        handle_diff(args)
    else:
        raise SystemExit(1)


def handle_suggest(args: argparse.Namespace) -> None:
    """Print a planner decision for the given target without execution."""
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target=args.target))
    print(json.dumps(plan, indent=2))


def handle_test(args: argparse.Namespace) -> None:
    """Plan and generate tests for the given target.

    Selects a forge via the planner and executes it according to the
    requested mode.
    """
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target=args.target))
    forge = _select_forge(plan["forge"])
    _execute_forge(forge, args.target, args.output, args.mode)


def handle_prop(args: argparse.Namespace) -> None:
    """Generate property-style tests directly using the prop forge."""
    forge = PropForge()
    _execute_forge(forge, args.target, args.output, args.mode)


def handle_diff(args: argparse.Namespace) -> None:
    """Generate diff-style tests directly using the diff forge."""
    forge = DiffForge()
    _execute_forge(forge, args.target, args.output, args.mode)


def _select_forge(name: str) -> Forge:
    if name == "prop":
        return PropForge()
    if name == "diff":
        return DiffForge()
    raise ValueError(f"Unknown forge: {name}")


def _execute_forge(forge: Any, target: str, output: str, mode: str) -> None:
    ctx = GenerationContext(target=target)
    result = forge.generate(ctx)
    out_dir = Path(output)
    paths = write_artifacts(result.artifacts, out_dir)

    for p in paths:
        if mode == "check":
            _check_file(p)
        elif mode == "run":
            run_pytest(p)


def _check_file(path: Path) -> None:
    source = path.read_text()
    ast.parse(source)
