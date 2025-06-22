"""
Helper utilities for the conversational AI agent.
"""
import datetime
import uuid
from typing import Any, Dict, Optional

from app.config.settings import QUESTIONS


def generate_session_id() -> str:
    """
    Generate a unique session ID.
    
    Returns:
        str: A unique session ID
    """
    return str(uuid.uuid4())


def get_question_by_index(index: int) -> Optional[Dict[str, Any]]:
    """
    Get a question by its index.
    
    Args:
        index: The index of the question
        
    Returns:
        Optional[Dict[str, Any]]: The question or None if not found
    """
    if 0 <= index < len(QUESTIONS):
        return QUESTIONS[index]
    return None


def get_question_by_id(question_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a question by its ID.
    
    Args:
        question_id: The ID of the question
        
    Returns:
        Optional[Dict[str, Any]]: The question or None if not found
    """
    for question in QUESTIONS:
        if question["id"] == question_id:
            return question
    return None


def calculate_progress(answers: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate the progress of the conversation.
    
    Args:
        answers: Dictionary of answers
        
    Returns:
        Dict[str, int]: Progress information with current and total counts
    """
    total_required = sum(1 for q in QUESTIONS if q.get("required", True))
    answered_required = sum(
        1 for q in QUESTIONS 
        if q.get("required", True) and q["id"] in answers
    )
    
    return {
        "current": answered_required,
        "total": total_required
    }


def format_timestamp() -> str:
    """
    Format the current timestamp.
    
    Returns:
        str: Formatted timestamp
    """
    return datetime.datetime.now().isoformat()


def is_valid_option(question: Dict[str, Any], answer: str) -> bool:
    """
    Check if an answer is a valid option for a question.
    
    Args:
        question: The question dictionary
        answer: The user's answer
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not question.get("options"):
        return True  # Free text input
    
    return answer in question["options"]
