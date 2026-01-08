# Data Model: RAG Retrieval Pipeline

## Overview
Data structures and schemas for the RAG retrieval pipeline that interacts with Qdrant Cloud collection containing book embeddings.

## Input Data

### Query Input
```python
class QueryInput:
    query_text: str          # Natural language query from user
    top_k: int = 5          # Number of results to return (default 5)
    min_score: float = 0.0  # Minimum similarity score threshold (optional)
```

## Internal Data Structures

### Embedding Data
```python
class QueryEmbedding:
    vector: List[float]      # 384-dimensional embedding vector
    text: str               # Original query text
    model: str              # Model used for embedding ('all-MiniLM-L6-v2')
```

### Search Parameters
```python
class SearchParams:
    collection_name: str    # Qdrant collection name ('book_embeddings')
    query_vector: List[float]  # Query embedding vector
    limit: int              # Number of results to return
    with_payload: bool      # Whether to include metadata with results
    score_threshold: float # Minimum similarity score
```

## Output Data

### Retrieved Chunk
```python
class RetrievedChunk:
    text: str               # Text content of the chunk
    source_url: str         # URL where the content was sourced from
    position: int           # Position of the chunk in the original document
    score: float            # Similarity score (0.0-1.0)
    chunk_id: str           # Unique identifier for the chunk
    created_at: float       # Timestamp when the chunk was indexed
```

## Qdrant Collection Schema

### Collection Configuration
```python
# Vector Configuration
vector_size: 384           # Dimension of all-MiniLM-L6-v2 embeddings
distance: "Cosine"         # Cosine distance for similarity search

# Payload Schema (Metadata)
payload_schema: {
    "text": "keyword",           # Text content of the chunk
    "source_url": "keyword",     # Source URL
    "position": "integer",       # Position in original document
    "chunk_id": "keyword",       # Chunk identifier
    "created_at": "float"        # Creation timestamp
}
```

## API Interface

### Function Signatures
```python
def retrieve_chunks(
    query_text: str,
    top_k: int = 5,
    min_score: float = 0.0
) -> List[RetrievedChunk]:
    """
    Retrieve relevant text chunks from Qdrant based on semantic similarity
    to the input query.

    Args:
        query_text: Natural language query
        top_k: Number of results to return (default 5)
        min_score: Minimum similarity threshold (default 0.0)

    Returns:
        List of retrieved chunks with metadata
    """
    pass

def validate_retrieval(
    query_text: str,
    expected_sources: List[str] = None
) -> Dict[str, Any]:
    """
    Validate retrieval results for semantic relevance and metadata integrity.

    Args:
        query_text: Natural language query
        expected_sources: Optional list of expected source URLs for validation

    Returns:
        Validation results with metrics and quality indicators
    """
    pass
```

## Data Flow

1. **Input**: Natural language query received
2. **Processing**: Query converted to embedding vector using all-MiniLM-L6-v2
3. **Search**: Vector similarity search performed against Qdrant collection
4. **Filtering**: Results filtered by similarity score threshold
5. **Output**: Retrieved chunks with complete metadata returned
6. **Validation**: Optional validation of semantic relevance and metadata integrity

## Constraints

- Embedding vectors must be 384-dimensional to match all-MiniLM-L6-v2 output
- Similarity scores range from 0.0 to 1.0 (higher is more similar)
- Source URLs must match the original book website domain
- Position values must be non-negative integers
- All metadata fields must be preserved during retrieval