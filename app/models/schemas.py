"""
Pydantic models for the conversational AI agent.
"""
from typing import Dict, List, Optional, Literal

from pydantic import BaseModel, Field


class InterviewOption(BaseModel):
    """
    選択肢モデル
    """
    value: str
    label: str


class InterviewQuestion(BaseModel):
    """
    面接質問モデル
    """
    question_id: str = Field(description="質問ID")
    question_type: Literal["choice", "text", "multiple_choice"] = Field(description="質問タイプ")
    question_text: str = Field(description="質問文")
    options: Optional[List[str]] = Field(description="選択肢")
    reactions: Optional[Dict[str, str]] = Field(description="リアクション")


class InterviewAnswerRequest(BaseModel):
    """
    面接回答リクエストモデル
    """
    session_id: str = Field(description="セッションID")
    question_id: str = Field(description="質問ID")
    answer_type: Literal["choice", "text", "multiple_choice"] = Field(description="回答タイプ")
    answer: str = Field(description="回答")


class NextQuestion(BaseModel):
    """
    次の質問モデル
    """
    question_id: str = Field(description="質問ID")
    question_type: Literal["choice", "text", "multiple_choice"] = Field(description="質問タイプ")
    question_text: str = Field(description="質問文")
    options: List[str] = Field(description="選択肢")


class InterviewAnswerResponse(BaseModel):
    """
    面接回答レスポンスモデル
    """
    status: str = Field(description="回答状態")
    next_question: Optional[NextQuestion] = Field(default=None, description="次の質問")
    completion_message: Optional[str] = Field(default=None, description="完了メッセージ")


class ConversationState(BaseModel):
    """
    会話状態モデル
    """
    user_id: Optional[str] = Field(default=None, description="ユーザーID（分析用）")
    current_question_id: str = Field(default="", description="現在の質問 ID")
    answers: Dict[str, str] = Field(default_factory=dict, description="回答履歴 (質問ID: 選択肢)")
    completed: bool = Field(default=False, description="会話完了フラグ")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="会話履歴")
    # 拡張フェーズⅠ用フィールド（現在は未使用）
    # needs_deep_dive: bool = Field(default=False, description="深堀り質問が必要かどうか")
    # follow_up_asked: bool = Field(default=False, description="すでに深堀り質問を届けたかどうか")
    # current_deep_dive_question: Optional[str] = Field(default=None, description="現在の深堀り質問")


class FixedQuestion(BaseModel):
    """
    固定質問モデル
    """
    id: str = Field(description="質問ID")
    question: str = Field(description="質問文")
    options: List[str] = Field(description="選択肢リスト")
    reactions: Dict[str, str] = Field(description="選択肢ごとのリアクション")
    # 拡張フェーズⅠ用フィールド（現在は未使用）
    # deep_dive_triggers: Dict[str, bool] = Field(default_factory=dict, description="どの回答が深堀りをトリガーするか")
    # follow_up_questions: Dict[str, str] = Field(default_factory=dict, description="選択肢ごとの深堀り質問")
