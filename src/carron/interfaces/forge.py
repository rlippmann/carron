from abc import ABC, abstractmethod

from carron.core.types import GenerationContext, GenerationResult


class Forge(ABC):
    @abstractmethod
    def generate(self, ctx: GenerationContext) -> GenerationResult: ...
