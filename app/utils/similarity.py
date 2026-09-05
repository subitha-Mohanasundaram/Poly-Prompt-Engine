import numpy as np
from typing import Tuple, Set

try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    def cosine_similarity(X, Y=None):
        if Y is None:
            Y = X
        X_norm = np.linalg.norm(X, axis=1, keepdims=True)
        Y_norm = np.linalg.norm(Y, axis=1, keepdims=True)
        X_normalized = np.divide(X, X_norm, out=np.zeros_like(X), where=X_norm!=0)
        Y_normalized = np.divide(Y, Y_norm, out=np.zeros_like(Y), where=Y_norm!=0)
        return np.dot(X_normalized, Y_normalized.T)

def compute_cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Compute the cosine similarity matrix for a set of embeddings."""
    if len(embeddings) == 0:
        return np.array([])
    return cosine_similarity(embeddings)

def find_duplicates(similarity_matrix: np.ndarray, threshold: float = 0.85) -> Tuple[Set[int], float]:
    """
    Find duplicate indices in a similarity matrix based on a threshold.
    Returns a tuple of (duplicate_indices, duplicate_rate).
    """
    n = similarity_matrix.shape[0]
    if n <= 1:
        return set(), 0.0

    duplicates = set()
    for i in range(n):
        for j in range(i + 1, n):
            if similarity_matrix[i, j] > threshold:
                duplicates.add(j)
                
    duplicate_rate = len(duplicates) / n if n > 0 else 0.0
    return duplicates, duplicate_rate

def find_near_seed_duplicates(seed_embedding: np.ndarray, variation_embeddings: np.ndarray, threshold: float = 0.95) -> Set[int]:
    """
    Find variation indices that are too similar to the seed embedding.
    """
    if len(variation_embeddings) == 0:
        return set()
        
    if seed_embedding.ndim == 1:
        seed_embedding = seed_embedding.reshape(1, -1)
        
    sims = cosine_similarity(seed_embedding, variation_embeddings)[0]
    
    duplicates = {i for i, sim in enumerate(sims) if sim > threshold}
    return duplicates
