"""
ID generator module for the RAG ingestion pipeline.
Generates stable, deterministic IDs for text chunks based on content and metadata.
"""

import hashlib
import uuid
from typing import Optional
from urllib.parse import urlparse


def generate_chunk_id(
    content: str,
    source_url: str,
    page_title: str = "",
    section_heading: str = "",
    chunk_index: int = 0
) -> str:
    """
    Generate a stable, deterministic ID for a text chunk based on its content and metadata.

    The ID is generated using a hash of the content combined with metadata to ensure
    uniqueness while maintaining stability across pipeline runs.

    Args:
        content: The text content of the chunk
        source_url: The URL of the source page
        page_title: The title of the source page
        section_heading: The section heading of the content
        chunk_index: The sequential index of this chunk within the page

    Returns:
        A stable, deterministic ID for the chunk
    """
    # Create a string that combines content and metadata
    content_for_hash = f"{source_url}|{page_title}|{section_heading}|{chunk_index}|{content}"

    # Generate SHA-256 hash and use it to create a UUID
    hash_bytes = hashlib.sha256(content_for_hash.encode('utf-8')).digest()
    # Use first 16 bytes to create a UUID
    chunk_uuid = uuid.UUID(bytes=hash_bytes[:16])

    return str(chunk_uuid)


def generate_document_hash(content: str) -> str:
    """
    Generate a hash for document content to detect changes.

    Args:
        content: The content to hash

    Returns:
        A hash of the content
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def normalize_url(url: str) -> str:
    """
    Normalize a URL for consistent ID generation.

    Args:
        url: The URL to normalize

    Returns:
        A normalized version of the URL
    """
    parsed = urlparse(url)
    # Remove fragment and query parameters for consistent identification
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return normalized


def generate_page_id(url: str, title: str = "") -> str:
    """
    Generate a stable ID for a crawled page.

    Args:
        url: The URL of the page
        title: The title of the page

    Returns:
        A stable ID for the page
    """
    normalized_url = normalize_url(url)
    content_for_hash = f"{normalized_url}|{title}"
    hash_bytes = hashlib.sha256(content_for_hash.encode('utf-8')).digest()
    # Use first 16 bytes to create a UUID
    page_uuid = uuid.UUID(bytes=hash_bytes[:16])
    return str(page_uuid)