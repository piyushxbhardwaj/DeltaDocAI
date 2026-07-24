import numpy as np
from typing import List
from src.rag.base import BaseEmbedder
from src.observability.logger import logger

class SentenceTransformerEmbedder(BaseEmbedder):
    """SentenceTransformers local vector embedding implementation."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"SentenceTransformer embedding model '{self.model_name}' loaded.")
        except Exception as e:
            logger.warning(f"Failed to load SentenceTransformer ({e}). Falling back to deterministic pseudo-embeddings.")
            self.model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        
        # Fallback deterministic pseudo-embeddings
        embeddings = []
        for text in texts:
            np.random.seed(abs(hash(text)) % (2**32))
            vec = np.random.randn(384)
            vec /= np.linalg.norm(vec)
            embeddings.append(vec.tolist())
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        res = self.embed_texts([query])
        return res[0] if res else [0.0] * 384
