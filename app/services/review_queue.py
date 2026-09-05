import logging
from typing import List
from app.schemas.responses import Variation

logger = logging.getLogger(__name__)

class ReviewQueueService:
    """Service to handle adding generated variations to a review queue."""
    
    def __init__(self, low_confidence_threshold: float = 0.6):
        self.low_confidence_threshold = low_confidence_threshold
        
    def build_queue(self, variations: List[Variation], borderline_indices: List[int]) -> List[Variation]:
        """
        Determine which variations need human review.
        """
        review_queue = []
        
        for idx, variation in enumerate(variations):
            needs_review = False
            
            if variation.confidence_score < self.low_confidence_threshold:
                needs_review = True
                
            if getattr(variation, 'flagged_for_review', False):
                needs_review = True
                
            if idx in borderline_indices:
                needs_review = True
                
            if needs_review:
                variation.flagged_for_review = True
                review_queue.append(variation)
                
        return review_queue
