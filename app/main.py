"""
Main FastAPI application entry point for the interview system.
"""
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid

from app.graph.flow import QUESTIONS
from app.models.schemas import (
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    NextQuestion,
    ConversationState,
    InterviewQuestion
)

# 質問データをInterviewQuestionモデルに変換
# 今後はSQliteなどで管理する予定
INTERVIEW_QUESTIONS: Dict[str, InterviewQuestion] = {
    q.id: InterviewQuestion(
        question_id=q.id,
        question_type="choice",
        question_text=q.question,
        options=q.options,
        reactions=q.reactions
    ) for q in QUESTIONS
}

app = FastAPI(title="AI面接システム", description="選択式質問による面接システム", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンに制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 会話状態を保存するディクショナリ
session_states: Dict[str, ConversationState] = {}


@app.post("/interview/start")
async def start_interview(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    面接を開始し、最初の質問を返します。
    
    Args:
        user_id: オプションのユーザーID
    
    Returns:
        Dict: セッションIDと最初の質問を含む辞書
    """
    # 新しいセッションIDを生成
    session_id = str(uuid.uuid4())
    
    # 最初の質問を取得
    first_question = INTERVIEW_QUESTIONS["q1"]
    
    # セッション状態を初期化
    session_states[session_id] = ConversationState(
        user_id=user_id,
        current_question_id="q1",
        answers={},
        completed=False
    )
    
    return {
        "session_id": session_id,
        "question": {
            "question_id": first_question.question_id,
            "question_type": first_question.question_type,
            "question_text": first_question.question_text,
            "options": first_question.options
        }
    }


@app.post("/interview/answer", response_model=InterviewAnswerResponse)
async def process_answer(request: InterviewAnswerRequest) -> InterviewAnswerResponse:
    """
    面接の回答を処理し、次の質問または完了メッセージを返します。
    
    Args:
        request: 面接回答リクエスト
        
    Returns:
        InterviewAnswerResponse: 次の質問または完了メッセージを含むレスポンス
        
    Raises:
        HTTPException: リクエスト処理中にエラーが発生した場合
    """
    try:
        session_id = request.session_id
        question_id = request.question_id
        answer = request.answer
        
        # セッションが存在するか確認
        if session_id not in session_states:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        state = session_states[session_id]
        
        # 質問が存在するか確認
        if question_id not in INTERVIEW_QUESTIONS:
            raise HTTPException(status_code=404, detail="質問が見つかりません")
        
        current_question = INTERVIEW_QUESTIONS[question_id]
        
        # 回答が有効か確認（選択式の場合）
        if current_question.question_type == "choice" and answer not in current_question.options:
            raise HTTPException(status_code=400, detail="無効な回答です")
        
        # 回答を記録
        state.answers[question_id] = answer
        
        # 次の質問を決定
        next_question_id = get_next_question_id(question_id)
        
        if next_question_id:
            # 次の質問がある場合
            next_question = INTERVIEW_QUESTIONS[next_question_id]
            state.current_question_id = next_question_id
            
            return InterviewAnswerResponse(
                status="ok",
                next_question=NextQuestion(
                    question_id=next_question.question_id,
                    question_type=next_question.question_type,
                    question_text=next_question.question_text,
                    options=next_question.options
                )
            )
        else:
            # 全質問完了
            state.completed = True
            
            # 回答の分析や集計を行う場合はここで実装
            # この例では単純な完了メッセージを返す
            return InterviewAnswerResponse(
                status="completed",
                completion_message="すべての質問に回答いただき、ありがとうございました。結果を分析中です。"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in interview answer processing: {e}")
        raise HTTPException(status_code=500, detail=f"内部サーバーエラー: {str(e)}")


@app.get("/interview/questions")
async def list_questions() -> Dict[str, List[Dict[str, Any]]]:
    """
    利用可能な質問のリストを返します。
    
    Returns:
        Dict: 質問リストを含む辞書
    """
    questions = []
    for q_id, question in INTERVIEW_QUESTIONS.items():
        questions.append({
            "question_id": question.question_id,
            "question_type": question.question_type,
            "question_text": question.question_text,
            "options": question.options
        })
    
    return {"questions": questions}


def get_next_question_id(current_id: str) -> Optional[str]:
    """
    現在の質問IDから次の質問IDを取得します。
    
    Args:
        current_id: 現在の質問ID
        
    Returns:
        Optional[str]: 次の質問ID、最後の質問の場合はNone
    """
    # 質問IDを順番に取得
    question_ids = list(INTERVIEW_QUESTIONS.keys())
    
    try:
        current_index = question_ids.index(current_id)
        if current_index < len(question_ids) - 1:
            return question_ids[current_index + 1]
    except ValueError:
        pass
    
    return None


@app.get("/interview/resume/{session_id}")
async def resume_interview(session_id: str) -> Dict[str, Any]:
    """
    既存の面接セッションを再開します。セッションIDが存在しない場合は404エラーを返します。
    
    Args:
        session_id: 再開するセッションID
        
    Returns:
        Dict: セッションIDと現在の質問情報を含む辞書
        
    Raises:
        HTTPException: セッションが存在しない場合
    """
    # セッションが存在するか確認
    if session_id not in session_states:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    # セッション状態を取得
    state = session_states[session_id]
    
    # 既に完了している場合
    if state.completed:
        return {
            "session_id": session_id,
            "completed": True,
            "message": "このインタビューは既に完了しています"
        }
    
    # 現在の質問を取得
    current_question_id = state.current_question_id
    current_question = INTERVIEW_QUESTIONS.get(current_question_id)
    
    if not current_question:
        raise HTTPException(status_code=500, detail="質問データが見つかりません")
    
    # 次の質問を返す
    return {
        "session_id": session_id,
        "question": {
            "question_id": current_question.question_id,
            "question_type": current_question.question_type,
            "question_text": current_question.question_text,
            "options": current_question.options
        },
        "progress": {
            "answered_questions": len(state.answers),
            "total_questions": len(INTERVIEW_QUESTIONS)
        }
    }


@app.get("/")
async def root():
    """
    ルートエンドポイント
    """
    return {"status": "ok", "message": "AI面接システムAPIが稼働中です"}
