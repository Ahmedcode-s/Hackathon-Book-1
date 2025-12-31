"""
Vector storage module for the RAG ingestion pipeline.
Manages storage and retrieval of embedding vectors with idempotent operations.
"""

import logging
from typing import List
from ..models import EmbeddingVector
from .qdrant_client import QdrantStorageClient


logger = logging.getLogger(__name__)


class VectorStorage:
    """
    Class to manage vector storage operations with idempotent behavior.
    """

    def __init__(self, qdrant_client: QdrantStorageClient):
        """
        Initialize the vector storage manager.

        Args:
            qdrant_client: An instance of QdrantStorageClient
        """
        self.qdrant_client = qdrant_client

    def store_vectors_idempotent(self, collection_name: str, embedding_vectors: List[EmbeddingVector]) -> bool:
        """
        Store embedding vectors with idempotent behavior - avoid duplicates for unchanged content.

        Args:
            collection_name: Name of the collection to store vectors in
            embedding_vectors: List of EmbeddingVector objects to store

        Returns:
            True if vectors were stored successfully, False otherwise
        """
        if not embedding_vectors:
            logger.warning("No embedding vectors to store")
            return True

        # Create the collection if it doesn't exist
        if not self.qdrant_client.create_collection(collection_name):
            logger.error(f"Failed to create or access collection '{collection_name}'")
            return False

        # Filter out vectors that already exist in the collection
        vectors_to_store = []
        skipped_count = 0

        for embedding_vector in embedding_vectors:
            # Check if this vector ID already exists in the collection
            if not self.qdrant_client.vector_exists(collection_name, embedding_vector.vector_id):
                vectors_to_store.append(embedding_vector)
            else:
                logger.debug(f"Vector {embedding_vector.vector_id} already exists, skipping...")
                skipped_count += 1

        logger.info(f"Found {len(embedding_vectors)} vectors, {skipped_count} already exist, {len(vectors_to_store)} to store")

        if not vectors_to_store:
            logger.info("No new vectors to store")
            return True

        # Store the new vectors
        success = self.qdrant_client.store_vectors(collection_name, vectors_to_store)

        if success:
            logger.info(f"Successfully stored {len(vectors_to_store)} new vectors in collection '{collection_name}'")
            return True
        else:
            logger.error("Failed to store vectors in Qdrant")
            return False

    def store_single_vector_idempotent(self, collection_name: str, embedding_vector: EmbeddingVector) -> bool:
        """
        Store a single embedding vector with idempotent behavior.

        Args:
            collection_name: Name of the collection to store vector in
            embedding_vector: EmbeddingVector object to store

        Returns:
            True if vector was stored successfully, False otherwise
        """
        # Create the collection if it doesn't exist
        if not self.qdrant_client.create_collection(collection_name):
            logger.error(f"Failed to create or access collection '{collection_name}'")
            return False

        # Check if this vector ID already exists in the collection
        if self.qdrant_client.vector_exists(collection_name, embedding_vector.vector_id):
            logger.debug(f"Vector {embedding_vector.vector_id} already exists, skipping...")
            return True

        # Store the vector
        success = self.qdrant_client.store_vector(collection_name, embedding_vector)

        if success:
            logger.info(f"Successfully stored vector {embedding_vector.vector_id} in collection '{collection_name}'")
            return True
        else:
            logger.error(f"Failed to store vector {embedding_vector.vector_id} in Qdrant")
            return False

    def get_vector_count(self, collection_name: str) -> int:
        """
        Get the count of vectors in a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Number of vectors in the collection
        """
        return self.qdrant_client.get_vector_count(collection_name)

    def search_similar_vectors(self, collection_name: str, query_vector: List[float], limit: int = 10) -> List[dict]:
        """
        Search for similar vectors in the collection.

        Args:
            collection_name: Name of the collection to search in
            query_vector: Vector to search for similar vectors to
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of dictionaries containing search results
        """
        return self.qdrant_client.search_vectors(collection_name, query_vector, limit)


def create_vector_storage(qdrant_client: QdrantStorageClient) -> VectorStorage:
    """
    Convenience function to create a vector storage manager.

    Args:
        qdrant_client: An instance of QdrantStorageClient

    Returns:
        VectorStorage instance
    """
    return VectorStorage(qdrant_client)