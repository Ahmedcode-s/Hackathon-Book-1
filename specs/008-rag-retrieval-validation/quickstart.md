# Quickstart Guide: RAG Retrieval Pipeline

## Overview
Get started with the RAG retrieval pipeline to validate semantic search against stored book embeddings in Qdrant Cloud.

## Prerequisites

### Environment Setup
1. Python 3.11+
2. pip package manager
3. Access to Qdrant Cloud instance with book embeddings collection

### Required Credentials
- QDRANT_URL: URL of your Qdrant Cloud instance
- QDRANT_API_KEY: API key for authentication
- COLLECTION_NAME: Name of the embeddings collection (default: "book_embeddings")

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Navigate to Backend Directory
```bash
cd backend/
```

### 3. Install Dependencies
```bash
pip install sentence-transformers qdrant-client python-dotenv
```

### 4. Configure Environment Variables
Create a `.env` file in the backend directory:
```env
QDRANT_URL=your-qdrant-cloud-url
QDRANT_API_KEY=your-qdrant-api-key
COLLECTION_NAME=book_embeddings
```

## Usage

### 1. Basic Retrieval
```python
from retrieve import retrieve_chunks

# Perform a basic retrieval
results = retrieve_chunks("your natural language query here")
for chunk in results:
    print(f"Score: {chunk.score}")
    print(f"Source: {chunk.source_url}")
    print(f"Text: {chunk.text[:200]}...")
    print("---")
```

### 2. Advanced Retrieval with Parameters
```python
from retrieve import retrieve_chunks

# Retrieve with custom parameters
results = retrieve_chunks(
    query_text="your query here",
    top_k=10,           # Return top 10 results
    min_score=0.3       # Minimum similarity threshold
)
```

### 3. Direct Script Usage
```bash
python retrieve.py --query "your query here" --top-k 5
```

## Validation

### Test Retrieval Quality
```python
from retrieve import validate_retrieval

# Validate retrieval results
validation_result = validate_retrieval(
    query_text="sample query about the book content",
    expected_sources=["https://example-book-site.com/docs/example"]  # Optional
)
print(validation_result)
```

## Troubleshooting

### Common Issues

#### 1. Connection Errors
- Verify QDRANT_URL and QDRANT_API_KEY are correct
- Check internet connectivity to Qdrant Cloud
- Ensure firewall allows outbound HTTPS connections

#### 2. Empty Results
- Verify the collection name is correct
- Confirm embeddings exist in Qdrant Cloud
- Try lowering the min_score threshold

#### 3. Slow Performance
- Check network latency to Qdrant Cloud
- Verify query length (very long queries may take longer to embed)
- Monitor system memory usage

### Debug Mode
Run with debug logging enabled:
```bash
export DEBUG=1
python retrieve.py --query "test query"
```

## Configuration Options

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| QDRANT_URL | Qdrant Cloud instance URL | - |
| QDRANT_API_KEY | Authentication API key | - |
| COLLECTION_NAME | Name of embeddings collection | book_embeddings |
| TOP_K_DEFAULT | Default number of results | 5 |
| MIN_SCORE_DEFAULT | Default minimum similarity | 0.0 |

### Runtime Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| --query | Natural language query text | - |
| --top-k | Number of results to return | 5 |
| --min-score | Minimum similarity threshold | 0.0 |
| --verbose | Enable verbose logging | false |

## Next Steps

1. Integrate the retrieval function into your application
2. Experiment with different query formulations
3. Adjust top_k and min_score parameters based on your use case
4. Monitor retrieval quality and relevance