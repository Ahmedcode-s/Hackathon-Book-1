# API Contract: RAG Agent Service

## Overview
Contract for the RAG Agent service that integrates OpenAI Agent SDK with OpenRouter as LLM provider and Qdrant-based retrieval.

## Endpoints

### POST /agent/respond
Submit a query to the RAG agent for processing and receive a grounded response.

#### Request
```json
{
  "query": "string",
  "user_selected_text": "string | null",
  "top_k": "integer | optional, default: 5",
  "min_score": "float | optional, default: 0.3"
}
```

#### Response
```json
{
  "answer": "string",
  "confidence_score": "float",
  "sources_used": "string[]",
  "processing_time": "float",
  "grounding_validation_passed": "boolean",
  "retrieved_chunks": [
    {
      "text": "string",
      "source_url": "string",
      "position": "integer",
      "score": "float",
      "chunk_id": "string"
    }
  ]
}
```

#### Status Codes
- `200 OK` - Successful response generated
- `400 Bad Request` - Invalid query format or parameters
- `422 Unprocessable Entity` - Query too short, empty, or exceeds limits
- `500 Internal Server Error` - Agent processing error or service unavailable

#### Example Request
```json
{
  "query": "What are the main differences between ROS and ROS2?",
  "top_k": 3,
  "min_score": 0.5
}
```

#### Example Response
```json
{
  "answer": "ROS2 was designed to address several limitations of ROS1 including improved security, better real-time support, and multi-platform compatibility...",
  "confidence_score": 0.85,
  "sources_used": [
    "https://example.com/ros2-introduction",
    "https://example.com/ros-comparison"
  ],
  "processing_time": 4.2,
  "grounding_validation_passed": true,
  "retrieved_chunks": [
    {
      "text": "ROS2 introduces several improvements over ROS1 including enhanced security features, better real-time support, and improved multi-platform compatibility...",
      "source_url": "https://example.com/ros2-introduction",
      "position": 2,
      "score": 0.89,
      "chunk_id": "chunk_12345_2"
    }
  ]
}
```

### GET /agent/health
Check the health status of the agent service.

#### Response
```json
{
  "status": "healthy",
  "openai_connected": "boolean",
  "qdrant_connected": "boolean",
  "retrieval_tool_working": "boolean",
  "timestamp": "ISO8601 datetime"
}
```

#### Status Codes
- `200 OK` - Service is healthy
- `503 Service Unavailable` - One or more dependencies are unavailable

## Tool Contracts

### QdrantRetrievalTool
Tool for retrieving semantically similar content from Qdrant.

#### Input Schema
```json
{
  "query": "string",
  "top_k": "integer",
  "min_score": "float"
}
```

#### Output Schema
```json
{
  "chunks": [
    {
      "text": "string",
      "source_url": "string",
      "position": "integer",
      "score": "float",
      "chunk_id": "string"
    }
  ],
  "retrieval_time": "float"
}
```

### GroundingValidatorTool
Tool for validating that responses are properly grounded in context.

#### Input Schema
```json
{
  "response": "string",
  "context": "string",
  "sources": "string[]"
}
```

#### Output Schema
```json
{
  "is_valid": "boolean",
  "validation_details": "string",
  "hallucination_detected": "boolean",
  "confidence_score": "float"
}
```

## Error Handling

### Standard Error Format
```json
{
  "error": {
    "type": "string",
    "message": "string",
    "details": "object | null",
    "timestamp": "ISO8601 datetime"
  }
}
```

### Common Error Types
- `INVALID_QUERY` - Query is malformed or doesn't meet requirements
- `RETRIEVAL_FAILED` - Unable to retrieve context from Qdrant
- `AGENT_ERROR` - OpenAI Agent processing error
- `GROUNDING_FAILED` - Response validation failed
- `SERVICE_UNAVAILABLE` - Required service is not available

## Rate Limiting
- Requests per minute: 60
- Burst limit: 10 requests
- Retry after: 60 seconds if rate limited

## Security
- All requests must include proper authentication headers
- API keys must be sent via HTTPS only
- Query content is logged without storing sensitive information