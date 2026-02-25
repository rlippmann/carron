from carron.core.naming import generated_test_filename
from carron.core.types import FORGE_DIFF, FORGE_PROP, PLANNER_KEY_FORGE, PlannerInput
from carron.planner.heuristic import HeuristicPlanner


def test_naming() -> None:
    name = generated_test_filename("math:sqrt")
    assert name.startswith("test_")
    assert name.endswith(".py")


def test_planner_function_target() -> None:
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target="math:sqrt"))
    assert plan[PLANNER_KEY_FORGE] == FORGE_PROP


def test_planner_module_target() -> None:
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target="math"))
    assert plan[PLANNER_KEY_FORGE] == FORGE_DIFF
