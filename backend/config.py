# backend/config.py - Updated for production
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # API Settings
    api_title: str = "AskHerCare API"
    api_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # CORS Settings - Updated for production
    allowed_origins: list = [
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://*.vercel.app",
        "https://*.railway.app",
        "https://*.render.com"
    ]
    
    # OpenAI Settings
    openai_api_key: str = ""
    
    # Security Settings
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Server Settings
    port: int = 8000
    host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()




# from pydantic_settings import BaseSettings
# from functools import lru_cache
# import os

# class Settings(BaseSettings):
#     # API Settings
#     api_title: str = "AskHerCare API"
#     api_version: str = "1.0.0"
#     debug: bool = False
    
#     # CORS Settings
#     allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
#     # RAG Settings
#     embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
#     llm_model: str = "llama3.1"
#     chunk_size: int = 512
#     chunk_overlap: int = 50
#     similarity_top_k: int = 5
    
#     # Vector Store Settings
#     chroma_db_path: str = "./data/chroma_db"
#     dataset_path: str = "./data/medical_qa_dataset.json"
    
#     # Security Settings
#     rate_limit_requests: int = 100
#     rate_limit_window: int = 3600  # 1 hour
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False

# @lru_cache()
# def get_settings() -> Settings:
#     return Settings()