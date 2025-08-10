import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv(override=True)

class Settings(BaseSettings):
    pinecone_dense_index_host: str
    pinecone_sparse_index_host: str
    pinecone_namespace: str
    pinecone_top_k: int
    pinecone_api_key: str
    # Optional LLM settings for gating memories
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    openai_model: str = "gpt-5-nano-2025-08-07"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()