"""
Configuration settings for the conversational AI agent.
"""
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# UI settings
UI_HOST = os.getenv("UI_HOST", "0.0.0.0")
UI_PORT = int(os.getenv("UI_PORT", "7860"))

# LLM settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Conversation settings
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "10"))
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))

# Define the questions to be asked - can be moved to a JSON file later
QUESTIONS: List[Dict[str, Optional[object]]] = [
    {
        "id": "experience",
        "question": "あなたの関連職務経験年数を教えてください",
        "options": ["未経験", "1-3年", "4-6年", "7-10年", "10年以上"],
        "required": True,
    },
    {
        "id": "skills",
        "question": "あなたの主要なスキルを教えてください",
        "options": None,  # Free text input
        "required": True,
    },
    {
        "id": "availability",
        "question": "いつから就業可能ですか？",
        "options": ["すぐに可能", "1ヶ月以内", "2ヶ月以内", "3ヶ月以上先"],
        "required": True,
    },
    {
        "id": "salary",
        "question": "希望年収を教えてください",
        "options": ["400万円以下", "400-600万円", "600-800万円", "800-1000万円", "1000万円以上"],
        "required": False,
    },
    {
        "id": "work_style",
        "question": "希望する働き方を教えてください",
        "options": ["オフィス勤務", "リモートワーク", "ハイブリッド"],
        "required": True,
    },
]
