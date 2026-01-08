#!/usr/bin/env python3
"""
Test script for RAG retrieval functionality
"""

from retrieve import RAGRetriever

def test_retrieval():
    """
    Test the retrieval functionality with a sample query
    """
    try:
        # Initialize the retriever
        retriever = RAGRetriever()

        # Test with a sample query
        query = "What is ROS2 and how does it relate to physical AI?"
        print(f"Testing retrieval with query: '{query}'")

        # Retrieve chunks
        results = retriever.retrieve_chunks(query, top_k=3, min_score=0.1)

        print(f"\nRetrieved {len(results)} chunks:")
        for i, chunk in enumerate(results, 1):
            print(f"\n{i}. Score: {chunk.score:.3f}")
            print(f"   Source: {chunk.source_url}")
            print(f"   Position: {chunk.position}")
            print(f"   Text Preview: {chunk.text[:150]}...")

        # Run validation
        print(f"\nRunning validation for query: '{query}'")
        validation_result = retriever.validate_retrieval(query)

        print(f"Validation Results:")
        print(f"  Retrieved Count: {validation_result['retrieved_count']}")
        print(f"  Semantic Relevance Score: {validation_result['semantic_relevance_score']:.3f}")
        print(f"  Metadata Integrity: {validation_result['metadata_integrity']}")

        # Close the retriever
        retriever.close()

        print("\n✅ Retrieval test completed successfully!")

    except Exception as e:
        print(f"ERROR: Error during retrieval test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_retrieval()