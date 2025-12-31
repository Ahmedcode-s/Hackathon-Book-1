"""
Embedding generator module for the RAG ingestion pipeline.
Converts text chunks to embedding vectors using Cohere models.
"""

import logging
from typing import List
from ..models import TextChunk, EmbeddingVector
from .cohere_client import CohereClient


logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Class to generate embeddings from text chunks.
    """

    def __init__(self, cohere_client: CohereClient):
        """
        Initialize the embedding generator.

        Args:
            cohere_client: An instance of CohereClient
        """
        self.cohere_client = cohere_client

    def generate_embeddings_from_chunks(self, text_chunks: List[TextChunk]) -> List[EmbeddingVector]:
        """
        Generate embedding vectors from a list of text chunks.

        Args:
            text_chunks: List of TextChunk objects to convert to embeddings

        Returns:
            List of EmbeddingVector objects
        """
        if not text_chunks:
            return []

        # Extract text content from chunks
        texts = [chunk.content for chunk in text_chunks]

        logger.info(f"Generating embeddings for {len(texts)} text chunks")

        # Generate embeddings using Cohere
        embeddings = self.cohere_client.generate_embeddings(texts)

        # Create EmbeddingVector objects
        embedding_vectors = []
        for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
            # Create metadata dictionary
            metadata = {
                'source_url': chunk.source_url,
                'page_title': chunk.page_title,
                'section_heading': chunk.section_heading,
                'chunk_index': str(chunk.chunk_index)
            }

            # Create the embedding vector
            embedding_vector = EmbeddingVector(
                vector_id=chunk.id,  # Use the chunk ID as the vector ID for consistency
                embedding=embedding,
                text_chunk_id=chunk.id,
                metadata=metadata
            )

            embedding_vectors.append(embedding_vector)

        logger.info(f"Successfully created {len(embedding_vectors)} embedding vectors")
        return embedding_vectors

    def generate_single_embedding(self, text_chunk: TextChunk) -> EmbeddingVector:
        """
        Generate a single embedding vector from a text chunk.

        Args:
            text_chunk: TextChunk object to convert to embedding

        Returns:
            EmbeddingVector object
        """
        embedding = self.cohere_client.generate_single_embedding(text_chunk.content)

        # Create metadata dictionary
        metadata = {
            'source_url': text_chunk.source_url,
            'page_title': text_chunk.page_title,
            'section_heading': text_chunk.section_heading,
            'chunk_index': str(text_chunk.chunk_index)
        }

        # Create the embedding vector
        embedding_vector = EmbeddingVector(
            vector_id=text_chunk.id,
            embedding=embedding,
            text_chunk_id=text_chunk.id,
            metadata=metadata
        )

        return embedding_vector


def create_embedding_generator(cohere_client: CohereClient) -> EmbeddingGenerator:
    """
    Convenience function to create an embedding generator.

    Args:
        cohere_client: An instance of CohereClient

    Returns:
        EmbeddingGenerator instance
    """
    return EmbeddingGenerator(cohere_client)