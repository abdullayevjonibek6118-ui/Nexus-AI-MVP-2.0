"""
AI Training Service

Manages training data for AI screening enhancement using scraped resumes.
Builds few-shot learning prompts from training examples.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class TrainingExample(BaseModel):
    """Training example for AI screening."""
    resume_text: str
    vacancy_description: str
    ideal_questions: List[str]
    score: Optional[float] = None
    skills_match: Optional[List[str]] = None
    

class TrainingDataManager:
    """Manages AI training data and prompt enhancement."""
    
    def __init__(self):
        self._examples: List[TrainingExample] = []
    
    def add_example(self, example: TrainingExample):
        """Add a training example."""
        self._examples.append(example)
    
    def get_examples(self, limit: int = 5) -> List[TrainingExample]:
        """Get recent training examples."""
        return self._examples[:limit]
    
    def build_few_shot_prompt(self, examples: Optional[List[TrainingExample]] = None) -> str:
        """
        Build enhanced system prompt with few-shot examples.
        
        Args:
            examples: Training examples to include. If None, uses stored examples.
            
        Returns:
            Enhanced system prompt string
        """
        if examples is None:
            examples = self.get_examples(limit=3)
        
        if not examples:
            return """You are an expert HR AI assistant specializing in candidate screening and resume analysis. 
Your role is to objectively evaluate candidates against job requirements and provide actionable insights."""
        
        base_prompt = """You are an expert HR AI assistant specializing in candidate screening and resume analysis. 
Your role is to objectively evaluate candidates against job requirements and provide actionable insights.

Here are some examples of high-quality screening analyses:
"""
        
        for i, example in enumerate(examples, 1):
            base_prompt += f"\n\nExample {i}:"
            base_prompt += f"\nVacancy: {example.vacancy_description[:200]}..."
            base_prompt += f"\nResume: {example.resume_text[:200]}..."
            base_prompt += f"\nIdeal Questions:"
            for q in example.ideal_questions[:3]:
                base_prompt += f"\n  - {q}"
        
        base_prompt += "\n\nNow analyze the following candidate using similar depth and relevance."
        
        return base_prompt
    
    def clear_examples(self):
        """Clear all training examples."""
        self._examples = []


# Global training data manager
training_manager = TrainingDataManager()


def get_enhanced_system_prompt() -> str:
    """Get the enhanced system prompt with training examples."""
    return training_manager.build_few_shot_prompt()


def add_training_data(resume: str, vacancy: str, questions: List[str], 
                     score: Optional[float] = None, 
                     skills: Optional[List[str]] = None):
    """
    Add training data to the manager.
    
    Args:
        resume: Resume text
        vacancy: Vacancy description
        questions: List of ideal screening questions  
        score: Match score (0-1)
        skills: Matched skills list
    """
    example = TrainingExample(
        resume_text=resume,
        vacancy_description=vacancy,
        ideal_questions=questions,
        score=score,
        skills_match=skills
    )
    training_manager.add_example(example)
