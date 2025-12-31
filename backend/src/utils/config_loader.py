"""
Configuration loader module for the RAG ingestion pipeline.
Handles loading environment variables and configuration settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Configuration class to manage environment variables and settings.
    """

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Cohere configuration
        self.cohere_api_key: Optional[str] = os.getenv("COHERE_API_KEY")

        # Qdrant configuration
        self.qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
        self.qdrant_url: Optional[str] = os.getenv("QDRANT_URL")

        # Processing configuration
        self.default_chunk_size: int = int(os.getenv("DEFAULT_CHUNK_SIZE", "1000"))
        self.default_chunk_overlap: int = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "200"))

        # Validation
        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validate that required configuration values are present.
        """
        missing_vars = []

        if not self.cohere_api_key:
            missing_vars.append("COHERE_API_KEY")

        if not self.qdrant_api_key:
            missing_vars.append("QDRANT_API_KEY")

        if not self.qdrant_url:
            missing_vars.append("QDRANT_URL")

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Global configuration instance
config = Config()