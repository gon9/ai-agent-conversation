"""
Gradio UI for the conversational AI agent.
"""
import uuid
from typing import Dict, List, Optional, Tuple

import gradio as gr
import requests

# API endpoint
API_URL = "http://localhost:8000/chat"


def format_progress(progress: Optional[Dict[str, int]]) -> str:
    """
    Format the progress indicator.
    
    Args:
        progress: Dictionary containing current and total progress
        
    Returns:
        str: Formatted progress string
    """
    if not progress:
        return ""
    
    current = progress.get("current", 0)
    total = progress.get("total", 0)
    
    return f"進捗: {current}/{total} 質問"


def create_chat_interface() -> gr.Blocks:
    import sys
    print("create_chat_interface: 開始", file=sys.stderr)
    sys.stderr.flush()
    """
    Create the Gradio chat interface.
    
    Returns:
        gr.Blocks: The Gradio interface
    """
    print("create_chat_interface: gr.Blocks作成前", file=sys.stderr)
    sys.stderr.flush()
    with gr.Blocks(title="求人情報収集エージェント") as demo:
        print("create_chat_interface: gr.Blocks作成後", file=sys.stderr)
        sys.stderr.flush()
        # Session ID for the conversation
        print("create_chat_interface: gr.State作成前", file=sys.stderr)
        sys.stderr.flush()
        session_id = gr.State(lambda: str(uuid.uuid4()))
        print("create_chat_interface: gr.State作成後", file=sys.stderr)
        sys.stderr.flush()
        
        # Chat history
        print("create_chat_interface: gr.Chatbot作成前", file=sys.stderr)
        sys.stderr.flush()
        chatbot = gr.Chatbot(
            label="会話",
            height=400,
            type="messages",  # Use messages format instead of deprecated tuples format
        )
        
        # Progress indicator
        print("create_chat_interface: gr.Chatbot作成後, gr.Markdown作成前", file=sys.stderr)
        sys.stderr.flush()
        progress_indicator = gr.Markdown(
            value="",
            label="進捗状況"
        )
        
        # Message input
        print("create_chat_interface: gr.Markdown作成後, gr.Textbox作成前", file=sys.stderr)
        sys.stderr.flush()
        msg = gr.Textbox(
            placeholder="メッセージを入力してください...",
            label="メッセージ",
            scale=4
        )
        
        # Option buttons container
        print("create_chat_interface: gr.Textbox作成後, gr.Row作成前", file=sys.stderr)
        sys.stderr.flush()
        option_container = gr.Row(visible=False)
        option_buttons: List[gr.Button] = []
        
        # Function to handle option button clicks
        def option_click(option: str, session: str) -> Tuple[List, str, str]:
            """
            Handle option button clicks.
            
            Args:
                option: The selected option
                session: The session ID
                
            Returns:
                Tuple: Updated chatbot, empty message, and progress
            """
            # Send the option to the API
            response = send_message(option, session)
            
            # Update the chatbot
            history = chatbot.value.copy() if chatbot.value else []
            history.append((option, response["message"]))
            
            # Update progress
            progress = format_progress(response.get("progress"))
            
            # Update options
            update_options(response.get("options", []))
            
            return history, "", progress

        # Create option buttons (pre-create 5 buttons)
        with option_container:
            for i in range(5):
                btn = gr.Button(f"Option {i+1}", visible=False)
                option_buttons.append(btn)
        
        def update_options(options: List[str]) -> None:
            """
            Update the option buttons based on available options.
            
            Args:
                options: List of option strings
            """
            # Hide all buttons first
            for btn in option_buttons:
                btn.visible = False
            
            # Show and update buttons for available options
            if options:
                option_container.visible = True
                for i, option in enumerate(options[:5]):  # Limit to 5 options
                    option_buttons[i].visible = True
                    option_buttons[i].value = option
                    
                    # Update the click handler
                    option_buttons[i].click(
                        option_click,
                        inputs=[gr.State(option), session_id],
                        outputs=[chatbot, msg, progress_indicator]
                    )
            else:
                option_container.visible = False

        def send_message(message: str, session: str) -> Dict:
            """
            Send a message to the API.
            
            Args:
                message: The message to send
                session: The session ID
                
            Returns:
                Dict: The API response
            """
            # Debug: Print session ID type and value
            print(f"Debug - Session ID type: {type(session)}, value: {session}")
            
            # Ensure session_id is a string
            session_str = str(session) if session is not None else str(uuid.uuid4())
            
            # Send the message to the API
            payload = {"session_id": session_str, "message": message}
            print(f"Debug - Payload: {payload}")
            
            response = requests.post(
                API_URL,
                json=payload
            )
            
            # Debug: Print response status and content
            print(f"Debug - Response status: {response.status_code}")
            
            # Return the response
            return response.json()

        def user_message(message: str, session: str) -> Tuple[List, str, str]:
            """
            Process a user message.
            
            Args:
                message: The message to process
                session: The session ID
                
            Returns:
                Tuple: Updated chat history, empty message, and progress indicator
            """
            # Skip if message is empty
            if not message:
                return chatbot.value, "", progress_indicator.value
            
            # Send the message to the API
            try:
                response = send_message(message, session)
                
                # Debug: Print response
                print(f"Debug - API Response: {response}")
                
                # Ensure response has a message key
                if not isinstance(response, dict) or "message" not in response:
                    print(f"Debug - Invalid response format: {response}")
                    response = {"message": "エラーが発生しました。もう一度お試しください。"}
                
                # Update the chatbot (using messages format)
                history = chatbot.value.copy() if chatbot.value else []
                
                # Add user message
                history.append({"role": "user", "content": message})
                
                # Add assistant message
                history.append({"role": "assistant", "content": response["message"]})
                
                # Update progress
                progress = format_progress(response.get("progress"))
                
                # Update options
                update_options(response.get("options", []))
                
                return history, "", progress
            except Exception as e:
                # Debug: Print exception
                print(f"Debug - Exception in user_message: {str(e)}")
                
                # Update the chatbot with error message
                history = chatbot.value.copy() if chatbot.value else []
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": f"エラーが発生しました: {str(e)}。もう一度お試しください。"})
                
                return history, "", progress_indicator.value

        # Set up the message submission
        msg.submit(
            user_message,
            inputs=[msg, session_id],
            outputs=[chatbot, msg, progress_indicator]
        )
        
        # Welcome message
        gr.on(
            triggers=[demo.load],
            fn=lambda session: (
                [
                    {"role": "assistant", "content": "こんにちは！求人応募のための追加情報を教えてください。いつでもスキップと入力すると質問をスキップできます。"}
                ],
                format_progress({"current": 0, "total": 5})
            ),
            inputs=[session_id],
            outputs=[chatbot, progress_indicator]
        )
        
        # Add a skip button
        skip_btn = gr.Button("この質問をスキップ")
        skip_btn.click(
            user_message,
            inputs=[gr.State("スキップ"), session_id],
            outputs=[chatbot, msg, progress_indicator]
        )
        
        # Add a restart button
        restart_btn = gr.Button("会話をリスタート")
        
        def restart_conversation() -> Tuple[str, List, str]:
            """
            Restart the conversation.
            
            Returns:
                Tuple: New session ID, empty chatbot, and empty progress
            """
            new_session = str(uuid.uuid4())
            return new_session, [], ""
        
        restart_btn.click(
            restart_conversation,
            inputs=[],
            outputs=[session_id, chatbot, progress_indicator]
        )
        
    print("create_chat_interface: 終了", file=sys.stderr)
    sys.stderr.flush()
    return demo


def launch_ui() -> None:
    """
    Launch the Gradio UI.
    """
    import sys
    print("Gradioインターフェースを起動します...", file=sys.stderr)
    try:
        demo = create_chat_interface()
        print("インターフェース作成完了、サーバー起動を開始します...", file=sys.stderr)
        # 標準エラー出力にフラッシュ
        sys.stderr.flush()
        # 詳細なデバッグ情報を有効にして起動
        demo.launch(
            server_name="0.0.0.0", 
            server_port=7860,
            debug=True,
            quiet=False,
            show_error=True
        )
        print("Gradioサーバーが起動しました。", file=sys.stderr)
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()


if __name__ == "__main__":
    launch_ui()
