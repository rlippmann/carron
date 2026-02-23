from dataclasses import dataclass


@dataclass
class PlannerInput:
    target: str


@dataclass
class GeneratedArtifact:
    relative_path: str
    content: str


@dataclass
class GenerationResult:
    artifacts: list[GeneratedArtifact]
    diagnostics: list[str]


class GenerationContext:
    def __init__(self, target: str):
        self.target = target

    def generate_text(self, prompt: str) -> str:
        raise RuntimeError("LLM integration not implemented in v0.1")
