from ..core.types import PlannerInput


class HeuristicPlanner:
    def plan(self, inp: PlannerInput) -> dict[str, str]:
        target = inp.target
        if ":" in target:
            return {"forge": "prop", "reason": "function-level target"}
        return {"forge": "diff", "reason": "module-level target"}
