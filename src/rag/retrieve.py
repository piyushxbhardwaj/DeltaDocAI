import os
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from src.rag.base import BaseRetriever, BaseEmbedder, SearchDoc
from src.rag.embed import SentenceTransformerEmbedder
from src.observability.logger import logger

class ChromaDBRetriever(BaseRetriever):
    """Vector database indexing and similarity search using ChromaDB."""

    def __init__(self, persist_directory: str = "./data/chroma", embedder: Optional[BaseEmbedder] = None):
        self.persist_directory = persist_directory
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.client = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            logger.info(f"ChromaDB persistent client initialized at '{self.persist_directory}'.")
        except Exception as e:
            logger.warning(f"ChromaDB persistent client initialization failed ({e}). Using in-memory client fallback.")
            try:
                import chromadb
                self.client = chromadb.Client()
            except Exception as e2:
                logger.warning(f"ChromaDB in-memory fallback failed ({e2}). Vector search will use in-memory numpy store.")
                self.client = None
                self._in_mem_store: Dict[str, List[SearchDoc]] = {}

    async def index_documents(self, docs: List[Dict[str, Any]], collection_name: str = "delta_docs") -> bool:
        if not docs:
            return True

        formatted_ids = []
        formatted_texts = []
        formatted_metadatas = []

        for doc in docs:
            doc_id = doc.get("id", f"doc-{uuid.uuid4().hex[:8]}")
            text = doc.get("text", "")
            if not text:
                continue
            metadata = doc.get("metadata", {})
            
            formatted_ids.append(doc_id)
            formatted_texts.append(text)
            formatted_metadatas.append(metadata)

        embeddings = self.embedder.embed_texts(formatted_texts)

        if self.client:
            try:
                collection = self.client.get_or_create_collection(name=collection_name)
                # ChromaDB expects metadatas without nested dicts/lists
                clean_metadatas = []
                for m in formatted_metadatas:
                    clean_m = {}
                    for k, v in m.items():
                        if isinstance(v, (str, int, float, bool)):
                            clean_m[k] = v
                        else:
                            clean_m[k] = str(v)
                    clean_metadatas.append(clean_m)

                collection.upsert(
                    ids=formatted_ids,
                    documents=formatted_texts,
                    embeddings=embeddings,
                    metadatas=clean_metadatas
                )
                logger.info(f"Indexed {len(formatted_ids)} documents into ChromaDB collection '{collection_name}'.")
                return True
            except Exception as e:
                logger.error(f"ChromaDB indexing error: {e}")

        # Fallback in-memory numpy vector store
        if not hasattr(self, "_in_mem_store"):
            self._in_mem_store = {}
        
        search_docs = []
        for i in range(len(formatted_ids)):
            search_docs.append(SearchDoc(
                id=formatted_ids[i],
                text=formatted_texts[i],
                metadata=formatted_metadatas[i],
                score=1.0
            ))
        self._in_mem_store[collection_name] = search_docs
        return True

    async def search(self, query: str, collection_name: str = "delta_docs", top_k: int = 5) -> List[SearchDoc]:
        query_vec = self.embedder.embed_query(query)

        if self.client:
            try:
                collection = self.client.get_collection(name=collection_name)
                results = collection.query(
                    query_embeddings=[query_vec],
                    n_results=min(top_k, collection.count())
                )
                
                search_results = []
                if results and results.get("ids") and results["ids"][0]:
                    ids = results["ids"][0]
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
                    distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

                    for i in range(len(ids)):
                        search_results.append(SearchDoc(
                            id=ids[i],
                            text=docs[i],
                            metadata=metas[i],
                            score=round(1.0 / (1.0 + distances[i]), 3)
                        ))
                return search_results
            except Exception as e:
                logger.warning(f"ChromaDB query error or collection not found: {e}")

        # Fallback numpy cosine search
        if hasattr(self, "_in_mem_store") and collection_name in self._in_mem_store:
            store_docs = self._in_mem_store[collection_name]
            if not store_docs:
                return []
            
            doc_texts = [d.text for d in store_docs]
            doc_vecs = np.array(self.embedder.embed_texts(doc_texts))
            q_vec = np.array(query_vec)
            
            # Cosine similarity
            sims = np.dot(doc_vecs, q_vec) / (np.linalg.norm(doc_vecs, axis=1) * np.linalg.norm(q_vec) + 1e-9)
            top_indices = np.argsort(sims)[::-1][:top_k]
            
            res = []
            for idx in top_indices:
                d = store_docs[idx]
                d.score = float(round(sims[idx], 3))
                res.append(d)
            return res

        return []
