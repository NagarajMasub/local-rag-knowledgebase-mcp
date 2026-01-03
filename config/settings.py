import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application settings loaded from environment variables"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(DATA_DIR / "chroma_db"))
    UPLOAD_DOCS_PATH = os.getenv("UPLOAD_DOCS_PATH", str(DATA_DIR / "uploaded_docs"))
    
    # Models
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt2")
    LLM_SOURCE = os.getenv("LLM_SOURCE", "transformers")  # Options: "transformers", "ollama"
    
    # Note: LangSmith integration removed for public release
    
    # Security
    CONFIDENTIAL_MODE = os.getenv("CONFIDENTIAL_MODE", "true").lower() == "true"
    
    # Supported file types
    SUPPORTED_FILE_TYPES = {
        "docx": ".docx",
        "pptx": ".pptx",
        "pdf": ".pdf",
        "txt": ".txt"
    }
    
    # Chunking settings
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # Vector store settings
    VECTOR_STORE_COLLECTION = "knowledge_base"
    
    @classmethod
    def validate(cls):
        """Validate critical settings"""
        os.makedirs(cls.CHROMA_DB_PATH, exist_ok=True)
        os.makedirs(cls.UPLOAD_DOCS_PATH, exist_ok=True)

settings = Settings()
