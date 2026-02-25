from dataclasses import dataclass

PLANNER_KEY_FORGE = "recommended_forge"
FORGE_PROP = "prop"
FORGE_DIFF = "diff"


@dataclass
class PlannerInput:
    """Input to the planner describing the requested target."""

    target: str


@dataclass
class GeneratedArtifact:
    """A single generated file to be written under the output directory."""

    relative_path: str
    content: str


@dataclass
class GenerationResult:
    """Result of a forge run containing artifacts and human readable diagnostics."""

    artifacts: list[GeneratedArtifact]
    diagnostics: list[str]


class GenerationContext:
    """Context passed to a forge describing the generation target.

    In v0.1, this context does not provide LLM access.
    """

    def __init__(self, target: str, *, target_info: object | None, resolved_target: object | None):
        self.target = target
        self.target_info = target_info
        self.resolved_target = resolved_target

    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt.

        Raises:
            RuntimeError: Always, because LLM integration is not implemented in v0.1.
        """

        raise RuntimeError("LLM integration not implemented in v0.1")
