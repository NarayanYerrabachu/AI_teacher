# ==================== config.py ====================
"""Configuration settings for the document processor"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from current directory
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration"""

    # Optional: Only needed if using OpenAI embeddings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Embedding configuration
    USE_OPENAI_EMBEDDINGS = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Chunking configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Search configuration
    DEFAULT_SEARCH_K = int(os.getenv("DEFAULT_SEARCH_K", "4"))

    # LLM configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))

    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if cls.USE_OPENAI_EMBEDDINGS and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found but USE_OPENAI_EMBEDDINGS is true. "
                "Please set it in your .env file or set USE_OPENAI_EMBEDDINGS=false"
            )
        if not cls.OPENAI_API_KEY and cls.LLM_MODEL.startswith("gpt"):
            raise ValueError(
                "OPENAI_API_KEY not found but LLM_MODEL is set to OpenAI model. "
                "Please set OPENAI_API_KEY in your .env file"
            )


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)