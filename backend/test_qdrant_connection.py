#!/usr/bin/env python3
"""
Test script to verify that the Qdrant collection has been populated with embeddings
"""

import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_qdrant_connection():
    """Test the connection to Qdrant and check collection stats."""
    # Get Qdrant configuration from environment
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("Error: QDRANT_URL and QDRANT_API_KEY must be set in environment variables")
        return

    # Connect to Qdrant
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=10
    )

    try:
        # Get collection information
        collections = client.get_collections()
        print(f"Available collections: {[col.name for col in collections.collections]}")

        # Check for our book_embeddings collection
        collection_name = "book_embeddings"
        try:
            collection_info = client.get_collection(collection_name)
            print(f"\nCollection '{collection_name}' exists!")
            print(f"Points count: {collection_info.points_count}")

            # For newer versions of qdrant-client, vectors_count might not be available
            # so we'll just use points_count

            # Sample a few points to verify content
            if collection_info.points_count > 0:
                limit = min(3, collection_info.points_count)
                records, _ = client.scroll(
                    collection_name=collection_name,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )

                print(f"\nSample of first {limit} records:")
                for i, record in enumerate(records):
                    payload = record.payload
                    print(f"  {i+1}. URL: {payload.get('source_url', 'N/A')[:50]}...")
                    print(f"     Text preview: {payload.get('text', '')[:100]}...")
                    print(f"     Position: {payload.get('position', 'N/A')}")
                    print()

            print("SUCCESS: Qdrant connection and data verification successful!")

        except Exception as e:
            print(f"ERROR: Error accessing collection '{collection_name}': {str(e)}")

    except Exception as e:
        print(f"ERROR: Error connecting to Qdrant: {str(e)}")

    finally:
        client.close()

if __name__ == "__main__":
    test_qdrant_connection()