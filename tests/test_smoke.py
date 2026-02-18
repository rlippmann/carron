from carron.core.naming import test_filename_for_target
from carron.planner.heuristic import HeuristicPlanner
from carron.core.types import PlannerInput


def test_naming():
    name = test_filename_for_target("math:sqrt")
    assert name.startswith("test_")
    assert name.endswith(".py")


def test_planner_function_target():
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target="math:sqrt"))
    assert plan["forge"] == "prop"


def test_planner_module_target():
    planner = HeuristicPlanner()
    plan = planner.plan(PlannerInput(target="math"))
    assert plan["forge"] == "diff"
