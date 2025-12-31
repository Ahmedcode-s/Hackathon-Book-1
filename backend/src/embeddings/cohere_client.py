"""
Cohere client module for the RAG ingestion pipeline.
Handles integration with Cohere's embedding API.
"""

import cohere
import logging
from typing import List
from ..utils.config_loader import config


logger = logging.getLogger(__name__)


class CohereClient:
    """
    Class to handle Cohere API interactions for embedding generation.
    """

    def __init__(self):
        """
        Initialize the Cohere client with API key from configuration.
        """
        if not config.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(config.cohere_api_key)
        self.model = "embed-multilingual-v3.0"  # Using a robust multilingual model

    def generate_embeddings(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in each batch (default: 96, Cohere's max)

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []

        all_embeddings = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document"  # Optimize for search documents
                )

                batch_embeddings = response.embeddings
                all_embeddings.extend(batch_embeddings)

                logger.debug(f"Generated embeddings for batch {i//batch_size + 1}, size: {len(batch)}")

            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Re-raise the exception to handle it at a higher level
                raise

        logger.info(f"Successfully generated embeddings for {len(texts)} text chunks")
        return all_embeddings

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding for a text string.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector (list of floats)
        """
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_document"
            )

            # Return the first (and only) embedding
            return response.embeddings[0]

        except Exception as e:
            logger.error(f"Error generating embedding for text: {str(e)}")
            raise


def create_cohere_client() -> CohereClient:
    """
    Convenience function to create a Cohere client instance.

    Returns:
        CohereClient instance
    """
    return CohereClient()