"""Download LLM from hugging face repository."""
# pylint: disable=no-name-in-module
from langchain_community.llms import CTransformers
from mongo_bot import const




config = {"temperature": 0.1, "context_length": 8192}
LLM_MODEL = CTransformers(
    model="TheBloke/neural-chat-7B-v3-1-GGUF",
    model_file="neural-chat-7b-v3-1.Q4_K_M.gguf",
    config=config,
    gpu_layers=const.GPU_LAYERS,
)
