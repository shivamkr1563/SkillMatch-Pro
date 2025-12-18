"""Configuration settings for the SHL Assessment Recommender"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Gemini API
    gemini_api_key: str = ""
    llm_model: str = "gemini-pro"
    
    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Database
    chroma_persist_dir: str = "./data/chroma_db"
    
    # Recommendation Settings
    max_recommendations: int = 10
    min_recommendations: int = 5
    similarity_threshold: float = 0.3
    
    # Scraping
    shl_catalog_url: str = "https://www.shl.com/solutions/products/product-catalog/"
    headless_browser: bool = True
    
    # Paths
    data_dir: Path = Path("data")
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
