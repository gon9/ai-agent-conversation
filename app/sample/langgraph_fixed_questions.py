import json
import sqlite3
from typing import Dict, Any, List
from datetime import datetime
from langgraph.graph import Graph, END
from pydantic import BaseModel

# 状態管理用のモデル
class QuestionState(BaseModel):
    current_question_index: int = 0
    user_id: str = ""
    answers: List[Dict[str, Any]] = []
    current_question: Dict[str, Any] = {}
    current_answer: str = ""
    reaction_message: str = ""
    is_complete: bool = False

# 事前定義された質問リスト（JSON形式）
QUESTION_LIST = [
    {
        "id": 1,
        "question": "あなたの好きな季節は何ですか？",
        "options": ["春", "夏", "秋", "冬"],
        "reactions": {
            "春": "桜の季節ですね！新しい始まりの季節、素敵です。",
            "夏": "夏祭りや海水浴、アクティブな季節ですね！",
            "秋": "紅葉が美しい季節ですね。読書の秋でもあります。",
            "冬": "雪景色やイルミネーション、静寂な美しさがありますね。"
        }
    },
    {
        "id": 2,
        "question": "普段よく飲む飲み物は何ですか？",
        "options": ["コーヒー", "紅茶", "緑茶", "ジュース", "水"],
        "reactions": {
            "コーヒー": "カフェインで一日をスタート！香りも楽しめますね。",
            "紅茶": "リラックスタイムにぴったり。種類も豊富で楽しいですね。",
            "緑茶": "健康的な選択ですね。日本の伝統的な飲み物です。",
            "ジュース": "ビタミン補給にもなりますね。フレッシュな味わいが魅力です。",
            "水": "最もヘルシーな選択！体にとって必要不可欠ですね。"
        }
    },
    {
        "id": 3,
        "question": "休日はどのように過ごすことが多いですか？",
        "options": ["家でゆっくり", "外出・買い物", "スポーツ・運動", "友人と会う"],
        "reactions": {
            "家でゆっくり": "おうち時間を大切にするタイプですね。リラックスできる時間は重要です。",
            "外出・買い物": "アクティブに行動するタイプですね。新しい発見もありそうです。",
            "スポーツ・運動": "健康的な過ごし方ですね。体を動かすことでリフレッシュできます。",
            "友人と会う": "人とのつながりを大事にするタイプですね。コミュニケーションは大切です。"
        }
    }
]

class FixedQuestionFlow:
    def __init__(self, db_path: str = "answers.db"):
        self.db_path = db_path
        self.setup_database()
        self.graph = self.create_graph()
    
    def setup_database(self):
        """データベースの初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def ask_question_list(self, state: QuestionState) -> QuestionState:
        """質問リストから現在の質問を取得"""
        print(f"\n=== 質問 {state.current_question_index + 1}/{len(QUESTION_LIST)} ===")
        
        if state.current_question_index >= len(QUESTION_LIST):
            state.is_complete = True
            return state
        
        current_q = QUESTION_LIST[state.current_question_index]
        state.current_question = current_q
        
        print(f"質問: {current_q['question']}")
        print("選択肢:")
        for i, option in enumerate(current_q['options'], 1):
            print(f"  {i}. {option}")
        
        # ユーザーからの入力を受け取る
        while True:
            try:
                choice = input("\n番号を選択してください: ")
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(current_q['options']):
                    state.current_answer = current_q['options'][choice_idx]
                    break
                else:
                    print("無効な選択です。もう一度選択してください。")
            except ValueError:
                print("数字を入力してください。")
        
        return state
    
    def record_answer(self, state: QuestionState) -> QuestionState:
        """回答をデータベースに保存（LLM呼び出しなし）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO answers (user_id, question_id, question, answer)
            VALUES (?, ?, ?, ?)
        ''', (
            state.user_id,
            state.current_question['id'],
            state.current_question['question'],
            state.current_answer
        ))
        
        conn.commit()
        conn.close()
        
        # 回答を履歴に追加
        state.answers.append({
            "question_id": state.current_question['id'],
            "question": state.current_question['question'],
            "answer": state.current_answer,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✓ 回答を保存しました: {state.current_answer}")
        return state
    
    def fixed_reaction(self, state: QuestionState) -> QuestionState:
        """選択内容に紐付く固定メッセージを設定"""
        reactions = state.current_question.get('reactions', {})
        reaction = reactions.get(state.current_answer, "ご回答ありがとうございます。")
        
        state.reaction_message = reaction
        print(f"\n💬 {reaction}")
        
        # 次の質問へ
        state.current_question_index += 1
        return state
    
    def should_continue(self, state: QuestionState) -> str:
        """次のステップを決定"""
        if state.is_complete:
            return END
        return "ask_question_list"
    
    def create_graph(self) -> Graph:
        """LangGraphのワークフロー作成"""
        workflow = Graph()
        
        # ノードを追加
        workflow.add_node("ask_question_list", self.ask_question_list)
        workflow.add_node("record_answer", self.record_answer)
        workflow.add_node("fixed_reaction", self.fixed_reaction)
        
        # エッジを追加
        workflow.set_entry_point("ask_question_list")
        workflow.add_edge("ask_question_list", "record_answer")
        workflow.add_edge("record_answer", "fixed_reaction")
        workflow.add_conditional_edges(
            "fixed_reaction",
            self.should_continue,
            {
                "ask_question_list": "ask_question_list",
                END: END
            }
        )
        
        return workflow.compile()
    
    def run_survey(self, user_id: str):
        """アンケート実行"""
        print("=== 固定質問アンケート開始 ===")
        
        initial_state = QuestionState(user_id=user_id)
        
        # ワークフロー実行
        final_state = self.graph.invoke(initial_state)
        
        print("\n=== アンケート完了 ===")
        print("ご協力ありがとうございました！")
        
        # 結果表示
        print("\n=== 回答履歴 ===")
        for answer in final_state.answers:
            print(f"Q: {answer['question']}")
            print(f"A: {answer['answer']}")
            print("---")
        
        return final_state

# データベースから回答履歴を取得する関数
def get_user_answers(db_path: str, user_id: str) -> List[Dict]:
    """特定ユーザーの回答履歴を取得"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT question_id, question, answer, timestamp
        FROM answers
        WHERE user_id = ?
        ORDER BY timestamp
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "question_id": row[0],
            "question": row[1],
            "answer": row[2],
            "timestamp": row[3]
        }
        for row in results
    ]

# 使用例
if __name__ == "__main__":
    # フロー実行
    flow = FixedQuestionFlow()
    
    # アンケート実行
    user_id = input("ユーザーIDを入力してください: ")
    result = flow.run_survey(user_id)
    
    # 過去の回答履歴確認（オプション）
    print("\n=== 過去の回答履歴確認 ===")
    check_history = input("過去の回答履歴を確認しますか？ (y/n): ")
    if check_history.lower() == 'y':
        history = get_user_answers("answers.db", user_id)
        if history:
            for record in history:
                print(f"[{record['timestamp']}] {record['question']} → {record['answer']}")
        else:
            print("履歴がありません。")