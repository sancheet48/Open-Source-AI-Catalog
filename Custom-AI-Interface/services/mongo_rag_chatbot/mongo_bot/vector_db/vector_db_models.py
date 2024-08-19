"""Embedding function to be used for the vector database."""
from chromadb.utils import embedding_functions


EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)
