"""Constants defined module."""

import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
LOG_FILE = os.path.join(LOG_DIR, "custom_chatbot.log")
os.makedirs(LOG_DIR, exist_ok=True)

# ---------------- Chatbot Parameters ----------------
GENERIC_CHATBOT_URI = os.environ.get("GENERIC_CHATBOT_URI", "")
RAG_CHATBOT_URI = os.environ.get("RAG_CHATBOT_URI", "")
SQL_CHATBOT_URI = os.environ.get("SQL_CHATBOT_URI", "")
MONGO_DB_CHATBOT_URI = os.environ.get("MONGO_DB_CHATBOT_URI", "")

MISTRAL_URI = os.environ.get("MISTRAL_URI", "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3")
LLAMA_URI = os.environ.get("LLAMA_URI", "https://huggingface.co/meta-llama/Meta-Llama-3.1-8B")
GEMMA_URI = os.environ.get("GEMMA_URI", "https://huggingface.co/google/gemma-2-9b")
