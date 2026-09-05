from typing import List, Dict, Any
from app.schemas.llm_schemas import LLMSeedAnalysis

class PromptBuilder:
    """Builds prompt templates for LLM interactions."""
    
    @staticmethod
    def build_seed_analysis_prompt(seed_question: str, domain: str) -> str:
        """Prompt to analyze the seed question."""
        return f"""
        Analyze the following {domain} seed question.
        
        Seed Question:
        {seed_question}
        
        Extract the following information:
        1. detected_topic: The main topic
        2. detected_subtopic: The specific subtopic
        3. detected_difficulty: The difficulty level (e.g., easy, medium, hard)
        4. detected_question_type: The type of question (e.g., mcq, coding, fill_in_the_blank, descriptive)
        5. key_concepts: List of key concepts tested
        6. numerical_values: Any numerical values or constraints present
        7. context_description: A brief description of the context or scenario
        
        Provide the output matching the requested JSON schema exactly.
        """

    @staticmethod
    def build_variation_prompt(
        seed_question: str, 
        domain: str, 
        analysis: LLMSeedAnalysis, 
        batch_size: int, 
        batch_index: int
    ) -> str:
        """Prompt to generate variations of the seed question."""
        key_concepts_str = ", ".join(analysis.key_concepts) if analysis.key_concepts else "general"
        return f"""
        Generate {batch_size} distinct variations of the following {domain} seed question.
        
        Seed Question: {seed_question}
        Topic: {analysis.detected_topic} ({analysis.detected_subtopic})
        Key Concepts: {key_concepts_str}
        Context: {analysis.context_description}
        Target Difficulty: Equivalent to the seed question ({analysis.detected_difficulty}).
        
        CRITICAL RULES:
        1. Each variation MUST test the same core concept but with DIFFERENT scenarios, numbers, contexts, or methodologies.
        2. Difficulty must remain equivalent to the seed.
        3. Question type must match: {analysis.detected_question_type}.
        4. Each variation must include a complete, accurate answer key.
        5. For MCQs: provide options and correct answer clearly in the answer_key.
        6. For coding: provide working solution code in answer_key.
        7. For fill-in-the-blank: clearly mark the blank and provide the exact answer.
        8. This is batch #{batch_index}. Ensure these variations are highly distinct from typical generic examples.
        
        Make sure all output strictly follows the required JSON schema.
        """

    @staticmethod
    def build_difficulty_scoring_prompt(seed_difficulty: str, variations: List[Dict[str, Any]]) -> str:
        """Prompt to score variation difficulty compared to the seed."""
        return f"""
        You are an expert curriculum designer.
        The seed question had a target difficulty of: {seed_difficulty}.
        
        Review the following variations and score their difficulty on a 1-5 scale (where 1=trivial, 3=medium, 5=very hard).
        
        Variations:
        {variations}
        
        Return a JSON response with scores array mapping each variation_index to its score and level.
        """

    @staticmethod
    def build_answer_verification_prompt(question: str, answer: str, domain: str) -> str:
        """Prompt to verify an answer for a question."""
        return f"""
        You are a subject matter expert in {domain}.
        
        Review the following question and proposed answer.
        
        Question:
        {question}
        
        Proposed Answer:
        {answer}
        
        Is the proposed answer completely correct and accurate for the given question?
        Return a confidence score between 0.0 and 1.0, where 1.0 is perfectly correct.
        """
