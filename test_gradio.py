"""
Gradioの動作テスト
"""
import gradio as gr

def greet(name):
    return f"こんにちは、{name}さん！"

# シンプルなGradioインターフェースを作成
demo = gr.Interface(
    fn=greet,
    inputs="text",
    outputs="text",
    title="Gradioテスト"
)

if __name__ == "__main__":
    print("Gradioインターフェースを起動します...")
    demo.launch(server_name="0.0.0.0", server_port=7860)
    print("Gradioインターフェースが起動しました。")
