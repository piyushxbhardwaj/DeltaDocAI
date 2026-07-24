from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model: str = "gemini-2.5-flash"

class BaseLLM(ABC):
    """Abstract interface for LLM operations."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        pass

class BaseEmbedder(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        pass

class SearchDoc(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float = 0.0

class BaseRetriever(ABC):
    """Abstract interface for document vector indexing and retrieval."""

    @abstractmethod
    async def index_documents(self, docs: List[Dict[str, Any]], collection_name: str) -> bool:
        pass

    @abstractmethod
    async def search(self, query: str, collection_name: str, top_k: int = 5) -> List[SearchDoc]:
        pass
