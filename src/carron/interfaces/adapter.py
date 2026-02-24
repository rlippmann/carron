"""Language adapter interface and shared adapter exceptions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TargetRef:
    """Raw target reference string provided by the user."""

    raw: str


class AdapterError(Exception):
    """Base class for adapter-related errors."""


class TargetParseError(AdapterError):
    """Raised when a target string cannot be parsed."""


class TargetResolutionError(AdapterError):
    """Raised when a parsed target cannot be resolved."""


class InvalidSourceError(TargetResolutionError):
    """Raised when source code is invalid for the target language."""


class Adapter(ABC):
    """Abstract base class for language adapters.

    Adapters are responsible for parsing, validating, and summarizing
    targets for a specific programming language.

    All adapter operations must be synchronous and must not perform
    filesystem writes or subprocess execution.
    """

    @abstractmethod
    def get_target_summary(self, ref: TargetRef) -> object:
        """Return a best-effort summary of the given target.

        This method must not raise for recoverable resolution issues
        (e.g., module import failure) unless the source file is syntactically invalid.
        """

    @abstractmethod
    def validate_target(self, ref: TargetRef) -> object:
        """Strictly validate and resolve the given target.

        This method must raise if:
        - The target format is invalid.
        - The source file does not exist.
        - The source code is syntactically invalid.
        - The referenced symbol cannot be resolved.
        """
