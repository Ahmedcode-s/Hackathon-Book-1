"""
Qdrant-based retrieval tool for the RAG agent.
This tool wraps the existing retrieve.py functionality in an agent-compatible format.
"""
import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from models.agent_models import RetrievedContext, RetrievedChunk


class QdrantRetrievalTool:
    """
    Tool for retrieving semantically similar content from Qdrant.

    This tool integrates with the existing Qdrant collection containing book embeddings
    and provides retrieval functionality for the RAG agent.
    """

    def __init__(self):
        """
        Initialize the retrieval tool with Qdrant connection and embedding model.
        """
        # Load environment variables
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("COLLECTION_NAME", "book_embeddings")

        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in environment variables")

        # Connect to Qdrant
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=10
        )

        # Load the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def __call__(self, query: str, top_k: int = 5, min_score: float = 0.3) -> Dict[str, Any]:
        """
        Execute the retrieval tool to find relevant content based on the query.

        Args:
            query: Natural language query text
            top_k: Number of results to return (default 5)
            min_score: Minimum similarity threshold (default 0.3)

        Returns:
            Dictionary containing retrieved context with metadata
        """
        import time
        start_time = time.time()

        # Generate query embedding
        query_embedding = self.model.encode([query])[0].tolist()

        # Perform search in Qdrant
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
            score_threshold=min_score
        )

        # Convert results to RetrievedChunk objects
        retrieved_chunks = []
        for result in search_results.points:
            payload = result.payload
            chunk = RetrievedChunk(
                text=payload.get("text", ""),
                source_url=payload.get("source_url", ""),
                position=payload.get("position", 0),
                score=result.score,
                chunk_id=result.id,
                created_at=payload.get("created_at", 0.0)
            )
            retrieved_chunks.append(chunk)

        retrieval_time = time.time() - start_time

        # Create RetrievedContext object
        context = RetrievedContext(
            chunks=retrieved_chunks,
            query_embedding=query_embedding,
            retrieval_time=retrieval_time,
            total_chunks_found=len(retrieved_chunks)
        )

        return {
            "chunks": context.chunks,
            "retrieval_time": context.retrieval_time,
            "total_chunks_found": context.total_chunks_found
        }

    def validate_connection(self) -> bool:
        """
        Validate connection to Qdrant service.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            print(f"Connection validation failed: {str(e)}")
            return False