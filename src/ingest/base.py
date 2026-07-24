from abc import ABC, abstractmethod
from typing import Any, List, Union
from src.ingest.canonical import CanonicalObject

class BaseAdapter(ABC):
    """
    Abstract adapter for format-agnostic document ingestion.
    Supports Native PDF, Scanned PDF, DWG, and custom formats.
    """

    @abstractmethod
    async def load(self, source: Union[bytes, str]) -> Any:
        """Load source file data or path."""
        pass

    @abstractmethod
    async def extract(self, doc_data: Any) -> List[dict]:
        """Extract raw elements from loaded document data."""
        pass

    @abstractmethod
    async def normalize(self, raw_elements: List[dict]) -> List[CanonicalObject]:
        """Convert raw extracted elements into CanonicalObject representations."""
        pass

    async def process(self, source: Union[bytes, str]) -> List[CanonicalObject]:
        """Full execution pipeline: load -> extract -> normalize."""
        data = await self.load(source)
        raw = await self.extract(data)
        return await self.normalize(raw)
