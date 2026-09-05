import logging
from typing import List, Tuple

from app.utils.embeddings import EmbeddingService
from app.utils.similarity import (
    compute_cosine_similarity_matrix,
    find_duplicates,
    find_near_seed_duplicates,
    cosine_similarity
)

logger = logging.getLogger(__name__)

class DuplicateDetector:
    """Service to detect duplicate and near-duplicate generated variations."""

    def __init__(self, embedding_service: EmbeddingService, threshold: float = 0.85):
        self.embedding_service = embedding_service
        self.threshold = threshold

    def detect(self, seed_question: str, variations: List[str]) -> Tuple[List[int], float]:
        """
        Detect duplicates among variations and near-duplicates to the seed question.
        Returns sorted list of duplicate indices and duplicate rate among variations.
        """
        if not variations:
            return [], 0.0

        all_texts = [seed_question] + variations
        embeddings = self.embedding_service.encode(all_texts)

        seed_embedding = embeddings[0:1]
        variation_embeddings = embeddings[1:]

        # Similarity among variations
        var_sim_matrix = compute_cosine_similarity_matrix(variation_embeddings)
        var_duplicates, var_dup_rate = find_duplicates(var_sim_matrix, self.threshold)

        # Similarity to seed
        seed_duplicates = find_near_seed_duplicates(seed_embedding, variation_embeddings, threshold=0.95)

        all_duplicates = var_duplicates.union(seed_duplicates)
        
        return sorted(list(all_duplicates)), var_dup_rate

    def get_borderline_indices(self, seed_question: str, variations: List[str], lower: float = 0.80, upper: float = 0.85) -> List[int]:
        """
        Find variations in the 'borderline' similarity range with each other or the seed.
        """
        if not variations:
            return []

        all_texts = [seed_question] + variations
        embeddings = self.embedding_service.encode(all_texts)

        seed_embedding = embeddings[0:1]
        variation_embeddings = embeddings[1:]
        
        borderline = set()
        
        # Check variations vs variations
        var_sim_matrix = compute_cosine_similarity_matrix(variation_embeddings)
        n = var_sim_matrix.shape[0]
        for i in range(n):
            for j in range(i + 1, n):
                sim = var_sim_matrix[i, j]
                if lower <= sim <= upper:
                    borderline.add(i)
                    borderline.add(j)
                    
        # Check seed vs variations
        sims_to_seed = cosine_similarity(seed_embedding, variation_embeddings)[0]
        for i, sim in enumerate(sims_to_seed):
            if lower <= sim <= upper:
                borderline.add(i)
                
        return sorted(list(borderline))
