"""Constants defined module."""

import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
LOG_FILE = os.path.join(LOG_DIR, "custom_chatbot.log")
os.makedirs(LOG_DIR, exist_ok=True)

# ---------------- MongoDB Parameters ----------------
GENERIC_CHATBOT_URI = os.environ.get("GENERIC_CHATBOT_URI", "")
RAG_CHATBOT_URI = os.environ.get("RAG_CHATBOT_URI", "")
