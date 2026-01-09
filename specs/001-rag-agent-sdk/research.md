# Research: RAG Agent using OpenAI Agent SDK

## Overview
Research for implementing a RAG agent that integrates with OpenAI Agent SDK, uses Qdrant for semantic retrieval, and generates responses grounded in retrieved book content with proper source attribution.

## Key Components Analysis

### 1. OpenAI Agent SDK with OpenRouter Integration
- **Purpose**: Create an intelligent agent that can orchestrate tools and generate grounded responses using OpenRouter as the LLM provider
- **Implementation**: Use OpenAI's agent framework with OpenRouter as the LLM provider for response generation
- **Configuration**: Set up OpenRouter with mistralai/devstral-2512:free model via https://openrouter.ai/api/v1
- **System Instructions**: Define grounding rules to ensure responses only use retrieved context

### 2. Qdrant Retrieval Tool
- **Function**: Semantic search tool that retrieves relevant book content chunks based on user queries
- **Integration**: Wrap existing retrieve.py functionality in an agent-compatible tool format
- **Input**: Natural language query from user
- **Output**: List of relevant text chunks with source metadata
- **Parameters**: Top-k results, minimum similarity threshold

### 3. Grounded Response Generation
- **Constraint**: Agent responses must only contain information present in retrieved context
- **Validation**: Implement content validation to ensure no hallucination occurs
- **Citation**: Include source metadata in responses to indicate information origin
- **Fallback**: Handle cases where no relevant content is retrieved

### 4. User-Selected Text Integration
- **Feature**: Support for incorporating user-provided text alongside agent queries
- **Handling**: Combine user-selected text with retrieved context for enhanced responses
- **Conflict Resolution**: Mechanism to handle contradictions between sources

## Technical Approach

### Agent Architecture
```python
from openai import OpenAI
from qdrant_client import QdrantClient
import os

class RAGAgent:
    def __init__(self):
        # Configure OpenAI client to use OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.retrieval_tool = QdrantRetrievalTool()

    def respond(self, query, user_selected_text=None):
        # 1. Use retrieval tool to get relevant context
        context = self.retrieval_tool.search(query)

        # 2. Combine context with user-selected text if provided
        combined_context = self.combine_contexts(context, user_selected_text)

        # 3. Generate grounded response using OpenRouter model with combined context
        response = self.generate_response_with_openrouter_model(query, combined_context)

        # 4. Add source citations to response
        return self.add_citations(response, context)
```

### Retrieval Tool Implementation
```python
class QdrantRetrievalTool:
    def __call__(self, query: str, top_k: int = 5, min_score: float = 0.3):
        # Use the existing retrieve.py functionality
        # Return structured results with source metadata
        pass
```

### Response Grounding Strategy
- Prepend retrieved context to model prompt
- Use system instructions to constrain responses to provided context
- Implement post-processing validation to check for hallucinations
- Include source citations in final response

## Dependencies Analysis

### Core Dependencies
- `openai`: For OpenAI Agent SDK integration and tool orchestration
- `qdrant-client`: For vector database operations (already used in retrieval pipeline)
- `python-dotenv`: For environment configuration
- `sentence-transformers`: For embedding consistency with existing pipeline
- `openrouter`: For OpenRouter API integration for LLM access

### Potential Challenges
- Ensuring deterministic agent behavior with LLMs
- Managing token limits with large retrieved contexts
- Validating that responses are properly grounded in context
- Handling edge cases where retrieval returns no results
- Integrating user-selected text with retrieved context appropriately

## Architecture Considerations

### Single File Design
- All agent logic in agent.py as specified
- Supporting tools in separate modules for clarity
- Clean separation between agent orchestration and individual tool implementations

### Security Aspects
- Secure handling of API keys through environment variables
- Input validation for user queries
- Connection security to Qdrant Cloud via HTTPS
- Proper error handling without exposing sensitive information

### Scalability Factors
- Efficient retrieval to minimize token usage
- Caching mechanisms for repeated queries
- Proper resource management during agent execution