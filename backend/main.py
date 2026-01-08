#!/usr/bin/env python3
"""
RAG Ingestion Pipeline for Docusaurus-based Book Content

This script implements a pipeline that:
1. Crawls Docusaurus-based book websites
2. Extracts meaningful textual content
3. Chunks text with consistent size and overlap
4. Generates embeddings using all-MiniLM-L6-v2
5. Stores embeddings and metadata in Qdrant Cloud
"""

import argparse
import asyncio
import json
import logging
import os
import re
import time
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse, urljoin
from dataclasses import dataclass
import urllib.robotparser

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

# Global variable to store the model (loaded once for efficiency)
_embedding_model = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a segment of text extracted from a web page."""
    text: str
    source_url: str
    position: int
    chunk_id: str


@dataclass
class SourceMetadata:
    """Information about the origin of content."""
    url: str
    page_title: str
    crawl_timestamp: float
    document_structure: dict


@dataclass
class ProcessingConfig:
    """Parameters that control the ingestion pipeline."""
    chunk_size: int = 512
    chunk_overlap: int = 128
    rate_limit_delay: float = 1.0  # seconds between requests
    max_pages: int = 1000  # maximum pages to crawl per site


def load_environment_variables():
    """Load configuration from environment variables."""
    load_dotenv()

    config = {
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
        'qdrant_url': os.getenv('QDRANT_URL'),
        'collection_name': os.getenv('QDRANT_COLLECTION_NAME', 'book_embeddings'),
        'website_url': os.getenv('DEPLOYED_VERCEL_URL')  # Changed to match the .env file
    }

    if not config['qdrant_api_key'] or not config['qdrant_url']:
        logger.warning("Qdrant configuration not found in environment variables. "
                      "Please set QDRANT_API_KEY and QDRANT_URL.")

    return config


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")

            raise last_exception
        return wrapper
    return decorator


def error_handler(func):
    """Decorator to handle errors in functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper


@error_handler
def get_urls_from_sitemap(website_url: str) -> List[str]:
    """
    Extract URLs from a website's sitemap.xml file.

    Args:
        website_url: Base URL of the website

    Returns:
        List of URLs extracted from sitemap.xml
    """
    sitemap_url = f"{website_url.rstrip('/')}/sitemap.xml"
    logger.info(f"Fetching sitemap from: {sitemap_url}")

    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()

        # Try to parse the sitemap XML with lxml parser if available, otherwise use xml
        try:
            from lxml import etree
            # Parse with lxml if available
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(response.content, parser)

            # Find all loc elements (URLs) in the sitemap
            urls = []
            for elem in root.iter():
                if elem.tag.endswith('loc'):  # Handle namespaces
                    urls.append(elem.text.strip())
        except ImportError:
            # If lxml is not available, try using BeautifulSoup with xml parser
            # First, try to install xml parser by mentioning it
            try:
                soup = BeautifulSoup(response.content, 'xml')
            except:
                # If xml parser is not available, fall back to html parser
                logger.warning("XML parser not available, falling back to HTML parser for sitemap")
                soup = BeautifulSoup(response.content, 'html.parser')

            # Find all <url><loc> elements in the sitemap
            loc_elements = soup.find_all('loc')
            urls = [loc.get_text().strip() for loc in loc_elements if loc]

        logger.info(f"Found {len(urls)} URLs in sitemap")

        # If no URLs found, try alternative sitemap patterns
        if not urls:
            # Some sites use sitemap_index.xml or have sitemaps in subdirectories
            alternative_sitemaps = [
                f"{website_url.rstrip('/')}/sitemap_index.xml",
                f"{website_url.rstrip('/')}/sitemap-index.xml",
                f"{website_url.rstrip('/')}/wp-sitemap.xml",  # WordPress
            ]

            for alt_sitemap in alternative_sitemaps:
                try:
                    logger.info(f"Trying alternative sitemap: {alt_sitemap}")
                    alt_response = requests.get(alt_sitemap, timeout=10)
                    alt_response.raise_for_status()

                    try:
                        from lxml import etree
                        parser = etree.XMLParser(recover=True)
                        root = etree.fromstring(alt_response.content, parser)

                        alt_urls = []
                        for elem in root.iter():
                            if elem.tag.endswith('loc'):
                                alt_urls.append(elem.text.strip())
                    except ImportError:
                        try:
                            alt_soup = BeautifulSoup(alt_response.content, 'xml')
                        except:
                            alt_soup = BeautifulSoup(alt_response.content, 'html.parser')

                        alt_loc_elements = alt_soup.find_all('loc')
                        alt_urls = [loc.get_text().strip() for loc in alt_loc_elements if loc]

                    if alt_urls:
                        urls = alt_urls
                        logger.info(f"Found {len(urls)} URLs in alternative sitemap: {alt_sitemap}")
                        break
                except requests.RequestException:
                    continue

        return urls

    except requests.RequestException as e:
        logger.warning(f"Could not fetch sitemap from {sitemap_url}: {str(e)}")
        logger.info("Proceeding with the base website URL only")
        return [website_url]
    except Exception as e:
        logger.warning(f"Error parsing sitemap: {str(e)}")
        logger.info("Proceeding with the base website URL only")
        return [website_url]


@error_handler
def get_qdrant_client():
    """
    Create and return a Qdrant client connection.

    Returns:
        QdrantClient instance
    """
    config = load_environment_variables()

    if not config['qdrant_api_key'] or not config['qdrant_url']:
        raise ValueError("Qdrant configuration not provided in environment variables")

    client = QdrantClient(
        url=config['qdrant_url'],
        api_key=config['qdrant_api_key'],
        prefer_grpc=False  # Use HTTP for better compatibility
    )

    return client


@error_handler
def ensure_collection_exists(collection_name: str, vector_size: int = 384):
    """
    Ensure the Qdrant collection exists with the proper schema.

    Args:
        collection_name: Name of the collection to create/check
        vector_size: Size of the embedding vectors (all-MiniLM-L6-v2 produces 384-dim vectors)
    """
    client = get_qdrant_client()

    try:
        # Check if collection already exists
        client.get_collection(collection_name)
        logger.info(f"Collection '{collection_name}' already exists")
    except:
        # Collection doesn't exist, create it
        logger.info(f"Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        )
        logger.info(f"Collection '{collection_name}' created successfully")


@error_handler
def store_in_qdrant(embedding_results: List[Tuple[DocumentChunk, List[float]]], collection_name: str):
    """
    Store embedding vectors and metadata in Qdrant Cloud.

    Args:
        embedding_results: List of tuples containing (DocumentChunk, embedding_vector)
        collection_name: Name of the Qdrant collection to store in
    """
    if not embedding_results:
        logger.info("No embedding results to store")
        return

    logger.info(f"Storing {len(embedding_results)} embeddings in Qdrant collection '{collection_name}'...")

    # Ensure the collection exists
    ensure_collection_exists(collection_name)

    client = get_qdrant_client()

    # Prepare points for insertion
    points = []
    for idx, (doc_chunk, embedding_vector) in enumerate(embedding_results):
        point = models.PointStruct(
            id=abs(hash(doc_chunk.chunk_id)) % 1000000000,  # Convert to numeric ID for Qdrant compatibility
            vector=embedding_vector,
            payload={
                "text": doc_chunk.text,
                "source_url": doc_chunk.source_url,
                "position": doc_chunk.position,
                "chunk_id": doc_chunk.chunk_id,  # Store original chunk ID in payload
                "created_at": time.time()
            }
        )
        points.append(point)

    # Insert points into the collection
    try:
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        logger.info(f"Successfully stored {len(points)} embeddings in Qdrant")
    except Exception as e:
        logger.error(f"Failed to store embeddings in Qdrant: {str(e)}")
        raise


def validate_url(url: str) -> bool:
    """Validate if a URL is properly formatted and safe to use."""
    try:
        parsed = urlparse(url)
        # Basic validation - only http/https allowed
        if parsed.scheme not in ['http', 'https']:
            return False

        # Prevent SSRF attacks by disallowing certain patterns
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False

        # Check for suspicious patterns in URL
        suspicious_patterns = [
            r'127\.0\.0\.1',
            r'localhost',
            r'internal',
            r'private',
            r'\.\.',  # Directory traversal
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True
    except Exception:
        return False


def sanitize_content(content: str) -> str:
    """
    Sanitize content to prevent injection attacks.

    Args:
        content: Raw content to sanitize

    Returns:
        Sanitized content
    """
    if not content:
        return content

    # Remove potentially dangerous characters/sequences
    # This is a basic sanitization - for production, consider more thorough sanitization
    sanitized = content.replace('\0', '')  # Remove null bytes
    return sanitized


def setup_logging():
    """Create and configure logging for the application."""
    # Already configured at module level
    pass


def load_embedding_model():
    """
    Load the all-MiniLM-L6-v2 model for generating embeddings.
    The model is loaded once and cached globally for efficiency.
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading all-MiniLM-L6-v2 embedding model...")
        try:
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    return _embedding_model


@error_handler
def generate_embeddings(chunks: List[DocumentChunk]) -> List[Tuple[DocumentChunk, List[float]]]:
    """
    Generate embeddings for a list of document chunks using the loaded model.

    Args:
        chunks: List of DocumentChunk objects

    Returns:
        List of tuples containing (DocumentChunk, embedding_vector)
    """
    if not chunks:
        return []

    logger.info(f"Generating embeddings for {len(chunks)} chunks...")

    # Load the embedding model
    model = load_embedding_model()

    # Extract text content from chunks
    texts = [chunk.text for chunk in chunks]

    # Generate embeddings (batch processing)
    embeddings = model.encode(texts)

    # Convert embeddings to lists (required for JSON serialization)
    embedding_vectors = [embedding.tolist() for embedding in embeddings]

    # Pair each chunk with its corresponding embedding
    result = [(chunk, emb_vec) for chunk, emb_vec in zip(chunks, embedding_vectors)]

    logger.info(f"Successfully generated embeddings for {len(result)} chunks")
    return result


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")

            raise last_exception
        return wrapper
    return decorator


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace, normalizing line breaks, etc.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple consecutive newlines with a single newline
    text = re.sub(r'\n\s*\n', '\n', text)

    return text


def extract_content(html_content: str) -> str:
    """
    Extract meaningful content from HTML, removing non-content elements.

    Args:
        html_content: Raw HTML content

    Returns:
        Clean text content
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove navigation, footer, scripts, and other non-content elements
    for element in soup.find_all(['nav', 'footer', 'script', 'style', 'aside', 'header']):
        element.decompose()

    # Extract content using Docusaurus-specific selectors
    content_selectors = [
        '[class*="docItemContainer"]',  # Docusaurus v2+ documentation container
        '[class*="container"]',  # General container
        '[role="main"]',  # Main content area
        'article',  # Article content
        '[class*="theme"]',  # Theme-specific content
        'main',  # Main element
        '[class*="doc"]',  # Documentation classes
        '[class*="markdown"]',  # Markdown content
        '[class*="content"]',  # Content classes
        '[class*="docs-"]',  # Docusaurus-specific classes
        '[class*="docitem"]',  # Another Docusaurus pattern
    ]

    content_element = None
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element is not None:
            break

    if content_element is None:
        # Fallback to body content
        content_element = soup.find('body')

    if content_element:
        # Further clean the content element
        for element in content_element.find_all(['nav', 'footer', 'script', 'style', 'aside', 'header']):
            element.decompose()

        # Extract text content
        content_text = content_element.get_text(separator=' ', strip=True)
        return content_text
    else:
        # If no specific content element found, extract from the whole document
        return soup.get_text(separator=' ', strip=True)


def chunk_text(text: str, source_url: str, chunk_size: int = 512, overlap: int = 128) -> List[DocumentChunk]:
    """
    Split text into chunks with specified size and overlap.

    Args:
        text: Text to chunk
        source_url: Source URL for the text
        chunk_size: Size of each chunk (in characters)
        overlap: Overlap between chunks (in characters)

    Returns:
        List of DocumentChunk objects
    """
    if not text:
        return []

    # Clean the text first
    text = clean_text(text)

    chunks = []
    start = 0
    position = 0

    while start < len(text):
        # Determine the end position for this chunk
        end = start + chunk_size

        # If we're near the end of the text, adjust the end position
        if end > len(text):
            end = len(text)

        # Extract the chunk
        chunk_text = text[start:end]

        # Create a document chunk with proper metadata
        chunk = DocumentChunk(
            text=chunk_text,
            source_url=source_url,
            position=position,
            chunk_id=f"chunk_{hash(source_url) % 100000}_{position}"  # Use numeric ID based on hash
        )

        chunks.append(chunk)

        # Move to the next chunk position with overlap
        start = end - overlap if end < len(text) and overlap > 0 else end
        position += 1

    return chunks


def chunk_text_by_sentences(text: str, source_url: str, chunk_size: int = 512, overlap: int = 128) -> List[DocumentChunk]:
    """
    Split text into chunks by sentences to preserve semantic boundaries.

    Args:
        text: Text to chunk
        source_url: Source URL for the text
        chunk_size: Target size of each chunk (in characters)
        overlap: Overlap between chunks (in characters)

    Returns:
        List of DocumentChunk objects
    """
    if not text:
        return []

    # Clean the text first
    text = clean_text(text)

    # Split text into sentences
    import re
    sentence_endings = r'[.!?]+(?=\s|$)'
    sentences = re.split(sentence_endings, text)

    # Add back the punctuation that was removed
    sentence_matches = list(re.finditer(sentence_endings, text))
    if len(sentence_matches) > 0:
        # Reconstruct sentences with punctuation
        reconstructed_sentences = []
        last_end = 0
        for i, match in enumerate(sentence_matches):
            sentence = text[last_end:match.end()]
            reconstructed_sentences.append(sentence)
            last_end = match.end()
        if last_end < len(text):
            reconstructed_sentences.append(text[last_end:])
        sentences = reconstructed_sentences
    else:
        # If no sentence endings found, split by length
        sentences = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    chunks = []
    current_chunk = ""
    current_length = 0
    position = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        # If adding this sentence would exceed chunk size
        if current_length + sentence_length > chunk_size and current_chunk:
            # Save the current chunk
            chunk = DocumentChunk(
                text=current_chunk,
                source_url=source_url,
                position=position,
                chunk_id=f"chunk_{hash(source_url) % 100000}_{position}"
            )
            chunks.append(chunk)

            # Start a new chunk with overlap from the previous chunk
            if overlap > 0:
                # Find the overlap text from the end of the current chunk
                overlap_start = max(0, len(current_chunk) - overlap)
                current_chunk = current_chunk[overlap_start:] + sentence
            else:
                current_chunk = sentence
            current_length = len(current_chunk)
            position += 1
        else:
            # Add sentence to current chunk
            current_chunk += sentence
            current_length += sentence_length

    # Add the final chunk if it has content
    if current_chunk.strip():
        chunk = DocumentChunk(
            text=current_chunk,
            source_url=source_url,
            position=position,
            chunk_id=f"chunk_{hash(source_url) % 100000}_{position}"
        )
        chunks.append(chunk)

    return chunks


def check_robots_txt(base_url: str, path: str = "/") -> bool:
    """
    Check if a path is allowed by robots.txt.

    Args:
        base_url: Base URL of the site
        path: Path to check

    Returns:
        True if allowed, False if disallowed
    """
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(base_url, '/robots.txt'))
        rp.read()
        return rp.can_fetch('*', urljoin(base_url, path))
    except:
        # If robots.txt cannot be read, assume it's allowed
        logger.warning(f"Could not read robots.txt for {base_url}, assuming allowed")
        return True


@error_handler
def crawl_docusaurus_site(url: str, max_pages: int = 100) -> List[Tuple[str, str, str]]:
    """
    Crawl a Docusaurus-based site and extract page content.

    Args:
        url: Base URL of the Docusaurus site
        max_pages: Maximum number of pages to crawl

    Returns:
        List of tuples containing (url, title, content) for each page
    """
    if not validate_url(url):
        logger.error(f"Invalid URL: {url}")
        return []

    visited_urls = set()
    urls_to_visit = [url]
    results = []

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; RAG-Ingestion-Bot/1.0)'
    })

    # Check robots.txt for the base URL
    if not check_robots_txt(url):
        logger.warning(f"Robots.txt disallows crawling {url}")
        return []

    while urls_to_visit and len(results) < max_pages:
        current_url = urls_to_visit.pop(0)

        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)
        logger.info(f"Crawling: {current_url}")

        try:
            # Add rate limiting delay
            time.sleep(ProcessingConfig.rate_limit_delay)

            response = session.get(current_url, timeout=10)
            response.raise_for_status()

            # Extract title
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            page_title = title_tag.get_text().strip() if title_tag else "Untitled"

            # Extract content using the dedicated function
            content_text = extract_content(response.content)

            # Filter out very short content (likely just navigation fragments)
            if len(content_text) > 50:  # At least 50 characters
                results.append((current_url, page_title, content_text))

                # Find additional links to crawl
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(current_url, href)

                    # Only add URLs from the same domain that look like documentation pages
                    current_domain = urlparse(current_url).netloc
                    absolute_domain = urlparse(absolute_url).netloc

                    if (absolute_domain == current_domain and
                        absolute_url not in visited_urls and
                        absolute_url not in urls_to_visit and
                        not any(skip in absolute_url.lower() for skip in ['.pdf', '.jpg', '.png', '.zip', '.css', '.js'])):

                        # Check robots.txt compliance before adding
                        if check_robots_txt(url, urlparse(absolute_url).path):
                            # Check if it looks like a documentation page
                            path_parts = urlparse(absolute_url).path.split('/')
                            if len(path_parts) > 1:  # Not just the root
                                urls_to_visit.append(absolute_url)

        except requests.RequestException as e:
            logger.warning(f"Failed to crawl {current_url}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error crawling {current_url}: {str(e)}")
            continue

    logger.info(f"Crawled {len(results)} pages from {url}")
    return results


def main():
    """Main entry point function that orchestrates the entire pipeline."""
    parser = argparse.ArgumentParser(description='RAG Ingestion Pipeline for Docusaurus-based Book Content')
    parser.add_argument('--urls', nargs='+', help='List of URLs to crawl (optional, defaults to WEBSITE_URL from .env)')
    parser.add_argument('--chunk-size', type=int, default=512, help='Size of text chunks')
    parser.add_argument('--overlap', type=int, default=128, help='Overlap between chunks')
    parser.add_argument('--max-pages', type=int, default=1000, help='Maximum number of pages to crawl')

    args = parser.parse_args()

    # Load configuration
    config = load_environment_variables()

    # Get collection name from config
    collection_name = config['collection_name']

    # Determine URLs to process - either from command line or from environment variable
    if args.urls:
        urls_to_process = args.urls
        logger.info(f"Using URLs provided via command line: {urls_to_process}")
    elif config['website_url']:
        logger.info(f"Using website URL from environment variable: {config['website_url']}")

        # Get URLs from sitemap.xml
        sitemap_urls = get_urls_from_sitemap(config['website_url'])

        # Filter to only include URLs from the same domain as the original website
        original_domain = urlparse(config['website_url']).netloc
        filtered_urls = []
        for url in sitemap_urls:
            if urlparse(url).netloc == original_domain:
                filtered_urls.append(url)
            else:
                logger.info(f"Skipping URL from different domain: {url}")

        # If no valid URLs from the same domain were found in the sitemap,
        # process the original website URL itself
        if not filtered_urls:
            logger.info("No URLs from the same domain found in sitemap, using original website URL")
            urls_to_process = [config['website_url']]
        else:
            urls_to_process = filtered_urls

        logger.info(f"Processing {len(urls_to_process)} URLs from sitemap (filtered to same domain)")
    else:
        logger.error("No URLs provided. Please either use --urls argument or set WEBSITE_URL in environment.")
        return

    logger.info(f"Starting RAG ingestion pipeline with URLs: {urls_to_process}")

    try:
        # Process each URL provided
        for url in urls_to_process:
            logger.info(f"Processing URL: {url}")

            # Step 1: Crawl the Docusaurus site
            logger.info("Starting crawling process...")
            crawled_data = crawl_docusaurus_site(url, max_pages=args.max_pages)
            logger.info(f"Crawling completed. Retrieved {len(crawled_data)} pages.")

            if not crawled_data:
                logger.warning(f"No content retrieved from {url}. Skipping...")
                continue

            # Step 2: Process each crawled page in batches to manage memory
            all_chunks = []

            for i, (page_url, page_title, page_content) in enumerate(crawled_data):
                logger.info(f"Processing page {i+1}/{len(crawled_data)}: {page_url}")

                # Sanitize content for security
                sanitized_content = sanitize_content(page_content)

                # Chunk the content with sentence boundary awareness
                chunks = chunk_text_by_sentences(
                    text=sanitized_content,
                    source_url=page_url,
                    chunk_size=args.chunk_size,
                    overlap=args.overlap
                )

                all_chunks.extend(chunks)
                logger.info(f"Created {len(chunks)} chunks from {page_url}")

                # Process in batches to manage memory for large sites
                if len(all_chunks) >= 50 or i == len(crawled_data) - 1:  # Process every 50 chunks or at the end
                    if all_chunks:
                        logger.info(f"Processing batch of {len(all_chunks)} chunks...")

                        # Step 3: Generate embeddings for current batch
                        logger.info("Starting embedding generation...")
                        embedding_results = generate_embeddings(all_chunks)
                        logger.info(f"Embedding generation completed for {len(embedding_results)} chunks.")

                        # Step 4: Store embeddings in Qdrant
                        logger.info(f"Starting storage in Qdrant collection: {collection_name}")
                        store_in_qdrant(embedding_results, collection_name)
                        logger.info("Storage completed successfully.")

                        # Clear the batch to free memory
                        all_chunks = []
                        logger.info("Cleared processed chunks to manage memory")

            logger.info(f"Completed processing for {url}")

        logger.info("RAG ingestion pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    main()