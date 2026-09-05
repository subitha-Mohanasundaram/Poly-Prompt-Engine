"""
Domain models for the Poly Prompt Engine.
"""
from enum import StrEnum
from dataclasses import dataclass
from typing import List, Dict, Optional

class DomainType(StrEnum):
    mathematics = "mathematics"
    programming = "programming"
    science = "science"
    business = "business"
    language = "language"

class QuestionType(StrEnum):
    mcq = "mcq"
    fill_in_the_blank = "fill_in_the_blank"
    coding = "coding"
    descriptive = "descriptive"

class DifficultyLevel(StrEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

@dataclass
class DomainConfig:
    name: str
    label: str
    description: str
    supported_question_types: List[QuestionType]
    example_topics: Dict[str, List[str]]

class DomainRegistry:
    _domains: Dict[str, DomainConfig] = {
        DomainType.mathematics: DomainConfig(
            name=DomainType.mathematics,
            label="Mathematics",
            description="Mathematics and quantitative reasoning.",
            supported_question_types=[QuestionType.mcq, QuestionType.fill_in_the_blank, QuestionType.descriptive],
            example_topics={
                "Algebra": ["equations", "inequalities", "polynomials"],
                "Calculus": ["derivatives", "integrals", "limits"],
                "Geometry": ["triangles", "circles", "areas"],
                "Statistics": ["probability", "distributions", "hypothesis testing"]
            }
        ),
        DomainType.programming: DomainConfig(
            name=DomainType.programming,
            label="Programming",
            description="Computer programming and computer science concepts.",
            supported_question_types=[QuestionType.mcq, QuestionType.fill_in_the_blank, QuestionType.descriptive, QuestionType.coding],
            example_topics={
                "Data Structures": ["arrays", "linked lists", "trees", "graphs"],
                "Algorithms": ["sorting", "searching", "dynamic programming"],
                "OOP": ["classes", "inheritance", "polymorphism"],
                "Databases": ["SQL queries", "normalization", "joins"]
            }
        ),
        DomainType.science: DomainConfig(
            name=DomainType.science,
            label="Science",
            description="Natural sciences including physics, chemistry, and biology.",
            supported_question_types=[QuestionType.mcq, QuestionType.fill_in_the_blank, QuestionType.descriptive],
            example_topics={
                "Physics": ["mechanics", "thermodynamics", "electromagnetism"],
                "Chemistry": ["organic", "inorganic", "physical"],
                "Biology": ["genetics", "ecology", "cell biology"]
            }
        ),
        DomainType.business: DomainConfig(
            name=DomainType.business,
            label="Business",
            description="Business, finance, and management concepts.",
            supported_question_types=[QuestionType.mcq, QuestionType.fill_in_the_blank, QuestionType.descriptive],
            example_topics={
                "Finance": ["accounting", "investment", "valuation"],
                "Marketing": ["segmentation", "pricing", "branding"],
                "Management": ["strategy", "operations", "HR"]
            }
        ),
        DomainType.language: DomainConfig(
            name=DomainType.language,
            label="Language",
            description="Language grammar, vocabulary, and comprehension.",
            supported_question_types=[QuestionType.mcq, QuestionType.fill_in_the_blank, QuestionType.descriptive],
            example_topics={
                "Grammar": ["tenses", "voice", "articles"],
                "Vocabulary": ["synonyms", "antonyms", "idioms"],
                "Comprehension": ["inference", "summary", "analysis"]
            }
        )
    }

    @classmethod
    def get_domain(cls, name: str) -> Optional[DomainType]:
        try:
            return DomainType(name)
        except ValueError:
            return None

    @classmethod
    def list_domains(cls) -> List[DomainType]:
        return list(cls._domains.keys())

    @classmethod
    def get_domain_config(cls, name: str) -> Optional[DomainConfig]:
        return cls._domains.get(name)
