"""Constants defined module."""

import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
LOG_FILE = os.path.join(LOG_DIR, "custom_chatbot.log")
os.makedirs(LOG_DIR, exist_ok=True)

# ---------------- Chatbot Parameters ----------------
GENERIC_CHATBOT_URI = os.environ.get("GENERIC_CHATBOT_URI", "https://hub.docker.com/repository/docker/sancheet/generic_chatbot/general")
RAG_CHATBOT_URI = os.environ.get("RAG_CHATBOT_URI", "https://hub.docker.com/repository/docker/sancheet/rag_chat_with_docs/general")
SQL_CHATBOT_URI = os.environ.get("SQL_CHATBOT_URI", "https://hub.docker.com/repository/docker/sancheet/sql_chatbot_api/general")
MONGO_DB_CHATBOT_URI = os.environ.get("MONGO_DB_CHATBOT_URI", "https://hub.docker.com/repository/docker/sancheet/mongo_rag_chatbot/general")

MISTRAL_URI = os.environ.get("MISTRAL_URI", "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3")
LLAMA_URI = os.environ.get("LLAMA_URI", "https://huggingface.co/meta-llama/Meta-Llama-3.1-8B")
GEMMA_URI = os.environ.get("GEMMA_URI", "https://huggingface.co/google/gemma-2-9b")
