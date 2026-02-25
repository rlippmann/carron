from carron.core.types import FORGE_DIFF, FORGE_PROP, PLANNER_KEY_FORGE, PlannerInput


class HeuristicPlanner:
    """Select a forge implementation using simple structural heuristics.

    This planner does not perform static analysis or LLM calls. It
    chooses a forge based solely on the shape of the target string and
    is intended as the baseline planner for v0.1.
    """

    def plan(self, inp: PlannerInput) -> dict[str, str]:
        """Return a forge selection decision for the given target.

        The decision is deterministic and based only on the target string.
        No filesystem access, execution, or external calls are performed.

        Args:
            inp: The planner input describing the target to analyze.

        Returns:
            A dictionary describing the selected forge and reasoning.
        """
        target = inp.target
        if ":" in target:
            return {PLANNER_KEY_FORGE: FORGE_PROP, "reason": "function-level target"}
        return {PLANNER_KEY_FORGE: FORGE_DIFF, "reason": "module-level target"}
