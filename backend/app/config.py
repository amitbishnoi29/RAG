import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-35-turbo"
    azure_openai_embedding_deployment: str = "text-embedding-ada-002"
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Weaviate Configuration
    weaviate_url: str = "http://localhost:8080"
    
    # HeyGen Configuration
    heygen_api_key: str
    heygen_avatar_id: str = "default"
    heygen_voice_id: str = "default"
    
    # Application Configuration
    app_name: str = "RAG Chatbot"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS Configuration
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]
    # cors_origins: list = ["*"]
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf", ".txt", ".md", ".docx"]
    
    # Chunking Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # RAG Configuration
    max_retrieved_docs: int = 5
    temperature: float = 0.7
    max_tokens: int = 1000

    class Config:
        env_file = ".env"


settings = Settings() 