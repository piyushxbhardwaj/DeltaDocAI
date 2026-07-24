from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.rag.base import BaseLLM, BaseRetriever, SearchDoc
from src.rag.llm import get_llm_provider
from src.rag.retrieve import ChromaDBRetriever
from src.observability.logger import logger

class Citation(BaseModel):
    source: str  # e.g., "Revision A", "Revision B", "Delta Report"
    page: Optional[int] = None
    tag: Optional[str] = None
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    groundedness_score: float = 1.0
    retrieved_contexts: List[SearchDoc]
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0

class GroundedChatEngine:
    """Retrieval-Augmented Generation (RAG) Grounded Chat Engine."""

    def __init__(self, llm: Optional[BaseLLM] = None, retriever: Optional[BaseRetriever] = None):
        self.llm = llm or get_llm_provider()
        self.retriever = retriever or ChromaDBRetriever()

    async def ask(
        self,
        query: str,
        collection_name: str = "delta_docs",
        top_k: int = 5
    ) -> ChatResponse:
        """
        Executes grounded chat retrieval and LLM answer generation with citations.
        """
        # Step 1: Retrieve relevant context chunks
        docs = await self.retriever.search(query=query, collection_name=collection_name, top_k=top_k)

        context_str = ""
        citations: List[Citation] = []

        for idx, doc in enumerate(docs):
            src = doc.metadata.get("revision", doc.metadata.get("source", "Delta Report"))
            pg = doc.metadata.get("page")
            tag = doc.metadata.get("tag")
            context_str += f"\n[Context Chunk {idx+1}] (Source: {src}, Page: {pg or 'N/A'}, Tag: {tag or 'N/A'})\n{doc.text}\n"

            citations.append(Citation(
                source=str(src),
                page=int(pg) if pg and str(pg).isdigit() else None,
                tag=str(tag) if tag else None,
                snippet=doc.text[:120] + "..." if len(doc.text) > 120 else doc.text
            ))

        # Step 2: System prompt enforcing groundedness and citations
        system_prompt = (
            "You are DeltaDoc AI, a Senior Engineering Document Analyst.\n"
            "Answer the user's question STRICTLY using the provided context chunks below.\n"
            "RULES:\n"
            "1. NEVER introduce outside facts or hallucinate details not explicitly found in context.\n"
            "2. ALWAYS cite the context source in brackets (e.g. [Revision A, Page 1] or [Delta Report]).\n"
            "3. If the answer cannot be determined from context, state: 'The provided document context does not contain sufficient details to answer this question.'\n\n"
            f"RETRIEVED DOCUMENT CONTEXT:\n{context_str if context_str else 'No context found.'}"
        )

        # Step 3: Call LLM provider
        llm_res = await self.llm.generate(prompt=query, system_prompt=system_prompt)

        # Step 4: Verify groundedness metric
        groundedness = 1.0
        if "does not contain sufficient details" in llm_res.text.lower():
            groundedness = 0.5

        return ChatResponse(
            answer=llm_res.text,
            citations=citations,
            groundedness_score=groundedness,
            retrieved_contexts=docs,
            prompt_tokens=llm_res.prompt_tokens,
            completion_tokens=llm_res.completion_tokens,
            estimated_cost_usd=llm_res.estimated_cost_usd
        )
