from typing import List
from app.models.domain import DomainType, QuestionType, DomainRegistry

class DomainSelector:
    """Service to handle domain-specific logic."""
    
    @staticmethod
    def validate_domain(domain: str) -> DomainType:
        """Validate if the provided domain string is supported."""
        try:
            return DomainType(domain.lower())
        except ValueError:
            raise ValueError(f"Unsupported domain: {domain}. Supported domains are: {[d.value for d in DomainType]}")
            
    @staticmethod
    def get_supported_question_types(domain: DomainType) -> List[QuestionType]:
        """Get the supported question types for a given domain."""
        # Simple mapping for now, can be expanded based on DomainRegistry logic
        if domain == DomainType.CODING:
            return [QuestionType.CODING, QuestionType.MULTIPLE_CHOICE]
        return [QuestionType.MULTIPLE_CHOICE, QuestionType.FREE_TEXT, QuestionType.FILL_IN_BLANK]
