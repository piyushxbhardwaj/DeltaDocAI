"""
RAG and Grounded Chat module for DeltaDoc AI.
"""
from src.rag.base import BaseLLM, BaseEmbedder, BaseRetriever
from src.rag.embed import SentenceTransformerEmbedder
from src.rag.llm import GeminiProvider, OpenAIProvider, get_llm_provider
from src.rag.retrieve import ChromaDBRetriever
from src.rag.chat import GroundedChatEngine

__all__ = [
    "BaseLLM",
    "BaseEmbedder",
    "BaseRetriever",
    "SentenceTransformerEmbedder",
    "GeminiProvider",
    "OpenAIProvider",
    "get_llm_provider",
    "ChromaDBRetriever",
    "GroundedChatEngine",
]
