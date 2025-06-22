"""
FastAPIエンドポイントのE2Eテスト
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    """
    ルートエンドポイントのテスト
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_interview_flow():
    """
    インタビューフローの完全なテスト：開始から全質問回答まで
    """
    # インタビュー開始
    start_response = client.post("/interview/start")
    assert start_response.status_code == 200
    
    response_data = start_response.json()
    assert "session_id" in response_data
    assert "question" in response_data
    
    session_id = response_data["session_id"]
    question = response_data["question"]
    assert question["question_id"] == "q1"
    
    # 最初の質問に回答
    answer_response = client.post("/interview/answer", json={
        "session_id": session_id,
        "question_id": "q1",
        "answer_type": "choice",
        "answer": question["options"][0]  # 最初の選択肢を選ぶ
    })
    
    assert answer_response.status_code == 200
    answer_data = answer_response.json()
    assert answer_data["status"] == "ok"
    assert "next_question" in answer_data
    
    # 次の質問があれば全て回答していく
    while "next_question" in answer_data and answer_data["next_question"] is not None:
        next_question = answer_data["next_question"]
        
        # 次の質問に回答
        answer_response = client.post("/interview/answer", json={
            "session_id": session_id,
            "question_id": next_question["question_id"],
            "answer_type": next_question["question_type"],
            "answer": next_question["options"][0] if next_question["options"] else ""
        })
        
        assert answer_response.status_code == 200
        answer_data = answer_response.json()
    
    # 全ての質問が終了したらcompletedステータスが返される
    assert answer_data["status"] == "completed"
    assert "completion_message" in answer_data


def test_invalid_session():
    """
    無効なセッションIDのテスト
    """
    response = client.post("/interview/answer", json={
        "session_id": "invalid-session-id",
        "question_id": "q1",
        "answer_type": "choice",
        "answer": "option1"
    })
    
    assert response.status_code == 404


def test_invalid_answer():
    """
    無効な回答のテスト
    """
    # インタビュー開始
    start_response = client.post("/interview/start")
    session_id = start_response.json()["session_id"]
    
    # 存在しない選択肢で回答
    response = client.post("/interview/answer", json={
        "session_id": session_id,
        "question_id": "q1",
        "answer_type": "choice",
        "answer": "non-existent-option"
    })
    
    assert response.status_code == 400


def test_question_list():
    """
    質問リスト取得のテスト
    """
    response = client.get("/interview/questions")
    assert response.status_code == 200
    assert "questions" in response.json()
    assert len(response.json()["questions"]) > 0
