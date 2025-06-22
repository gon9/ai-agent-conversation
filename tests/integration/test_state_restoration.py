"""
Integration tests for state restoration in the conversation flow.
"""
from app.graph.flow import ConversationGraph


def test_session_state_persistence():
    """Test that session state is persisted between requests."""
    # Create a conversation graph
    graph = ConversationGraph()
    session_id = "test-persistence-session"
    
    # Send an initial message
    graph.process_message(session_id, "こんにちは")
    
    # Send an answer to the first question
    response2 = graph.process_message(session_id, "1-3年")
    
    # Check that we've moved to the second question
    assert "skills" in response2["message"].lower() or "スキル" in response2["message"]
    
    # Check that the progress has been updated
    assert response2["progress"]["current"] == 1
    
    # Send another message
    response3 = graph.process_message(session_id, "Python, FastAPI")
    
    # Check that we've moved to the third question
    assert "availability" in response3["message"].lower() or "就業可能" in response3["message"]
    
    # Check that the progress has been updated
    assert response3["progress"]["current"] == 2


def test_skip_and_return():
    """Test skipping a question and then returning to it later."""
    # Create a conversation graph
    graph = ConversationGraph()
    session_id = "test-skip-session"
    
    # Send an initial message
    graph.process_message(session_id, "こんにちは")
    
    # Skip the first question
    response1 = graph.process_message(session_id, "スキップ")
    
    # Check that we've moved to the second question
    assert "skills" in response1["message"].lower() or "スキル" in response1["message"]
    
    # Answer the second question
    response2 = graph.process_message(session_id, "Python, FastAPI")
    
    # Check that we've moved to the third question
    assert "availability" in response2["message"].lower() or "就業可能" in response2["message"]
    
    # Answer the third question
    graph.process_message(session_id, "1ヶ月以内")
    
    # Answer the fourth question (salary - optional)
    graph.process_message(session_id, "600-800万円")
    
    # Answer the fifth question
    response5 = graph.process_message(session_id, "リモートワーク")
    
    # Check that we're now being asked the first question again (which was skipped)
    assert "experience" in response5["message"].lower() or "経験年数" in response5["message"]
    
    # Answer the first question
    response6 = graph.process_message(session_id, "4-6年")
    
    # Check that we've completed the conversation
    assert response6["completed"] is True


def test_resume_conversation():
    """Test resuming a conversation after a break."""
    # Create a conversation graph
    graph = ConversationGraph()
    session_id = "test-resume-session"
    
    # Send an initial message
    graph.process_message(session_id, "こんにちは")
    
    # Answer the first question
    graph.process_message(session_id, "1-3年")
    
    # Answer the second question
    graph.process_message(session_id, "Python, FastAPI")
    
    # Create a new graph instance (simulating a server restart)
    new_graph = ConversationGraph()
    
    # Resume the conversation
    response = new_graph.process_message(session_id, "続けます")
    
    # Check that we're at the third question
    assert "availability" in response["message"].lower() or "就業可能" in response["message"]
    
    # Check that the progress is maintained
    assert response["progress"]["current"] == 2
