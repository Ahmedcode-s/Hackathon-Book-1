"""
Qdrant client module for the RAG ingestion pipeline.
Handles integration with Qdrant Cloud for vector storage.
"""

import logging
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..utils.config_loader import config
from ..models import EmbeddingVector


logger = logging.getLogger(__name__)


class QdrantStorageClient:
    """
    Class to handle Qdrant Cloud interactions for vector storage.
    """

    def __init__(self):
        """
        Initialize the Qdrant client with configuration from environment variables.
        """
        if not config.qdrant_api_key:
            raise ValueError("QDRANT_API_KEY environment variable is required")

        if not config.qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")

        try:
            self.client = QdrantClient(
                url=config.qdrant_url,
                api_key=config.qdrant_api_key,
                # Set timeout and retry settings for reliability
                timeout=30
            )
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {str(e)}")
            raise

    def create_collection(self, collection_name: str, vector_size: int = 1024) -> bool:
        """
        Create a collection in Qdrant if it doesn't exist.

        Args:
            collection_name: Name of the collection to create
            vector_size: Size of the vectors (default: 1024, adjust based on embedding model)

        Returns:
            True if collection was created or already exists, False otherwise
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            existing_collections = [col.name for col in collections.collections]

            if collection_name in existing_collections:
                logger.info(f"Collection '{collection_name}' already exists")
                return True

            # Create the collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE  # Cosine distance is good for embeddings
                )
            )

            logger.info(f"Successfully created collection '{collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error creating collection '{collection_name}': {str(e)}")
            return False

    def store_vectors(self, collection_name: str, embedding_vectors: List[EmbeddingVector], batch_size: int = 64) -> bool:
        """
        Store embedding vectors in Qdrant collection.

        Args:
            collection_name: Name of the collection to store vectors in
            embedding_vectors: List of EmbeddingVector objects to store
            batch_size: Number of vectors to store in each batch (default: 64)

        Returns:
            True if vectors were stored successfully, False otherwise
        """
        if not embedding_vectors:
            logger.warning("No embedding vectors to store")
            return True

        try:
            # Process in batches to respect API limits and improve performance
            for i in range(0, len(embedding_vectors), batch_size):
                batch = embedding_vectors[i:i + batch_size]

                # Prepare points for insertion
                points = []
                for embedding_vector in batch:
                    point = models.PointStruct(
                        id=embedding_vector.vector_id,
                        vector=embedding_vector.embedding,
                        payload=embedding_vector.metadata
                    )
                    points.append(point)

                # Upsert the batch of points
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )

                logger.debug(f"Stored batch {i//batch_size + 1} of vectors ({len(batch)} vectors)")

            logger.info(f"Successfully stored {len(embedding_vectors)} vectors in collection '{collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error storing vectors in collection '{collection_name}': {str(e)}")
            return False

    def store_vector(self, collection_name: str, embedding_vector: EmbeddingVector) -> bool:
        """
        Store a single embedding vector in Qdrant collection.

        Args:
            collection_name: Name of the collection to store vector in
            embedding_vector: EmbeddingVector object to store

        Returns:
            True if vector was stored successfully, False otherwise
        """
        try:
            point = models.PointStruct(
                id=embedding_vector.vector_id,
                vector=embedding_vector.embedding,
                payload=embedding_vector.metadata
            )

            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )

            logger.debug(f"Successfully stored vector '{embedding_vector.vector_id}' in collection '{collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error storing vector '{embedding_vector.vector_id}' in collection '{collection_name}': {str(e)}")
            return False

    def vector_exists(self, collection_name: str, vector_id: str) -> bool:
        """
        Check if a vector with the given ID exists in the collection.

        Args:
            collection_name: Name of the collection to check
            vector_id: ID of the vector to check for

        Returns:
            True if vector exists, False otherwise
        """
        try:
            # Try to retrieve the point by ID
            records = self.client.retrieve(
                collection_name=collection_name,
                ids=[vector_id]
            )

            return len(records) > 0

        except Exception as e:
            logger.warning(f"Error checking if vector '{vector_id}' exists in collection '{collection_name}': {str(e)}")
            return False

    def get_vector_count(self, collection_name: str) -> int:
        """
        Get the count of vectors in a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Number of vectors in the collection
        """
        try:
            count_result = self.client.count(
                collection_name=collection_name
            )
            return count_result.count

        except Exception as e:
            logger.error(f"Error getting vector count for collection '{collection_name}': {str(e)}")
            return 0

    def search_vectors(self, collection_name: str, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """
        Search for similar vectors in the collection.

        Args:
            collection_name: Name of the collection to search in
            query_vector: Vector to search for similar vectors to
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of dictionaries containing search results
        """
        try:
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )

            # Convert results to a more accessible format
            results = []
            for result in search_results:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload,
                    'vector': result.vector
                })

            return results

        except Exception as e:
            logger.error(f"Error searching vectors in collection '{collection_name}': {str(e)}")
            return []


def create_qdrant_client() -> QdrantStorageClient:
    """
    Convenience function to create a Qdrant storage client instance.

    Returns:
        QdrantStorageClient instance
    """
    return QdrantStorageClient()