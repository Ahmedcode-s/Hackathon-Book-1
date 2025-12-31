# RAG Ingestion Pipeline

This pipeline crawls Docusaurus-based technical book websites, extracts clean text content, generates embeddings using Cohere models, and stores vectors with metadata in Qdrant Cloud. The pipeline is idempotent and re-runnable without duplication, with deterministic chunking and stable chunk IDs.

## Prerequisites

- Python 3.11+
- `uv` package manager
- Cohere API key
- Qdrant Cloud account and API key

## Setup

1. **Install dependencies using uv**:
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_URL=your_qdrant_cluster_url
   ```

## Usage

Run the ingestion pipeline:

```bash
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name"
```

### Additional options:

```bash
# With custom chunk size
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name" --chunk-size 1000

# With custom overlap
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name" --chunk-overlap 200

# Verbose logging
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name" --verbose
```

## Architecture

The pipeline consists of the following components:

- **Crawler**: Discovers and crawls Docusaurus-based book URLs
- **Text Processor**: Extracts clean content and chunks it deterministically
- **Embeddings**: Generates vector embeddings using Cohere models
- **Storage**: Stores vectors with metadata in Qdrant Cloud

## Features

- **Idempotent**: Safe to run multiple times without creating duplicates
- **Robust**: Handles network errors and API rate limits gracefully
- **Configurable**: Adjustable chunk size and overlap parameters
- **Monitored**: Comprehensive logging and error handling