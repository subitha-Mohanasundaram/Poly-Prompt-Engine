import logging
from typing import List
from app.schemas.responses import Variation

logger = logging.getLogger(__name__)

class ReviewQueueService:
    """Service to handle routing generated variations to a review queue for PS8 + PS2."""
    
    def __init__(self, low_confidence_threshold: float = 0.6, reliability_threshold: float = 0.85):
        self.low_confidence_threshold = low_confidence_threshold
        self.reliability_threshold = reliability_threshold
        
    def build_queue(self, variations: List[Variation], borderline_indices: List[int]) -> List[Variation]:
        """
        Determine which variations need human review based on PS8 confidence/difficulty/duplicates
        and PS2 hallucination_flag & reliability_score.
        """
        review_queue = []
        
        for idx, variation in enumerate(variations):
            needs_review = False
            
            # PS8 checks
            if variation.confidence_score < self.low_confidence_threshold:
                needs_review = True
                
            if getattr(variation, 'flagged_for_review', False):
                needs_review = True
                
            if idx in borderline_indices:
                needs_review = True

            # PS2 Reliability & Hallucination checks
            if getattr(variation, 'hallucination_flag', False):
                needs_review = True

            if getattr(variation, 'reliability_score', 1.0) < self.reliability_threshold:
                needs_review = True
                
            if needs_review:
                variation.flagged_for_review = True
                review_queue.append(variation)
                
        return review_queue
