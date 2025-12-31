# API Contract: RAG Retrieval and Validation

## Endpoints

### POST /retrieve
**Description**: Retrieve semantically relevant text chunks from a Qdrant collection based on a natural language query.

**Request Body**:
```json
{
  "query": "string - The natural language query text",
  "collection": "string - Name of the Qdrant collection to search",
  "top_k": "integer - Number of results to retrieve (default: 5)",
  "query_embedding_model": "string - Model to use for query embedding (default: 'embed-english-v3.0')"
}
```

**Response**:
```json
{
  "success": "boolean - Whether the retrieval was successful",
  "retrieved_chunks": [
    {
      "content": "string - The text content of the chunk",
      "source_url": "string - Original URL where the content was found",
      "page_title": "string - Title of the original page",
      "section_hierarchy": "string - Section hierarchy in the original document",
      "chunk_index": "integer - Position of the chunk in the original text",
      "similarity_score": "number - Similarity score between query and chunk",
      "vector_id": "string - Unique identifier of the stored vector"
    }
  ],
  "query_embedding": {
    "vector": "array[number] - The embedding vector",
    "model": "string - The model used to generate the embedding"
  },
  "metrics": {
    "response_time_ms": "number - Time taken for the retrieval",
    "retrieval_count": "integer - Number of chunks retrieved"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "type": "string - Type of error (e.g., 'collection_not_found', 'invalid_query', 'qdrant_unavailable')",
    "message": "string - Human-readable error message",
    "details": "object - Additional error details if applicable"
  }
}
```

### POST /validate
**Description**: Validate the retrieval pipeline by running test queries and checking results.

**Request Body**:
```json
{
  "collection": "string - Name of the Qdrant collection to validate",
  "test_queries": "array[string] - List of test queries to run",
  "expected_sources": "array[object] - Expected source mappings for validation",
  "consistency_runs": "integer - Number of times to run each query for consistency validation (default: 3)"
}
```

**Response**:
```json
{
  "success": "boolean - Whether the validation was successful",
  "validation_results": [
    {
      "query": "string - The test query",
      "retrieved_chunks": "array[RetrievedChunk] - Chunks returned by the retrieval",
      "relevance_valid": "boolean - Whether retrieved chunks are semantically relevant",
      "metadata_correct": "boolean - Whether source metadata is correct",
      "consistency_score": "number - Consistency of results across runs (0-1)",
      "validation_metrics": {
        "accuracy": "number - Accuracy of source mapping",
        "relevance_score": "number - Average relevance of results",
        "consistency_variance": "number - Variance in similarity scores"
      }
    }
  ],
  "overall_validation": {
    "passed": "boolean - Whether overall validation passed",
    "summary": "string - Summary of validation results",
    "score": "number - Overall validation score (0-1)"
  }
}
```

## Validation Rules

### Input Validation
- Query text must be non-empty and less than 1000 characters
- Collection name must match valid Qdrant collection name format
- top_k must be between 1 and 100
- consistency_runs must be between 1 and 10

### Response Guarantees
- All retrieved chunks will include complete source metadata
- Similarity scores will be between 0 and 1
- Response time will be under 2 seconds for 95% of requests
- Error responses will include actionable error messages

## FastAPI Compatibility
The functions implemented in `retrieve.py` will be designed to be easily wrapped in FastAPI endpoints by returning structured dictionaries that can be directly converted to JSON responses.