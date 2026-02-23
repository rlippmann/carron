from carron.core.naming import generated_test_filename
from carron.core.types import GeneratedArtifact, GenerationContext, GenerationResult
from carron.interfaces.forge import Forge


class PropForge(Forge):
    """Generate property-style tests based on a target identifier.

    This implementation produces placeholder property tests without
    external analysis or LLM integration.
    """

    def generate(self, ctx: GenerationContext) -> GenerationResult:
        """Create property-style test artifacts for the given context.

        Returns a single test file containing a placeholder assertion.
        """
        filename = generated_test_filename(ctx.target)
        content = "def test_placeholder():\n    assert True\n"
        artifact = GeneratedArtifact(relative_path=filename, content=content)
        return GenerationResult(artifacts=[artifact], diagnostics=[])
