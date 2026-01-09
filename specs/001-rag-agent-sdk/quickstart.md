# Quickstart Guide: RAG Agent using OpenAI Agent SDK

## Overview
This guide provides instructions for setting up and running the RAG agent that integrates OpenAI Agent SDK with Qdrant-based retrieval for grounded responses based on book content.

## Prerequisites

### Environment Setup
- Python 3.11+
- pip package manager
- Git for version control

### Required Accounts
- OpenAI API key for OpenAI Agent SDK
- Qdrant Cloud account with access to the book embeddings collection
- Access to the pre-populated Qdrant collection with book content

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install openai qdrant-client python-dotenv sentence-transformers openrouter
```

### 4. Configure Environment Variables
Create a `.env` file in the backend directory with the following variables:
```env
OPENROUTER_API_KEY=your_openrouter_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
COLLECTION_NAME=book_embeddings
```

## Basic Usage

### 1. Initialize the Agent
```python
from agent import RAGAgent

# Create an instance of the RAG agent
agent = RAGAgent()
```

### 2. Submit a Query
```python
# Simple query
response = agent.respond("What is ROS2?")
print(response.answer)
print(response.sources_used)

# Query with user-selected text
user_text = "I'm interested in ROS2 nodes and their communication patterns."
response = agent.respond("Explain ROS2 concepts", user_selected_text=user_text)
print(response.answer)
```

### 3. Advanced Query Options
```python
# With specific parameters for retrieval
response = agent.respond(
    query="What are the key features of ROS2?",
    top_k=3,           # Number of chunks to retrieve
    min_score=0.5      # Minimum similarity threshold
)
```

## Key Features

### Semantic Retrieval
The agent integrates with Qdrant to perform semantic search against book content:
- Uses all-MiniLM-L6-v2 embeddings for consistency with the ingestion pipeline
- Retrieves top-k most relevant content chunks
- Includes source metadata for proper attribution

### Grounded Responses
- Responses are strictly grounded in retrieved context
- Prevents hallucination by constraining answers to provided context
- Includes source citations in all responses

### User-Selected Text Integration
- Supports incorporating user-provided text for enhanced responses
- Combines user context with retrieved content appropriately
- Handles potential conflicts between different information sources

## Troubleshooting

### Common Issues

#### API Key Issues
- Verify that OPENAI_API_KEY and QDRANT_API_KEY are correctly set in the environment
- Check that the API keys have the necessary permissions

#### Retrieval Problems
- Ensure the QDRANT_URL is accessible
- Verify that the COLLECTION_NAME matches the one used in the ingestion pipeline
- Check that the Qdrant collection contains data

#### Response Quality
- Adjust top_k and min_score parameters to influence retrieval quality
- Review the retrieved context to ensure it's relevant to the query

## Example Queries

### Basic Information Query
```python
response = agent.respond("What is the difference between ROS and ROS2?")
```

### Technical Concept Explanation
```python
response = agent.respond("Explain how ROS2 nodes communicate with each other")
```

### With User Context
```python
user_context = "I'm working on a robotics project involving sensor fusion."
response = agent.respond(
    "What ROS2 components are useful for sensor fusion?",
    user_selected_text=user_context
)
```

## Development

### Running Tests
```bash
pytest tests/agent_test.py
pytest tests/retrieval_test.py
pytest tests/integration_test.py
```

### Modifying Agent Behavior
- Adjust system instructions in the agent initialization
- Modify grounding rules for response generation
- Tune retrieval parameters for different use cases

## Next Steps

1. Experiment with different types of queries to understand the agent's capabilities
2. Fine-tune retrieval parameters based on your specific use case
3. Implement custom tools if additional functionality is needed
4. Monitor response quality and adjust system parameters as needed