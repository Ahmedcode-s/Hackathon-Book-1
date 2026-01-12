"""
FastAPI backend for RAG Agent integration.

This module exposes the RAG agent functionality through RESTful API endpoints
to enable communication with frontend applications.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import time
from datetime import datetime
import traceback
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API request/response validation
class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.

    Attributes:
        query: The user's natural language question (required)
        selected_text: Additional context from user selection (optional)
        top_k: Number of results to retrieve from Qdrant (default: 5)
        min_score: Minimum similarity threshold (default: 0.3)
    """
    query: str = Field(..., description="The user's natural language question", min_length=1)
    selected_text: Optional[str] = Field(None, description="Additional context from user selection")
    top_k: int = Field(default=5, description="Number of results to retrieve from Qdrant", ge=1, le=20)
    min_score: float = Field(default=0.3, description="Minimum similarity threshold", ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.

    Attributes:
        answer: The agent's response to the query
        confidence_score: Confidence level in the response (0.0-1.0)
        sources_used: URLs of sources used in the response
        processing_time: Time taken to process the request in seconds
        grounding_validation_passed: Whether response passed grounding validation
    """
    answer: str
    confidence_score: float
    sources_used: List[str]
    processing_time: float
    grounding_validation_passed: bool


class HealthResponse(BaseModel):
    """
    Response model for the health check endpoint.

    Attributes:
        status: Health status of the service
        timestamp: ISO timestamp of the health check
    """
    status: str
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="RAG Agent API",
    description="API for interacting with the RAG Agent for book content queries",
    version="1.0.0"
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3000", "http://127.0.0.1:3000"],  # Allow Docusaurus dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware for logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Process time: {process_time:.4f}s")
    return response

# Import the actual RAG agent
try:
    from agent import RAGAgent
    rag_agent = RAGAgent()
except ImportError as e:
    logger.error(f"Failed to import RAGAgent: {e}")
    # Fallback to mock implementation for testing
    class MockRAGAgent:
        def respond(self, query: str, user_selected_text: Optional[str] = None, top_k: int = 5, min_score: float = 0.3):
            # Mock response for initial testing
            return type('MockResponse', (), {
                'answer': f"This is a mock response to your query: '{query}'. In a real implementation, this would come from the RAG agent.",
                'confidence_score': 0.8,
                'sources_used': ['https://example.com/mock-source'],
                'processing_time': 0.5,
                'grounding_validation_passed': True
            })()

    rag_agent = MockRAGAgent()

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return HTTPException(
        status_code=422,
        detail={
            "error": "Validation error",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return HTTPException(status_code=exc.status_code, detail=exc.detail)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"General error: {exc}")
    logger.error(traceback.format_exc())
    return HTTPException(
        status_code=500,
        detail={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

@app.get("/")
async def root():
    """Root endpoint for basic connectivity check."""
    return {"message": "RAG Agent API is running"}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify service availability."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that accepts user queries and returns responses from the RAG agent.

    Args:
        request: ChatRequest containing query and optional parameters

    Returns:
        ChatResponse with agent's answer and metadata
    """
    try:
        # Process the request using the RAG agent with timeout protection
        # Using run_in_executor to run the synchronous agent in a thread pool
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                rag_agent.respond,
                request.query,
                request.selected_text,
                request.top_k,
                request.min_score
            ),
            timeout=60.0  # 60 second timeout
        )

        # Return the response in the expected format
        return ChatResponse(
            answer=response.answer,
            confidence_score=response.confidence_score,
            sources_used=response.sources_used,
            processing_time=response.processing_time,
            grounding_validation_passed=response.grounding_validation_passed
        )
    except asyncio.TimeoutError:
        logger.error("Request timeout processing chat request")
        raise HTTPException(
            status_code=408,  # Request Timeout
            detail={
                "error": "Request timeout",
                "message": "The request took too long to process and timed out"
            }
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Processing error",
                "message": "Failed to process the request with the RAG agent"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)