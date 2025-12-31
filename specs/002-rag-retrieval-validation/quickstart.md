# Quickstart Guide: RAG Retrieval and Validation

## Overview
This guide helps you quickly set up and run the RAG retrieval and validation system. The system retrieves semantically relevant text chunks from Qdrant based on natural language queries and validates the end-to-end pipeline.

## Prerequisites
- Python 3.11+
- Cohere API key
- Qdrant Cloud account and API key
- Valid vector collection in Qdrant (from ingestion pipeline)

## Setup
1. Ensure you have the backend directory with the RAG ingestion pipeline
2. Make sure your environment variables are set:
   ```bash
   export COHERE_API_KEY=your_cohere_api_key_here
   export QDRANT_API_KEY=your_qdrant_api_key_here
   export QDRANT_URL=your_qdrant_cluster_url_here
   ```

## Running Retrieval and Validation
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Run the retrieval system with a query:
   ```bash
   python retrieve.py --query "Your natural language query here" --collection "your-collection-name" --top-k 5
   ```

3. Run end-to-end validation tests:
   ```bash
   python retrieve.py --validate --collection "your-collection-name"
   ```

## Example Usage
```bash
# Simple retrieval
python retrieve.py --query "How do I configure the system?" --collection "my-book" --top-k 3

# Validation mode
python retrieve.py --validate --collection "my-book" --test-query "Sample query for validation"

# With verbose output
python retrieve.py --query "Explain the architecture" --collection "my-book" --verbose
```

## Expected Output
The system will return:
- Retrieved text chunks with source metadata (URL, title, section)
- Similarity scores for each chunk
- Validation results showing relevance and metadata correctness
- Performance metrics and consistency checks