#!/usr/bin/env python3
"""
Script to run the RAG ingestion pipeline using URLs from the sitemap_urls.json file.
This script will process all the URLs and store the embeddings in Qdrant.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import load_environment_variables, crawl_docusaurus_site, chunk_text_by_sentences, generate_embeddings, store_in_qdrant, ensure_collection_exists, logger

def load_urls_from_file(filename: str = "sitemap_urls.json") -> list:
    """
    Load URLs from a file

    Args:
        filename: Name of the file to load from

    Returns:
        List of URLs
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            urls = json.load(f)
        logger.info(f"Loaded {len(urls)} URLs from {filename}")
        return urls
    except FileNotFoundError:
        logger.error(f"File {filename} not found")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {filename}")
        return []

def run_pipeline_with_urls():
    """Run the RAG ingestion pipeline with URLs from the sitemap file."""
    # Load URLs from the sitemap file
    urls = load_urls_from_file("sitemap_urls.json")

    if not urls:
        logger.error("No URLs loaded from sitemap_urls.json")
        return

    logger.info(f"Starting RAG ingestion pipeline with {len(urls)} URLs from sitemap")

    # Load configuration
    config = load_environment_variables()
    collection_name = config['collection_name']

    # Ensure collection exists
    ensure_collection_exists(collection_name)

    # Process each URL
    total_chunks = 0
    total_embeddings = 0

    for i, url in enumerate(urls, 1):
        logger.info(f"Processing URL {i}/{len(urls)}: {url}")

        try:
            # Crawl the specific page
            crawled_data = crawl_docusaurus_site(url, max_pages=1)  # Just this specific URL

            if not crawled_data:
                logger.warning(f"No content retrieved from {url}. Skipping...")
                continue

            # Process each crawled page
            all_chunks = []
            for page_url, page_title, page_content in crawled_data:
                logger.info(f"Processing page: {page_url}")

                # Chunk the content
                chunks = chunk_text_by_sentences(
                    text=page_content,
                    source_url=page_url,
                    chunk_size=512,
                    overlap=128
                )

                all_chunks.extend(chunks)
                logger.info(f"Created {len(chunks)} chunks from {page_url}")

            if not all_chunks:
                logger.warning(f"No chunks created from {url}. Skipping embedding and storage...")
                continue

            # Generate embeddings for all chunks from this URL
            logger.info(f"Generating embeddings for {len(all_chunks)} chunks from {url}...")
            embedding_results = generate_embeddings(all_chunks)
            logger.info(f"Generated embeddings for {len(embedding_results)} chunks")

            # Store embeddings in Qdrant
            logger.info(f"Storing {len(embedding_results)} embeddings in Qdrant...")
            store_in_qdrant(embedding_results, collection_name)

            total_chunks += len(all_chunks)
            total_embeddings += len(embedding_results)

            logger.info(f"Successfully processed and stored {url}")

        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            continue

    logger.info(f"Ingestion pipeline completed! Processed {total_chunks} chunks and generated {total_embeddings} embeddings.")

if __name__ == "__main__":
    run_pipeline_with_urls()