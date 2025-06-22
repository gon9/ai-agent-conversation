"""
OpenAI APIへの接続テスト
"""
import os
from openai import OpenAI

def test_openai_connection():
    """OpenAI APIへの接続をテストする"""
    print("OpenAI接続テスト開始")
    
    # APIキーを取得
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("エラー: OPENAI_API_KEYが設定されていません")
        return False
    
    print(f"APIキー: {api_key[:10]}...")
    
    # OpenAIクライアントを初期化
    client = OpenAI(api_key=api_key)
    
    try:
        # シンプルなリクエストを送信
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "こんにちは"}],
            max_tokens=10
        )
        
        # レスポンスを表示
        content = response.choices[0].message.content
        print(f"成功: レスポンス = {content}")
        return True
    
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()
