"""
Unit tests for the conversation flow.
"""
from app.graph.flow import ConversationGraph, ConversationState


def test_initialize_conversation():
    """Test initializing a conversation."""
    # Create a conversation graph
    graph = ConversationGraph()
    
    # Initialize a new state
    state: ConversationState = {
        "session_id": "test-session",
        "current_question_index": 0,
        "answers": {},
        "skipped_questions": [],
        "completed": False,
        "history": []
    }
    
    # Process the state through the initialize node
    result = graph._initialize_conversation(state)
    
    # Check that the state was initialized correctly
    assert result["session_id"] == "test-session"
    assert result["current_question_index"] == 0
    assert result["answers"] == {}
    assert result["skipped_questions"] == []
    assert result["completed"] is False
    assert result["history"] == []


def test_ask_question():
    """Test asking a question."""
    # Create a conversation graph
    graph = ConversationGraph()
    
    # Initialize a new state
    state: ConversationState = {
        "session_id": "test-session",
        "current_question_index": 0,
        "answers": {},
        "skipped_questions": [],
        "completed": False,
        "history": []
    }
    
    # Process the state through the ask_question node
    result = graph._ask_question(state)
    
    # Check that the state was not modified (since we're just asking a question)
    assert result["current_question_index"] == 0
    assert result["completed"] is False


def test_process_answer():
    """Test processing an answer."""
    # Create a conversation graph
    graph = ConversationGraph()
    
    # Initialize a new state with a history entry
    state: ConversationState = {
        "session_id": "test-session",
        "current_question_index": 0,
        "answers": {},
        "skipped_questions": [],
        "completed": False,
        "history": [{"user": "1-3年"}]
    }
    
    # Process the state through the process_answer node
    result = graph._process_answer(state)
    
    # Check that the answer was processed correctly
    assert result["state"]["answers"]["experience"] == "1-3年"
    assert result["state"]["current_question_index"] == 1
    assert result["next"] == "ask_question"


def test_handle_skip():
    """Test handling a skip."""
    # Create a conversation graph
    graph = ConversationGraph()
    
    # Initialize a new state
    state: ConversationState = {
        "session_id": "test-session",
        "current_question_index": 0,
        "answers": {},
        "skipped_questions": [],
        "completed": False,
        "history": []
    }
    
    # Process the state through the handle_skip node
    result = graph._handle_skip(state)
    
    # Check that the skip was handled correctly
    assert 0 in result["state"]["skipped_questions"]
    assert result["state"]["current_question_index"] == 1
    assert result["next"] == "ask_question"


def test_check_completion():
    """Test checking completion."""
    # Create a conversation graph
    graph = ConversationGraph()
    
    # Initialize a new state with all required questions answered
    state: ConversationState = {
        "session_id": "test-session",
        "current_question_index": 5,  # Beyond the last question
        "answers": {
            "experience": "1-3年",
            "skills": "Python, FastAPI",
            "availability": "1ヶ月以内",
            "work_style": "リモートワーク"
        },
        "skipped_questions": [],
        "completed": False,
        "history": []
    }
    
    # Check completion
    result = graph._check_completion(state)
    
    # Check that completion was detected correctly
    assert result is True


def test_process_message():
    """Test processing a message."""
    # Create a conversation graph
    graph = ConversationGraph()
    
    # Process a message
    result = graph.process_message("test-session", "こんにちは")
    
    # Check that the response contains the expected fields
    assert "message" in result
    assert "options" in result
    assert "progress" in result
    assert "completed" in result
    assert result["completed"] is False
