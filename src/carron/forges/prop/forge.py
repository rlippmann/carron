from ...core.naming import test_filename_for_target
from ...core.types import GeneratedArtifact, GenerationContext, GenerationResult
from ...interfaces.forge import Forge


class PropForge(Forge):
    def generate(self, ctx: GenerationContext) -> GenerationResult:
        filename = test_filename_for_target(ctx.target)
        content = "def test_placeholder():\n    assert True\n"
        artifact = GeneratedArtifact(relative_path=filename, content=content)
        return GenerationResult(artifacts=[artifact], diagnostics=[])
