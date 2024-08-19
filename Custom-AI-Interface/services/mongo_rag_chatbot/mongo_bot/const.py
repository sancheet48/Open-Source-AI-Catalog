"""Constants defined module."""
import os
import socket


PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))


LLM_SCHEMA_PATH = os.path.join(PROJECT_DIR, "lib", "llm_schema.txt")
GPU_LAYERS = int(os.environ.get("GPU_LAYERS", 0))
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "")
# HOSTNAME = os.environ.get("HOSTNAME", socket.gethostname())


SERVICE_COM_TOKEN = os.environ.get("SERVICE_COM_TOKEN", "")