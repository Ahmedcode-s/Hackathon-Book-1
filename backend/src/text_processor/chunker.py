"""
Text chunker module for the RAG ingestion pipeline.
Implements deterministic text chunking with stable chunk IDs.
"""

import logging
from typing import List, Tuple
from ..models import TextChunk
from ..utils.id_generator import generate_chunk_id, generate_document_hash


logger = logging.getLogger(__name__)


class Chunker:
    """
    Class to perform deterministic text chunking with stable chunk IDs.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the chunker with chunk size and overlap parameters.

        Args:
            chunk_size: Maximum size of each chunk in characters (default: 1000)
            chunk_overlap: Number of overlapping characters between chunks (default: 200)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, source_url: str, page_title: str = "", section_heading: str = "") -> List[TextChunk]:
        """
        Chunk the text deterministically with stable IDs.

        Args:
            text: The text to chunk
            source_url: The URL of the source page
            page_title: The title of the source page
            section_heading: The section heading of the content

        Returns:
            A list of TextChunk objects
        """
        if not text:
            return []

        chunks = []
        text_length = len(text)
        start_idx = 0
        chunk_index = 0

        while start_idx < text_length:
            # Determine the end index for this chunk
            end_idx = start_idx + self.chunk_size

            # If this is not the last chunk, try to break at a sentence or word boundary
            if end_idx < text_length:
                # Look for a good breaking point within the overlap region
                search_start = end_idx - self.chunk_overlap
                breaking_point = end_idx

                # Look for sentence endings first
                for i in range(min(end_idx, text_length) - 1, max(search_start, start_idx), -1):
                    if text[i] in '.!?':
                        breaking_point = i + 1
                        break
                else:
                    # If no sentence ending found, look for word boundaries
                    for i in range(min(end_idx, text_length) - 1, max(search_start, start_idx), -1):
                        if text[i] in ' \t\n':
                            breaking_point = i + 1
                            break

                end_idx = breaking_point

            # Extract the chunk
            chunk_content = text[start_idx:end_idx].strip()

            # Only create a chunk if it has content
            if chunk_content:
                # Generate a stable chunk ID based on content and metadata
                chunk_id = generate_chunk_id(
                    content=chunk_content,
                    source_url=source_url,
                    page_title=page_title,
                    section_heading=section_heading,
                    chunk_index=chunk_index
                )

                # Generate content hash for duplicate detection
                content_hash = generate_document_hash(chunk_content)

                text_chunk = TextChunk(
                    id=chunk_id,
                    content=chunk_content,
                    source_url=source_url,
                    page_title=page_title,
                    section_heading=section_heading,
                    chunk_index=chunk_index,
                    hash=content_hash
                )

                chunks.append(text_chunk)
                chunk_index += 1

            # Move to the next chunk position
            start_idx = end_idx

            # Handle the case where we might get stuck (shouldn't happen with proper logic)
            if start_idx == 0:  # If we didn't advance, move by chunk_size anyway
                start_idx = min(start_idx + self.chunk_size, text_length)

        logger.debug(f"Chunked text into {len(chunks)} chunks")
        return chunks

    def chunk_text_with_structural_awareness(
        self,
        text: str,
        source_url: str,
        page_title: str = "",
        section_heading: str = "",
        structural_breaks: List[int] = None
    ) -> List[TextChunk]:
        """
        Chunk text while being aware of structural breaks (like section boundaries).

        Args:
            text: The text to chunk
            source_url: The URL of the source page
            page_title: The title of the source page
            section_heading: The section heading of the content
            structural_breaks: List of character positions where structural breaks occur

        Returns:
            A list of TextChunk objects
        """
        if not text:
            return []

        if not structural_breaks:
            return self.chunk_text(text, source_url, page_title, section_heading)

        # Sort structural breaks to ensure they're in order
        structural_breaks = sorted(set(structural_breaks))

        chunks = []
        start_idx = 0
        chunk_index = 0

        for break_point in structural_breaks:
            if start_idx >= len(text):
                break

            # Get the text segment between the current start and the structural break
            segment = text[start_idx:break_point].strip()

            if segment:
                # Chunk this segment if it's larger than our chunk size
                if len(segment) > self.chunk_size:
                    segment_chunks = self.chunk_text(
                        segment,
                        source_url,
                        page_title,
                        section_heading
                    )
                    # Update the chunk_index for these chunks
                    for chunk in segment_chunks:
                        chunk.chunk_index = chunk_index
                        # Regenerate ID with the new chunk index
                        chunk.id = generate_chunk_id(
                            content=chunk.content,
                            source_url=source_url,
                            page_title=page_title,
                            section_heading=section_heading,
                            chunk_index=chunk_index
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                else:
                    # Create a single chunk for this segment
                    chunk_id = generate_chunk_id(
                        content=segment,
                        source_url=source_url,
                        page_title=page_title,
                        section_heading=section_heading,
                        chunk_index=chunk_index
                    )

                    content_hash = generate_document_hash(segment)

                    text_chunk = TextChunk(
                        id=chunk_id,
                        content=segment,
                        source_url=source_url,
                        page_title=page_title,
                        section_heading=section_heading,
                        chunk_index=chunk_index,
                        hash=content_hash
                    )

                    chunks.append(text_chunk)
                    chunk_index += 1

            start_idx = break_point

        # Handle any remaining text after the last structural break
        if start_idx < len(text):
            remaining_text = text[start_idx:].strip()
            if remaining_text:
                remaining_chunks = self.chunk_text(
                    remaining_text,
                    source_url,
                    page_title,
                    section_heading
                )
                # Update chunk indices for remaining chunks
                for chunk in remaining_chunks:
                    chunk.chunk_index = chunk_index
                    # Regenerate ID with the new chunk index
                    chunk.id = generate_chunk_id(
                        content=chunk.content,
                        source_url=source_url,
                        page_title=page_title,
                        section_heading=section_heading,
                        chunk_index=chunk_index
                    )
                    chunks.append(chunk)
                    chunk_index += 1

        logger.debug(f"Structurally-aware chunked text into {len(chunks)} chunks")
        return chunks


def chunk_text(text: str, source_url: str, page_title: str = "", section_heading: str = "", chunk_size: int = 1000, chunk_overlap: int = 200) -> List[TextChunk]:
    """
    Convenience function to chunk text with stable IDs.

    Args:
        text: The text to chunk
        source_url: The URL of the source page
        page_title: The title of the source page
        section_heading: The section heading of the content
        chunk_size: Maximum size of each chunk in characters (default: 1000)
        chunk_overlap: Number of overlapping characters between chunks (default: 200)

    Returns:
        A list of TextChunk objects
    """
    chunker = Chunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_text(text, source_url, page_title, section_heading)