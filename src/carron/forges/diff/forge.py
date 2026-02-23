from ...core.naming import generated_test_filename
from ...core.types import GeneratedArtifact, GenerationContext, GenerationResult
from ...interfaces.forge import Forge


class DiffForge(Forge):
    def generate(self, ctx: GenerationContext) -> GenerationResult:
        filename = generated_test_filename(ctx.target)
        content = "def test_diff_placeholder():\n    assert True\n"
        artifact = GeneratedArtifact(relative_path=filename, content=content)
        return GenerationResult(artifacts=[artifact], diagnostics=[])
