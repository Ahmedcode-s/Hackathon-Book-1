#!/usr/bin/env python3
"""
RAG Ingestion Pipeline - Main Entry Point

This script orchestrates the full pipeline:
1. URL discovery
2. Text extraction
3. Deterministic chunking
4. Embedding generation
5. Vector storage
"""

import argparse
import logging
from typing import Optional
from datetime import datetime
from src.crawler.url_discovery import URLDiscovery
from src.crawler.docusaurus_crawler import DocusaurusCrawler
from src.text_processor.content_extractor import ContentExtractor
from src.text_processor.chunker import Chunker
from src.embeddings.cohere_client import CohereClient
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.storage.qdrant_client import QdrantStorageClient
from src.storage.vector_storage import VectorStorage
from src.models import ProcessingJob


def main():
    """
    Main entry point for the RAG ingestion pipeline.
    Orchestrates the full pipeline: URL discovery → text extraction → deterministic chunking →
    embedding generation → vector storage.
    """
    parser = argparse.ArgumentParser(description="RAG Ingestion Pipeline")
    parser.add_argument("--url", help="Root URL of the Docusaurus book to process")
    parser.add_argument("--collection", required=True, help="Qdrant collection name for storing vectors")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Size of text chunks (default: 1000)")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Overlap between chunks (default: 200)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Use URL from environment variable if not provided as argument
    if not args.url:
        import os
        args.url = os.getenv("WEBSITE_URL")
        if not args.url:
            parser.error("--url argument or WEBSITE_URL environment variable is required")

    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting RAG ingestion pipeline for URL: {args.url}")
    logger.info(f"Using collection: {args.collection}")

    # Create processing job record
    job = ProcessingJob(
        id=f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        source_url=args.url,
        status="running",
        started_at=datetime.now()
    )

    try:
        logger.info("Step 1: Discovering URLs...")
        url_discovery = URLDiscovery(args.url)
        urls = url_discovery.discover_urls()
        logger.info(f"Discovered {len(urls)} URLs")

        if not urls:
            logger.error("No URLs discovered, stopping pipeline")
            return

        logger.info("Step 2: Crawling pages...")
        crawler = DocusaurusCrawler()
        crawled_pages = crawler.crawl_pages(urls)

        # Filter successful crawls
        successful_pages = [page for page in crawled_pages if page.status == 'success']
        logger.info(f"Crawled {len(successful_pages)} pages successfully out of {len(crawled_pages)}")

        if not successful_pages:
            logger.error("No pages crawled successfully, stopping pipeline")
            return

        logger.info("Step 3: Extracting and processing content...")
        extractor = ContentExtractor()
        chunker = Chunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)

        all_text_chunks = []
        for page in successful_pages:
            # Extract content with hierarchy
            content = extractor.extract_content_with_hierarchy(page)

            if content.strip():  # Only process if there's actual content
                # Create text chunks
                text_chunks = chunker.chunk_text(
                    content,
                    page.url,
                    page.title,
                    " / ".join(page.section_hierarchy) if page.section_hierarchy else "Uncategorized"
                )
                all_text_chunks.extend(text_chunks)

        logger.info(f"Created {len(all_text_chunks)} text chunks")

        if not all_text_chunks:
            logger.error("No text chunks created, stopping pipeline")
            return

        logger.info("Step 4: Generating embeddings...")
        cohere_client = CohereClient()
        embedding_generator = EmbeddingGenerator(cohere_client)

        embedding_vectors = embedding_generator.generate_embeddings_from_chunks(all_text_chunks)
        logger.info(f"Generated {len(embedding_vectors)} embedding vectors")

        if not embedding_vectors:
            logger.error("No embedding vectors generated, stopping pipeline")
            return

        logger.info("Step 5: Storing vectors in Qdrant...")
        qdrant_client = QdrantStorageClient()
        vector_storage = VectorStorage(qdrant_client)

        success = vector_storage.store_vectors_idempotent(args.collection, embedding_vectors)

        if success:
            # Update job record
            job.status = "completed"
            job.pages_processed = len(successful_pages)
            job.chunks_created = len(all_text_chunks)
            job.vectors_stored = len(embedding_vectors)
            job.completed_at = datetime.now()

            # Get final vector count
            final_count = vector_storage.get_vector_count(args.collection)
            logger.info(f"Pipeline completed successfully!")
            logger.info(f"Stored {len(embedding_vectors)} new vectors in collection '{args.collection}'")
            logger.info(f"Total vectors in collection: {final_count}")
        else:
            logger.error("Failed to store vectors in Qdrant")
            job.status = "failed"
            job.error_message = "Failed to store vectors in Qdrant"

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        job.status = "failed"
        job.error_message = str(e)
        raise

    finally:
        logger.info(f"Pipeline job {job.id} completed with status: {job.status}")


if __name__ == "__main__":
    main()