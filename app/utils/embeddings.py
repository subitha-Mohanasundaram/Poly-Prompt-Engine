import logging
import time
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self._model = None
        self._is_available = self.is_available()

    def is_available(self) -> bool:
        """Check if sentence-transformers is installed."""
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False

    def _ensure_loaded(self):
        """Lazy load the sentence-transformers model."""
        if self._model is not None or not self._is_available:
            return
            
        try:
            import sentence_transformers
            start_time = time.time()
            logger.info(f"Loading embedding model {self.model_name}...")
            self._model = sentence_transformers.SentenceTransformer(self.model_name)
            load_time = time.time() - start_time
            logger.info(f"Embedding model loaded in {load_time:.2f} seconds.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self._is_available = False

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode a list of texts into embeddings."""
        if not texts:
            return np.empty((0, 384))
            
        self._ensure_loaded()
        
        if not self._is_available or self._model is None:
            logger.warning("sentence-transformers not available or model failed to load. Returning random vectors.")
            # Mock random embeddings of dimension 384
            return np.random.rand(len(texts), 384).astype(np.float32)
            
        return self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
