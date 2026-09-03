from abc import ABC, abstractmethod
from .types import ParsedSave


class BaseSaveParser(ABC):
    @abstractmethod
    def parse(self, data: bytes) -> ParsedSave:
        """Parse raw save file bytes into a ParsedSave."""
        ...

    @abstractmethod
    def can_parse(self, data: bytes) -> bool:
        """Return True if this parser can handle the given save data."""
        ...
