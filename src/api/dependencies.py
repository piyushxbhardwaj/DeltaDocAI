from typing import Generator
from src.rag.retrieve import ChromaDBRetriever
from src.rag.chat import GroundedChatEngine
from src.rag.llm import get_llm_provider
from src.pipeline.orchestrator import PipelineOrchestrator

# Global singletons for performance and memory reuse
_retriever = ChromaDBRetriever()
_orchestrator = PipelineOrchestrator(retriever=_retriever)
_chat_engine = GroundedChatEngine(llm=get_llm_provider(), retriever=_retriever)

def get_retriever() -> ChromaDBRetriever:
    return _retriever

def get_orchestrator() -> PipelineOrchestrator:
    return _orchestrator

def get_chat_engine() -> GroundedChatEngine:
    return _chat_engine
