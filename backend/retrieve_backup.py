#!/usr/bin/env python3
"""
RAG Retrieval Pipeline for Book Content

This module provides functionality to retrieve relevant text chunks from a Qdrant Cloud
collection based on semantic similarity to a natural language query. It uses the
all-MiniLM-L6-v2 model for generating query embeddings and performs top-k similarity
search against stored book embeddings.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import argparse

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


@dataclass
class RetrievedChunk:
    """
    Represents a retrieved text chunk with metadata.

    Attributes:
        text: Text content of the chunk
        source_url: URL where the content was sourced from
        position: Position of the chunk in the original document
        score: Similarity score (0.0-1.0)
        chunk_id: Unique identifier for the chunk
        created_at: Timestamp when the chunk was indexed
    """
    text: str
    source_url: str
    position: int
    score: float
    chunk_id: str
    created_at: float


class RAGRetriever:
    """
    RAG retrieval system that performs semantic search against stored book embeddings.
    """

    def __init__(self):
        """
        Initialize the RAG retriever with model and Qdrant client.
        """
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Load the embedding model
        self.logger.info("Loading all-MiniLM-L6-v2 embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.logger.info("Embedding model loaded successfully")

        # Get Qdrant configuration from environment
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

        self.logger.info(f"Connected to Qdrant collection: {self.collection_name}")

    def generate_query_embedding(self, query_text: str) -> List[float]:
        """
        Generate embedding vector for the input query text.

        Args:
            query_text: Natural language query text

        Returns:
            Embedding vector as a list of floats
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        self.logger.info(f"Generating embedding for query: {query_text[:50]}...")
        embedding = self.model.encode([query_text])
        return embedding[0].tolist()  # Convert to list for Qdrant compatibility

    def retrieve_chunks(
        self,
        query_text: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant text chunks from Qdrant based on semantic similarity
        to the input query.

        Args:
            query_text: Natural language query
            top_k: Number of results to return (default 5)
            min_score: Minimum similarity threshold (default 0.0)

        Returns:
            List of retrieved chunks with metadata, sorted by similarity score descending
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        if not (0.0 <= min_score <= 1.0):
            raise ValueError("min_score must be between 0.0 and 1.0")

        # Generate query embedding
        query_embedding = self.generate_query_embedding(query_text)

        # Perform search in Qdrant
        self.logger.info(f"Searching for top {top_k} similar chunks...")
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

        self.logger.info(f"Retrieved {len(retrieved_chunks)} chunks")
        return retrieved_chunks

    def validate_retrieval(
        self,
        query_text: str,
        expected_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate retrieval results for semantic relevance and metadata integrity.

        Args:
            query_text: Natural language query for validation
            expected_sources: Optional list of expected source URLs for validation

        Returns:
            Validation results including metrics and quality indicators
        """
        # Retrieve chunks for validation
        results = self.retrieve_chunks(query_text, top_k=5)

        # Calculate validation metrics
        retrieved_count = len(results)
        semantic_relevance_score = sum([chunk.score for chunk in results]) / len(results) if results else 0.0
        metadata_integrity = all([
            chunk.text and chunk.source_url and chunk.chunk_id
            for chunk in results
        ])

        # Check if expected sources are present (if provided)
        sources_found = 0
        if expected_sources:
            sources_found = sum(1 for chunk in results
                              if any(expected in chunk.source_url for expected in expected_sources))

        validation_result = {
            "query": query_text,
            "retrieved_count": retrieved_count,
            "semantic_relevance_score": semantic_relevance_score,
            "metadata_integrity": metadata_integrity,
            "expected_sources_found": sources_found,
            "expected_sources_count": len(expected_sources) if expected_sources else 0,
            "results": [
                {
                    "text": chunk.text,
                    "source_url": chunk.source_url,
                    "position": chunk.position,
                    "score": chunk.score,
                    "chunk_id": chunk.chunk_id,
                    "created_at": chunk.created_at
                }
                for chunk in results
            ]
        }

        return validation_result

    def close(self):
        """
        Close the Qdrant client connection.
        """
        if hasattr(self, 'client'):
            self.client.close()
            self.logger.info("Qdrant client connection closed")


def main():
    """
    Main function to run the retrieval pipeline from command line.
    """
    parser = argparse.ArgumentParser(description="RAG Retrieval Pipeline for Book Content")
    parser.add_argument("--query", type=str, required=True, help="Natural language query text")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return (default: 5)")
    parser.add_argument("--min-score", type=float, default=0.0, help="Minimum similarity threshold (default: 0.0)")
    parser.add_argument("--validate", action="store_true", help="Run validation instead of basic retrieval")
    parser.add_argument("--expected-sources", nargs="*", help="Expected source URLs for validation")

    args = parser.parse_args()

    retriever = None
    try:
        # Initialize the retriever
        retriever = RAGRetriever()

        if args.validate:
            # Run validation
            validation_result = retriever.validate_retrieval(
                args.query,
                args.expected_sources
            )

            print(f"Validation Results for Query: '{args.query}'")
            print(f"Retrieved Count: {validation_result['retrieved_count']}")
            print(f"Semantic Relevance Score: {validation_result['semantic_relevance_score']:.3f}")
            print(f"Metadata Integrity: {validation_result['metadata_integrity']}")
            print(f"Expected Sources Found: {validation_result['expected_sources_found']}/{validation_result['expected_sources_count']}")
            print("\nRetrieved Results:")

            for i, result in enumerate(validation_result['results'], 1):
                print(f"\n{i}. Score: {result['score']:.3f}")
                print(f"   Source: {result['source_url']}")
                print(f"   Position: {result['position']}")
                print(f"   Text Preview: {result['text'][:200]}...")
        else:
            # Run basic retrieval
            results = retriever.retrieve_chunks(
                args.query,
                top_k=args.top_k,
                min_score=args.min_score
            )

            print(f"Retrieved {len(results)} chunks for query: '{args.query}'")
            print("\nResults:")

            for i, chunk in enumerate(results, 1):
                print(f"\n{i}. Score: {chunk.score:.3f}")
                print(f"   Source: {chunk.source_url}")
                print(f"   Position: {chunk.position}")
                print(f"   Text Preview: {chunk.text[:200]}...")

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

    finally:
        if retriever:
            retriever.close()


if __name__ == "__main__":
    main()