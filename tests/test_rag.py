import pytest
from src.rag.embed import SentenceTransformerEmbedder
from src.rag.retrieve import ChromaDBRetriever
from src.rag.chat import GroundedChatEngine

def test_sentence_transformer_embedder():
    embedder = SentenceTransformerEmbedder()
    vecs = embedder.embed_texts(["26-PIT-9055 Pressure Transmitter", "Valve V-102"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 384

@pytest.mark.asyncio
async def test_chroma_retriever_and_chat():
    retriever = ChromaDBRetriever(persist_directory="./data/test_chroma")
    docs = [
        {"id": "d1", "text": "Valve V-102 was removed from Revision B.", "metadata": {"revision": "Delta Report", "page": 1}}
    ]
    await retriever.index_documents(docs, collection_name="test_col")

    chat = GroundedChatEngine(retriever=retriever)
    res = await chat.ask(query="Which valve was removed?", collection_name="test_col")

    assert res.answer is not None
    assert len(res.citations) > 0
    assert res.groundedness_score > 0.0
