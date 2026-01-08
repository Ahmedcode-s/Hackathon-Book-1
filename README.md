# RAG Retrieval Pipeline Validation

This script validates the RAG (Retrieval Augmented Generation) retrieval pipeline by accepting natural language queries, generating embeddings using Cohere, and performing semantic similarity search against the Qdrant collection containing the book content.

## Prerequisites

- Python 3.7+
- Required Python packages:
  - `cohere`
  - `qdrant-client`
  - `python-dotenv`

## Environment Setup

Create a `.env` file in the project root directory with the following variables:

```env
COHERE_API_KEY="your_cohere_api_key"
QDRANT_URL="your_qdrant_cloud_url"
QDRANT_API_KEY="your_qdrant_api_key"
DELAY_BETWEEN_REQUEST=5.0
```

## Installation

Install the required dependencies:

```bash
pip install cohere qdrant-client python-dotenv
```

## Usage

### Validate Connections Only
```bash
cd backend
python retrieve.py --validate-only
```

### Search with a Query
```bash
cd backend
python retrieve.py "your query here"
```

### Search with Custom Top-K Results
```bash
cd backend
python retrieve.py "your query here" --top-k 10
```

### Get Help
```bash
cd backend
python retrieve.py --help
```

## Example Queries

```bash
# Search for information about ROS 2 with default top-5 results
cd backend
python retrieve.py "What is ROS 2?"

# Search with custom number of results
python retrieve.py "Digital Twin simulation" --top-k 3
```

## Output Format

The script returns results in the following format:
- Result number and similarity score
- Source URL where the content was found
- Page title
- Content preview (first 200 characters)
- Chunk index

## Error Handling

- Rate limiting: The script implements retry logic with exponential backoff for Cohere API rate limits
- Connection failures: Appropriate error messages are displayed if connections to Cohere or Qdrant fail
- Invalid input: Input validation ensures queries are not empty and top-k values are positive

## Features

- Semantic similarity search using Cohere embeddings
- Integration with Qdrant Cloud for vector storage and retrieval
- Configurable number of results (top-k)
- Comprehensive error handling and logging
- Input validation for queries and parameters
- Support for trial API keys with rate limiting