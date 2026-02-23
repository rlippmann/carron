from abc import ABC, abstractmethod

from carron.core.types import GenerationContext, GenerationResult


class Forge(ABC):
    """Abstract base class for all forge implementations.

    A forge is responsible for generating test artifacts from a
    GenerationContext. Implementations must be pure generators and
    must not perform side effects such as writing files or executing
    subprocesses."""

    @abstractmethod
    def generate(self, ctx: GenerationContext) -> GenerationResult:
        """Produce test artifacts for the given generation context.

        Implementations must return all generated content inside the
        GenerationResult and must not perform filesystem writes,
        subprocess execution, or other side effects.

        Args:
            ctx: The generation context describing the target.

        Returns:
            A GenerationResult containing artifacts and diagnostics.
        """
        ...
