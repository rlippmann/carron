import argparse
import json
from pathlib import Path

from carron.adapters.python.adapter import PythonRuntimeAdapter
from carron.core.types import (
    FORGE_DIFF,
    FORGE_PROP,
    PLANNER_KEY_FORGE,
    GenerationContext,
    PlannerInput,
)
from carron.core.workflow import write_artifacts
from carron.forges.diff.forge import DiffForge
from carron.forges.prop.forge import PropForge
from carron.interfaces.adapter import AdapterError, TargetRef
from carron.interfaces.forge import Forge
from carron.planner.heuristic import HeuristicPlanner
from carron.runner.pytest_runner import run_pytest

_COMMAND_SUGGEST = "suggest"
_COMMAND_TEST = "test"

_MODE_CHOICES = ("emit", "check", "run")
_MODE_EMIT, _MODE_CHECK, _MODE_RUN = _MODE_CHOICES
_DEFAULT_MODE = _MODE_EMIT

_DEFAULT_OUTPUT_DIR = "tests/generated"


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the Carron command-line argument parser."""
    parser = argparse.ArgumentParser(prog="carron")
    sub = parser.add_subparsers(dest="command", required=True)

    suggest = sub.add_parser(_COMMAND_SUGGEST)
    suggest.add_argument("target")
    suggest.add_argument("--apply", action="store_true")
    suggest.add_argument("--mode", choices=_MODE_CHOICES, default=_DEFAULT_MODE)
    suggest.add_argument("--output", default=_DEFAULT_OUTPUT_DIR)

    def add_forge_command(name: str) -> None:
        cmd = sub.add_parser(name)
        cmd.add_argument("target")
        cmd.add_argument("--mode", choices=_MODE_CHOICES, default=_DEFAULT_MODE)
        cmd.add_argument("--output", default=_DEFAULT_OUTPUT_DIR)

    for name in (_COMMAND_TEST, FORGE_PROP, FORGE_DIFF):
        add_forge_command(name)

    return parser


def dispatch(args: argparse.Namespace) -> None:
    """Dispatch parsed CLI arguments to the appropriate handler."""
    if args.command == _COMMAND_SUGGEST:
        handle_suggest(args)
    elif args.command == _COMMAND_TEST:
        handle_test(args)
    elif args.command == FORGE_PROP:
        handle_prop(args)
    elif args.command == FORGE_DIFF:
        handle_diff(args)
    else:
        raise SystemExit(1)


def handle_suggest(args: argparse.Namespace) -> None:
    """Print a planner decision for the given target or apply it."""
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target=args.target))

    if not args.apply:
        print(json.dumps(plan, indent=2))
        return

    try:
        forge_name = plan[PLANNER_KEY_FORGE]
    except KeyError as exc:
        print("Planner returned invalid decision structure")
        raise SystemExit(1) from exc

    forge = _select_forge(forge_name)
    _execute_forge(forge, args.target, args.output, args.mode)


def handle_test(args: argparse.Namespace) -> None:
    """Plan and generate tests for the given target.

    Selects a forge via the planner and executes it according to the
    requested mode.
    """
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target=args.target))
    forge = _select_forge(plan[PLANNER_KEY_FORGE])
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
    if name == FORGE_PROP:
        return PropForge()
    if name == FORGE_DIFF:
        return DiffForge()
    raise ValueError(f"Unknown forge: {name}")


def _execute_forge(forge: Forge, target: str, output: str, mode: str) -> None:
    """Generate tests via a forge after validating the target."""
    adapter = PythonRuntimeAdapter()
    ref = TargetRef(raw=target)

    try:
        resolved = adapter.validate_target(ref)
        info = adapter.get_target_summary(ref)
    except AdapterError as exc:
        print(exc)
        raise SystemExit(1) from exc

    ctx = GenerationContext(
        target=target,
        target_info=info,
        resolved_target=resolved,
    )

    result = forge.generate(ctx)
    out_dir = Path(output)
    paths = write_artifacts(result.artifacts, out_dir)

    if mode == _MODE_EMIT:
        return
    collect_only = mode == _MODE_CHECK
    if mode in {_MODE_CHECK, _MODE_RUN}:
        for p in paths:
            run_pytest(p, collect_only=collect_only)
        return

    raise SystemExit(1)
