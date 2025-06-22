"""
固定質問フローの定義ファイル
"""
from typing import Any, Dict

from langgraph.graph import StateGraph
from langgraph.graph.graph import END
from langgraph.checkpoint.memory import MemorySaver

# スキーマをインポート
from app.models.schemas import ConversationState, FixedQuestion

# 固定質問リスト
QUESTIONS = [
    FixedQuestion(
        id="q1",
        question="あなたの現在の職業は何ですか？",
        options=["会社員", "自営業", "学生", "その他"],
        reactions={
            "会社員": "企業でのお仕事、お疲れ様です。次の質問に進みましょう。",
            "自営業": "自分のビジネスを経営されているのですね。次の質問に進みましょう。",
            "学生": "学業との両立、頑張ってくださいね。次の質問に進みましょう。",
            "その他": "承知しました。次の質問に進みましょう。"
        }
    ),
    FixedQuestion(
        id="q2",
        question="キャリアについて最も関心のある分野はどれですか？",
        options=["技術スキル向上", "マネジメント能力", "起業・独立", "ワークライフバランス"],
        reactions={
            "技術スキル向上": "専門性を高めることは重要ですね。最後の質問に進みましょう。",
            "マネジメント能力": "人をまとめる力は貴重なスキルです。最後の質問に進みましょう。",
            "起業・独立": "自分のビジョンを形にするのは素晴らしいことです。最後の質問に進みましょう。",
            "ワークライフバランス": "充実した人生のために大切な視点ですね。最後の質問に進みましょう。"
        }
    ),
    FixedQuestion(
        id="q3",
        question="今後のキャリアでどのような支援が欲しいですか？",
        options=["メンタリング", "スキルトレーニング", "ネットワーキング", "キャリアカウンセリング"],
        reactions={
            "メンタリング": "経験者からのアドバイスは貴重ですね。ご回答ありがとうございました。",
            "スキルトレーニング": "実践的なスキルを身につけることは重要です。ご回答ありがとうございました。",
            "ネットワーキング": "人脈は大切な資産になりますね。ご回答ありがとうございました。",
            "キャリアカウンセリング": "専門家のアドバイスで道が開けることもあります。ご回答ありがとうございました。"
        }
    )
]


class ConversationGraph:
    """
    固定質問フローの会話グラフを管理するクラス
    """
    
    def __init__(self) -> None:
        """
        固定質問フローの会話グラフを初期化します。
        """
        # 質問リストの設定
        self.questions = QUESTIONS
        
        # ノード関数の定義
        self.workflow = self._create_workflow()
        
        # チェックポインターを設定
        self.memory_saver = MemorySaver()
        
        # グラフをコンパイル
        self.compiled_workflow = self.workflow.compile(checkpointer=self.memory_saver)
    
    def _ask_question_node(self, state: ConversationState) -> Dict[str, Any]:
        """
        質問リストから現在の質問を取得します。
        """
        current_question_id = state.current_question_id
        current_question = None
        
        for question in self.questions:
            if question.id == current_question_id:
                current_question = question
                break
        
        if not current_question:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "質問が見つかりませんでした。"
                    }
                ]
            }
        
        return {
            "messages": [
                {
                    "role": "assistant", 
                    "content": f"{current_question.question}\n\n" + "\n".join([f"- {option}" for option in current_question.options])
                }
            ]
        }
    
    def _record_answer_node(self, state: ConversationState) -> Dict[str, Any]:
        """
        ユーザーの回答を記録します。LLMは使用しません。
        """
        messages = state.messages
        last_user_msg = None
        
        # 最新のユーザーメッセージを見つける
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        
        if not last_user_msg:
            return {"messages": messages}
        
        # 回答を記録
        state.answers[state.current_question_id] = last_user_msg
        
        # 次の質問のIDを設定するか、完了フラグをセット
        next_question_id = None
        
        # 単純な順序で次の質問を選択
        if state.current_question_id == "q1":
            next_question_id = "q2"
        elif state.current_question_id == "q2":
            next_question_id = "q3"
        else:
            # q3が最後の質問
            state.completed = True
        
        if next_question_id:
            state.current_question_id = next_question_id
        
        return {"messages": messages}
    
    def _fixed_reaction_node(self, state: ConversationState) -> Dict[str, Any]:
        """
        選択内容に紐付く固定メッセージを返します。
        """
        current_question_id = state.current_question_id
        last_question_id = state.current_question_id
        
        # 完了している場合は最後の質問IDを取得
        if state.completed:
            # 最後に回答された質問のIDを取得
            last_question_keys = list(state.answers.keys())
            if last_question_keys:
                last_question_id = last_question_keys[-1]
        
        # 該当する質問を取得
        question = None
        for q in self.questions:
            if q.id == last_question_id:
                question = q
                break
        
        if not question:
            return {
                "messages": state.messages + [{"role": "assistant", "content": "質問が見つかりませんでした。"}]
            }
        
        # 回答を取得
        answer = state.answers.get(last_question_id)
        if not answer:
            return {
                "messages": state.messages + [{"role": "assistant", "content": "回答が記録されていません。"}]
            }
        
        # 反応メッセージを取得
        reaction = question.reactions.get(answer, "ご回答ありがとうございます。")
        
        return {
            "messages": state.messages + [{"role": "assistant", "content": reaction}]
        }
    
    # 拡張フェーズIで追加予定の深堀り質問判定ノード
    def _decide_deep_dive_node(self, state: ConversationState) -> ConversationState:
        """
        回答に基づいて深堀り質問が必要かどうかを判定します。
        
        Args:
            state: 現在の会話状態。
            
        Returns:
            更新された会話状態。
        """
        # 現在はコメントアウトされていますが、拡張フェーズIではここで深堀り判定を行います
        # current_question_id = state.current_question_id
        # current_answer = state.answers.get(current_question_id, "")
        # 
        # # 質問オブジェクトを取得
        # current_question = next((q for q in self.questions if q.id == current_question_id), None)
        # 
        # if current_question and current_answer in current_question.deep_dive_triggers:
        #     # 深堀り条件に一致する場合
        #     state.needs_deep_dive = current_question.deep_dive_triggers.get(current_answer, False)
        # 
        # return state
        
        # 現在は深堀りなしにする
        return state
    
    # 拡張フェーズIで追加予定の深堀り質問ノード
    def _ask_follow_up_node(self, state: ConversationState) -> ConversationState:
        """
        深堀り質問を届けます。
        
        Args:
            state: 現在の会話状態。
            
        Returns:
            更新された会話状態。
        """
        # 現在はコメントアウトされていますが、拡張フェーズIではここで深堀り質問を行います
        # current_question_id = state.current_question_id
        # current_answer = state.answers.get(current_question_id, "")
        # 
        # # 質問オブジェクトを取得
        # current_question = next((q for q in self.questions if q.id == current_question_id), None)
        # 
        # if current_question and current_answer in current_question.follow_up_questions:
        #     # 深堀り質問を取得
        #     follow_up = current_question.follow_up_questions.get(current_answer, "")
        #     if follow_up:
        #         state.current_deep_dive_question = follow_up
        #         state.follow_up_asked = True
        #         state.messages.append({"role": "assistant", "content": follow_up})
        # 
        # return state
        
        # 現在は深堀りなしにする
        return state

    def _create_workflow(self):
        """
        固定質問フローのワークフローを作成します。
        """
        builder = StateGraph(ConversationState)
        
        # ノードの追加
        builder.add_node("ask_question", self._ask_question_node)
        builder.add_node("record_answer", self._record_answer_node)
        builder.add_node("fixed_reaction", self._fixed_reaction_node)
        
        # 拡張フェーズIで追加予定のノード
        # builder.add_node("deep_dive_trigger", self._decide_deep_dive_node)
        # builder.add_node("ask_follow_up", self._ask_follow_up_node)
        
        # 開始ノードの設定
        builder.set_entry_point("ask_question")
        
        # エッジの追加
        builder.add_edge("ask_question", "record_answer")
        builder.add_edge("record_answer", "fixed_reaction")
        
        # 拡張フェーズIで変更予定の条件分岐設定
        # builder.remove_edge("record_answer", "fixed_reaction")
        # builder.add_edge("record_answer", "deep_dive_trigger")
        # 
        # # 深堀り判定ノードからの分岐
        # builder.add_conditional_edges(
        #     "deep_dive_trigger",
        #     lambda state: "need_deep_dive" if state.needs_deep_dive else "no_deep_dive",
        #     {
        #         "need_deep_dive": "ask_follow_up",
        #         "no_deep_dive": "fixed_reaction" 
        #     }
        # )
        # builder.add_edge("ask_follow_up", "fixed_reaction")
        
        # 条件分岐：完了または次の質問へ
        builder.add_conditional_edges(
            "fixed_reaction",
            lambda state: "completed" if state.completed else "not_completed",
            {
                "not_completed": "ask_question",
                "completed": END
            }
        )
        
        return builder
    
    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        ユーザーからのメッセージを処理し、固定質問フローの応答を返します。

        Args:
            session_id: セッションID。
            message: ユーザーからのメッセージ内容。

        Returns:
            固定質問フローの応答メッセージを含む辞書。
        """
        # 既存のセッション状態を取得するか、新しいセッションを初期化
        state = self.memory_saver.get(session_id, None)
        
        if state is None:
            # 新しいセッションの場合は初期状態を設定
            state = ConversationState(
                current_question_id="q1",
                messages=[],
                answers={},
                completed=False
            )
        
        # ユーザーのメッセージをステートに追加
        state.messages.append({"role": "user", "content": message})
        
        # ワークフロー実行
        result = self.compiled_workflow.invoke({
            "messages": state.messages,
            "current_question_id": state.current_question_id,
            "answers": state.answers,
            "completed": state.completed
        }, {"configurable": {"session_id": session_id}})
        
        # 最後のアシスタントのメッセージを取得
        last_message = ""
        if result["messages"]:
            for msg in reversed(result["messages"]):
                if msg["role"] == "assistant":
                    last_message = msg["content"]
                    break
        
        return {
            "message": last_message,
            "completed": result["completed"]
        }
