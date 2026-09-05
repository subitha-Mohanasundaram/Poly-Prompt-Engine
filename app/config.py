"""
Configuration management using pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings for Poly Prompt Engine.
    """
    app_name: str = 'Poly Prompt Engine'
    ollama_base_url: str = 'http://localhost:11434'
    ollama_model: str = 'qwen2.5:7b'
    embedding_model: str = 'all-MiniLM-L6-v2'
    max_variations: int = 60
    duplicate_similarity_threshold: float = 0.85
    low_confidence_threshold: float = 0.6
    generation_timeout_seconds: int = 300
    batch_size: int = 10
    max_retries: int = 3
    log_level: str = 'INFO'

    model_config = SettingsConfigDict(env_file='.env', env_prefix='')

@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings as a singleton instance.
    """
    return Settings()
