"""
シンプルなGradioアプリケーション
"""
import gradio as gr

def hello(name):
    return f"こんにちは、{name}さん！"

# デバッグ情報を出力
print("Gradioアプリケーションを初期化中...")

try:
    # シンプルなインターフェースを作成
    demo = gr.Interface(
        fn=hello,
        inputs="text",
        outputs="text",
        title="シンプルなGradioアプリ"
    )
    
    print("インターフェース作成完了、サーバー起動を開始します...")
    
    # サーバーを起動
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
    print("Gradioサーバーが起動しました。")
except Exception as e:
    print(f"エラーが発生しました: {str(e)}")
    import traceback
    traceback.print_exc()
