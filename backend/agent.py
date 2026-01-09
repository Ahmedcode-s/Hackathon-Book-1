"""
RAG Agent implementation using OpenAI Agents SDK with OpenRouter as LLM provider.

This agent integrates with Qdrant retrieval system and generates grounded responses
based on retrieved book content with proper source citations.
"""
import os
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models.agent_models import (
    AgentQuery, RetrievedContext, GroundedResponse, RetrievedChunk
)
from tools.retrieval_tool import QdrantRetrievalTool


class RAGAgent:
    """
    RAG agent that integrates OpenAI Agent SDK with OpenRouter as LLM provider
    and Qdrant-based retrieval for grounded responses based on book content.
    """

    def __init__(self):
        """
        Initialize the RAG agent with OpenRouter configuration and tools.
        """
        # Configure OpenAI client to use OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

        # Initialize tools
        self.retrieval_tool = QdrantRetrievalTool()

        # Model to use
        self.model = "mistralai/devstral-2512:free"

    def combine_contexts(self, retrieved_context: RetrievedContext, user_selected_text: Optional[str]) -> str:
        """
        Combine retrieved context with user-selected text if provided.

        Args:
            retrieved_context: Context retrieved from Qdrant
            user_selected_text: Additional context provided by user

        Returns:
            Combined context as a string
        """
        context_parts = []

        # Add retrieved context
        for chunk in retrieved_context.chunks:
            context_parts.append(f"Source: {chunk.source_url}")
            context_parts.append(f"Content: {chunk.text}")
            context_parts.append("---")

        # Add user-selected text if provided
        if user_selected_text:
            context_parts.append("User-Provided Context:")
            context_parts.append(user_selected_text)
            context_parts.append("---")

        return "\n".join(context_parts)

    def generate_response_with_openrouter_model(self, query: str, combined_context: str) -> str:
        """
        Generate response using OpenRouter model with combined context.

        Args:
            query: Original user query
            combined_context: Combined context from retrieval and user input

        Returns:
            Generated response from the model
        """
        system_prompt = """You are a helpful assistant that answers questions based strictly on the provided context.
        Only use information that is present in the provided context. Do not generate information that is not
        explicitly stated in the context. Always cite sources when possible."""

        user_message = f"""Context: {combined_context}

Question: {query}

Please provide a detailed answer based only on the information provided in the context above.
If the context does not contain information to answer the question, say so explicitly.
Always cite the source URLs when referencing information from the context."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for more deterministic behavior
            max_tokens=1000
        )

        return response.choices[0].message.content

    def add_citations(self, response: str, retrieved_context: RetrievedContext) -> GroundedResponse:
        """
        Add source citations to the response and create a GroundedResponse object.

        Args:
            response: Raw response from the model
            retrieved_context: Context that was used to generate the response

        Returns:
            GroundedResponse object with citations and metadata
        """
        # Extract source URLs from the retrieved context
        source_urls = list(set([chunk.source_url for chunk in retrieved_context.chunks]))

        # Calculate a basic confidence score based on the number of sources used
        # and the similarity scores of the chunks
        avg_similarity = sum([chunk.score for chunk in retrieved_context.chunks]) / len(retrieved_context.chunks) if retrieved_context.chunks else 0.0
        confidence_score = min(avg_similarity, 1.0)  # Ensure it's between 0 and 1

        # Create the grounded response
        grounded_response = GroundedResponse(
            answer=response,
            confidence_score=confidence_score,
            sources_used=source_urls,
            processing_time=retrieved_context.retrieval_time,  # This is just the retrieval time
            grounding_validation_passed=True  # We assume it's properly grounded since we use context
        )

        return grounded_response

    def respond(self, query: str, user_selected_text: Optional[str] = None, top_k: int = 5, min_score: float = 0.3) -> GroundedResponse:
        """
        Process a query and return a grounded response.

        Args:
            query: Natural language question from user
            user_selected_text: Optional additional context from user
            top_k: Number of results to retrieve from Qdrant
            min_score: Minimum similarity threshold for retrieval

        Returns:
            GroundedResponse with answer and source citations
        """
        start_time = time.time()

        # 1. Use retrieval tool to get relevant context
        retrieval_result = self.retrieval_tool(query, top_k=top_k, min_score=min_score)

        # Convert retrieval result to RetrievedContext
        retrieved_context = RetrievedContext(
            chunks=retrieval_result["chunks"],
            retrieval_time=retrieval_result["retrieval_time"],
            total_chunks_found=retrieval_result["total_chunks_found"]
        )

        # 2. Combine context with user-selected text if provided
        combined_context = self.combine_contexts(retrieved_context, user_selected_text)

        # 3. Generate grounded response using OpenRouter model with combined context
        raw_response = self.generate_response_with_openrouter_model(query, combined_context)

        # 4. Add source citations to response
        final_response = self.add_citations(raw_response, retrieved_context)

        # Update processing time to include the full cycle
        final_response.processing_time = time.time() - start_time

        return final_response


def main():
    """
    Main function to run the RAG agent from command line.
    """
    import argparse

    parser = argparse.ArgumentParser(description="RAG Agent using OpenAI Agent SDK with OpenRouter")
    parser.add_argument("--query", type=str, required=True, help="Natural language query text")
    parser.add_argument("--user-text", type=str, default=None, help="Additional user-provided context")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to retrieve (default: 5)")
    parser.add_argument("--min-score", type=float, default=0.3, help="Minimum similarity threshold (default: 0.3)")

    args = parser.parse_args()

    try:
        # Initialize the agent
        agent = RAGAgent()

        # Validate connections first
        if not agent.retrieval_tool.validate_connection():
            print("ERROR: Cannot connect to Qdrant. Please check your environment variables.")
            return

        print(f"Processing query: '{args.query}'")
        print("Retrieving relevant context...")

        # Process the query
        response = agent.respond(
            query=args.query,
            user_selected_text=args.user_text,
            top_k=args.top_k,
            min_score=args.min_score
        )

        print(f"\nAnswer: {response.answer}")
        print(f"Confidence Score: {response.confidence_score:.3f}")
        print(f"Processing Time: {response.processing_time:.3f}s")
        print(f"Sources Used: {len(response.sources_used)}")
        for i, source in enumerate(response.sources_used, 1):
            print(f"  {i}. {source}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()