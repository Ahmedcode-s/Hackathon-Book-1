#!/usr/bin/env python3
"""
RAG Retrieval and Validation System

This module provides functionality to retrieve semantically relevant text chunks
from Qdrant based on natural language queries, validate chunk-to-source mappings,
and verify pipeline consistency. The system uses Cohere for query embeddings
and provides comprehensive validation capabilities.
"""
import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv
import cohere


def load_config():
    """
    Load configuration from environment variables for Cohere and Qdrant credentials
    """
    load_dotenv()  # Load environment variables from .env file

    config = {
        'cohere_api_key': os.getenv('COHERE_API_KEY'),
        'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
        'qdrant_url': os.getenv('QDRANT_URL'),
    }

    # Validate that required configuration is present
    missing_keys = []
    for key, value in config.items():
        if not value:
            missing_keys.append(key)

    if missing_keys:
        raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")

    return config


def setup_logging(verbose: bool = False):
    """
    Set up logging configuration for the application
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


class RAGError(Exception):
    """
    Custom exception class for RAG retrieval and validation errors
    """
    def __init__(self, message: str, error_type: str = "general", details: Optional[Dict] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Format error response consistent with API contract
    """
    if isinstance(error, RAGError):
        return {
            "success": False,
            "error": {
                "type": error.error_type,
                "message": error.message,
                "details": error.details
            }
        }
    else:
        return {
            "success": False,
            "error": {
                "type": "unknown_error",
                "message": f"An error occurred: {str(error)}",
                "details": {"context": context, "error_class": error.__class__.__name__}
            }
        }


@dataclass
class Query:
    """
    A natural language input from a user that needs to be matched against stored vectors
    """
    text: str
    collection_name: str
    top_k: int = 5
    embedding: Optional[List[float]] = None

    def __post_init__(self):
        """Validate the query after initialization"""
        if not self.text.strip():
            raise ValueError("Query text must not be empty")
        if self.top_k <= 0:
            raise ValueError("top_k must be a positive integer")


@dataclass
class RetrievedChunk:
    """
    A text segment returned by the similarity search, including content, source metadata, and similarity score
    """
    content: str
    source_url: str
    page_title: str
    section_hierarchy: str
    chunk_index: int
    similarity_score: float
    vector_id: str

    def __post_init__(self):
        """Validate the retrieved chunk after initialization"""
        # Content can be empty, but other fields must be present
        if not self.source_url.strip():
            raise ValueError("Source URL must not be empty")
        if not self.page_title.strip():
            raise ValueError("Page title must not be empty")
        if not 0 <= self.similarity_score <= 1:
            raise ValueError("Similarity score must be between 0 and 1")


@dataclass
class QueryEmbedding:
    """
    The vector representation of a user query generated using Cohere models
    """
    vector: List[float]
    model: str
    query_text: str


@dataclass
class ValidationResult:
    """
    The outcome of a validation check, including success/failure status and detailed metrics
    """
    success: bool
    query: Query
    retrieved_chunks: List[RetrievedChunk] = field(default_factory=list)
    message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the validation result after initialization"""
        if not self.success and not self.message:
            raise ValueError("Message must be provided when validation fails")


class CohereClient:
    """
    Cohere client integration for query embedding generation
    """
    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        self.client = cohere.Client(api_key)
        self.model = model

    def generate_embeddings(self, texts: List[str]):
        """
        Generate embeddings for a list of texts using Cohere
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_query"  # Using search_query for queries
            )
            return response
        except Exception as e:
            raise RAGError(
                f"Failed to generate embeddings: {str(e)}",
                error_type="cohere_error",
                details={"model": self.model}
            )

    def embed_query(self, query_text: str) -> QueryEmbedding:
        """
        Generate embedding for a single query text
        """
        response = self.generate_embeddings([query_text])
        embedding_vector = response.embeddings[0]  # Get the first (and only) embedding

        return QueryEmbedding(
            vector=embedding_vector,
            model=self.model,
            query_text=query_text
        )


class QdrantClient:
    """
    Qdrant client integration for similarity search
    """
    def __init__(self, api_key: str, url: str):
        from qdrant_client import QdrantClient as QdrantClientLib
        from qdrant_client.http import models
        self.client = QdrantClientLib(
            url=url,
            api_key=api_key,
            # Handle SSL certificate issues if needed
            https=True
        )

    def search(self, collection_name: str, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        Perform similarity search against Qdrant collection
        """
        try:
            # Perform the search - using the correct method for the Qdrant client
            search_results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=top_k
            )

            # Format results to match our RetrievedChunk structure
            formatted_results = []
            for result in search_results.points:
                # Extract payload information
                payload = result.payload if result.payload else {}
                formatted_results.append({
                    'content': payload.get('content', payload.get('text', payload.get('body', payload.get('page_content', '')))),
                    'source_url': payload.get('source_url', ''),
                    'page_title': payload.get('page_title', ''),
                    'section_hierarchy': payload.get('section_heading', payload.get('section_hierarchy', '')),
                    'chunk_index': int(payload.get('chunk_index', 0)),
                    'similarity_score': result.score,
                    'vector_id': str(result.id)
                })

            return formatted_results
        except Exception as e:
            raise RAGError(
                f"Failed to perform similarity search: {str(e)}",
                error_type="qdrant_error",
                details={"collection_name": collection_name, "top_k": top_k}
            )

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Qdrant
        """
        try:
            self.client.get_collection(collection_name)
            return True
        except Exception:
            return False


def embed_query_text(query_text: str, cohere_client: CohereClient) -> QueryEmbedding:
    """
    Generate embedding for query text using Cohere
    """
    return cohere_client.embed_query(query_text)


def perform_similarity_search(
    query_embedding: List[float],
    collection_name: str,
    qdrant_client: QdrantClient,
    top_k: int = 5
) -> List[Dict]:
    """
    Perform similarity search against Qdrant collection
    """
    return qdrant_client.search(collection_name, query_embedding, top_k)


def retrieve_chunks_with_metadata(
    query_embedding: List[float],
    collection_name: str,
    qdrant_client: QdrantClient,
    top_k: int = 5
) -> List[RetrievedChunk]:
    """
    Retrieve chunks with complete source metadata (URL, page title, section hierarchy, chunk index)
    """
    search_results = qdrant_client.search(collection_name, query_embedding, top_k)

    chunks = []
    for result in search_results:
        chunk = RetrievedChunk(
            content=result['content'],
            source_url=result['source_url'],
            page_title=result['page_title'],
            section_hierarchy=result['section_hierarchy'],
            chunk_index=result['chunk_index'],
            similarity_score=result['similarity_score'],
            vector_id=result['vector_id']
        )
        chunks.append(chunk)

    return chunks


def retrieve_relevant_chunks(
    query_text: str,
    collection_name: str,
    cohere_client: CohereClient,
    qdrant_client: QdrantClient,
    top_k: int = 5
) -> List[RetrievedChunk]:
    """
    Main function to retrieve semantically relevant text chunks from Qdrant based on natural language queries
    with configurable top-k parameter for number of results
    """
    # Generate embedding for the query text
    query_embedding_obj = cohere_client.embed_query(query_text)
    query_vector = query_embedding_obj.vector

    # Retrieve chunks with complete source metadata
    retrieved_chunks = retrieve_chunks_with_metadata(
        query_vector,
        collection_name,
        qdrant_client,
        top_k
    )

    return retrieved_chunks


def validate_collection_exists(
    collection_name: str,
    qdrant_client: QdrantClient
) -> bool:
    """
    Add validation for collection existence before retrieval
    """
    return qdrant_client.collection_exists(collection_name)


def validate_source_url(url: str) -> bool:
    """
    Create source validation function to verify URL format and accessibility
    """
    import re
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def validate_metadata_fields(
    page_title: str,
    section_hierarchy: str
) -> Dict[str, bool]:
    """
    Create metadata validation function to check page title and section hierarchy
    """
    result = {
        'page_title_valid': bool(page_title and page_title.strip()),
        'section_hierarchy_valid': bool(section_hierarchy and section_hierarchy.strip())
    }
    return result


def validate_chunk_source_mappings(
    retrieved_chunks: List[RetrievedChunk]
) -> Dict[str, Any]:
    """
    Implement function to validate retrieved chunk source mappings point to valid locations
    """
    validation_results = {
        'total_chunks': len(retrieved_chunks),
        'valid_mappings': 0,
        'invalid_mappings': 0,
        'details': []
    }

    for chunk in retrieved_chunks:
        url_valid = validate_source_url(chunk.source_url)
        metadata_valid = validate_metadata_fields(chunk.page_title, chunk.section_hierarchy)

        is_valid = url_valid and metadata_valid['page_title_valid'] and metadata_valid['section_hierarchy_valid']

        validation_results['details'].append({
            'chunk_id': chunk.vector_id,
            'source_url': chunk.source_url,
            'url_valid': url_valid,
            'page_title_valid': metadata_valid['page_title_valid'],
            'section_hierarchy_valid': metadata_valid['section_hierarchy_valid'],
            'overall_valid': is_valid
        })

        if is_valid:
            validation_results['valid_mappings'] += 1
        else:
            validation_results['invalid_mappings'] += 1

    return validation_results


def create_validation_report(
    validation_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create validation report with accuracy metrics
    """
    total_chunks = validation_results['total_chunks']
    valid_mappings = validation_results['valid_mappings']

    accuracy = (valid_mappings / total_chunks * 100) if total_chunks > 0 else 0

    report = {
        'accuracy_percentage': accuracy,
        'total_chunks_analyzed': total_chunks,
        'valid_mappings_count': valid_mappings,
        'invalid_mappings_count': validation_results['invalid_mappings'],
        'mapping_accuracy': accuracy / 100,  # As a 0-1 value
        'validation_details': validation_results['details'],
        'summary': f"Successfully validated {valid_mappings} out of {total_chunks} chunk mappings ({accuracy:.2f}% accuracy)"
    }

    return report


def validate_consistency_across_runs(
    query_text: str,
    collection_name: str,
    cohere_client: CohereClient,
    qdrant_client: QdrantClient,
    num_runs: int = 3,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Create consistency validation function to run queries multiple times
    """
    results = []

    for run in range(num_runs):
        try:
            retrieved_chunks = retrieve_relevant_chunks(
                query_text,
                collection_name,
                cohere_client,
                qdrant_client,
                top_k
            )
            results.append({
                'run': run + 1,
                'chunks': retrieved_chunks,
                'chunk_ids': [chunk.vector_id for chunk in retrieved_chunks],
                'scores': [chunk.similarity_score for chunk in retrieved_chunks]
            })
        except Exception as e:
            results.append({
                'run': run + 1,
                'error': str(e)
            })

    return {
        'num_runs': num_runs,
        'query': query_text,
        'collection': collection_name,
        'top_k': top_k,
        'run_results': results
    }
def calculate_score_variance(
    consistency_results: Dict[str, Any]
) -> Dict[str, float]:
    """
    Implement similarity score variance calculation
    """
    import statistics
    
    # Extract scores from all runs
    all_scores = []
    for run_result in consistency_results['run_results']:
        if 'scores' in run_result:
            all_scores.extend(run_result['scores'])
    
    if not all_scores:
        return {
            'variance': 0.0,
            'std_deviation': 0.0,
            'mean_score': 0.0,
            'min_score': 0.0,
            'max_score': 0.0
        }
    
    variance = statistics.variance(all_scores) if len(all_scores) > 1 else 0.0
    std_dev = statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0
    
    return {
        'variance': variance,
        'std_deviation': std_dev,
        'mean_score': statistics.mean(all_scores),
        'min_score': min(all_scores),
        'max_score': max(all_scores)
    }

def calculate_consistency_score(
    consistency_results: Dict[str, Any],
    score_variance: Dict[str, float]
) -> float:
    """
    Add consistency scoring mechanism (0-1 scale)
    """
    # Calculate consistency based on variance and chunk ID consistency
    run_results = consistency_results['run_results']
    
    # Calculate how consistent the chunk IDs are across runs
    chunk_id_sets = []
    for run_result in run_results:
        if 'chunk_ids' in run_result:
            chunk_id_sets.append(set(run_result['chunk_ids']))
    
    if len(chunk_id_sets) < 2:
        return 1.0  # Perfect consistency if only one run
    
    # Calculate intersection of chunk IDs across all runs
    if not chunk_id_sets:
        return 1.0
    
    # Find intersection of all chunk ID sets
    intersection = chunk_id_sets[0]
    for chunk_set in chunk_id_sets[1:]:
        intersection = intersection.intersection(chunk_set)
    
    # Calculate consistency as ratio of intersection to average set size
    avg_set_size = sum(len(s) for s in chunk_id_sets) / len(chunk_id_sets)
    if avg_set_size == 0:
        chunk_consistency = 1.0
    else:
        chunk_consistency = len(intersection) / avg_set_size
    
    # Calculate score consistency (lower variance = higher consistency)
    # Invert variance so that lower variance gives higher score
    score_variance_value = score_variance['variance']
    score_consistency = 1.0 / (1.0 + score_variance_value)  # As variance approaches 0, consistency approaches 1
    
    # Combine both measures (equal weight)
    overall_consistency = (chunk_consistency + score_consistency) / 2.0
    
    return min(overall_consistency, 1.0)  # Ensure it doesn't exceed 1.0

def create_validation_metrics(
    consistency_results: Dict[str, Any],
    score_variance: Dict[str, float],
    consistency_score: float
) -> Dict[str, Any]:
    """
    Create validation metrics for relevance and consistency
    """
    # Calculate metrics from the consistency results
    run_results = [r for r in consistency_results['run_results'] if 'chunks' in r]
    
    if not run_results:
        return {
            'relevance_score': 0.0,
            'consistency_score': 0.0,
            'consistency_variance': 0.0,
            'average_retrieval_count': 0,
            'success_rate': 0.0
        }
    
    # Calculate average number of chunks retrieved per run
    retrieval_counts = [len(r['chunks']) for r in run_results]
    avg_retrieval_count = sum(retrieval_counts) / len(retrieval_counts)
    
    # Calculate success rate (percentage of runs that completed successfully)
    total_runs = consistency_results['num_runs']
    successful_runs = len(run_results)
    success_rate = successful_runs / total_runs if total_runs > 0 else 0.0
    
    # Calculate relevance based on average similarity scores
    all_scores = []
    for run_result in run_results:
        all_scores.extend(run_result['scores'])
    
    avg_similarity_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    return {
        'relevance_score': avg_similarity_score,
        'consistency_score': consistency_score,
        'consistency_variance': score_variance['variance'],
        'average_retrieval_count': avg_retrieval_count,
        'success_rate': success_rate,
        'total_runs': total_runs,
        'successful_runs': successful_runs
    }

def aggregate_validation_results(
    consistency_results: Dict[str, Any],
    score_variance: Dict[str, float],
    consistency_score: float,
    validation_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Implement validation result aggregation with summary statistics
    """
    # Aggregate all the results into a comprehensive summary
    summary = {
        'query': consistency_results['query'],
        'collection': consistency_results['collection'],
        'top_k': consistency_results['top_k'],
        'num_runs': consistency_results['num_runs'],
        'consistency_score': consistency_score,
        'metrics': validation_metrics,
        'score_variance': score_variance,
        'run_summaries': []
    }
    
    # Add details for each run
    for run_result in consistency_results['run_results']:
        if 'chunks' in run_result:
            run_summary = {
                'run_number': run_result['run'],
                'chunk_count': len(run_result['chunks']),
                'average_score': sum(run_result['scores']) / len(run_result['scores']) if run_result['scores'] else 0,
                'top_score': max(run_result['scores']) if run_result['scores'] else 0,
                'bottom_score': min(run_result['scores']) if run_result['scores'] else 0,
                'chunk_ids': run_result['chunk_ids']
            }
        else:
            run_summary = {
                'run_number': run_result['run'],
                'error': run_result.get('error', 'Unknown error')
            }
        
        summary['run_summaries'].append(run_summary)
    
    # Calculate overall summary statistics
    successful_runs = [r for r in summary['run_summaries'] if 'chunk_count' in r]
    if successful_runs:
        avg_chunks = sum(r['chunk_count'] for r in successful_runs) / len(successful_runs)
        avg_scores = [r['average_score'] for r in successful_runs]
        avg_overall_score = sum(avg_scores) / len(avg_scores)
        
        summary['overall_statistics'] = {
            'average_chunks_per_run': avg_chunks,
            'average_score_across_runs': avg_overall_score,
            'successful_runs': len(successful_runs),
            'failed_runs': len(summary['run_summaries']) - len(successful_runs)
        }
    else:
        summary['overall_statistics'] = {
            'average_chunks_per_run': 0,
            'average_score_across_runs': 0,
            'successful_runs': 0,
            'failed_runs': len(summary['run_summaries'])
        }
    
    return summary

def create_argument_parser():
    """
    Create command-line argument parsing for query, collection, and top-k parameters
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG Retrieval and Validation System")
    parser.add_argument("--query", help="Natural language query text")
    parser.add_argument("--collection", required=True, help="Qdrant collection name to search")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return (default: 5)")
    parser.add_argument("--validate", action="store_true", help="Run validation mode instead of retrieval")
    parser.add_argument("--validation-runs", type=int, default=3, help="Number of runs for consistency validation (default: 3)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    return parser


def main():
    """
    Main function to orchestrate retrieval and validation operations
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.verbose)
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize clients
        cohere_client = CohereClient(config['cohere_api_key'])
        qdrant_client = QdrantClient(config['qdrant_api_key'], config['qdrant_url'])
        
        if args.validate:
            # Run validation mode
            if not args.query:
                # If no query provided, run a general validation
                logger.info(f"Validating collection: {args.collection}")
                
                # Perform consistency validation
                validation_results = validate_consistency_across_runs(
                    "test query for validation",
                    args.collection,
                    cohere_client,
                    qdrant_client,
                    num_runs=args.validation_runs,
                    top_k=args.top_k
                )
                
                score_variance = calculate_score_variance(validation_results)
                consistency_score = calculate_consistency_score(validation_results, score_variance)
                metrics = create_validation_metrics(validation_results, score_variance, consistency_score)
                summary = aggregate_validation_results(validation_results, score_variance, consistency_score, metrics)
                
                print("Validation Results:")
                print(f"Consistency Score: {consistency_score:.4f}")
                print(f"Relevance Score: {metrics['relevance_score']:.4f}")
                print(f"Success Rate: {metrics['success_rate']:.2%}")
                print(f"Average Retrieval Count: {metrics['average_retrieval_count']:.2f}")
                
                return summary
            else:
                # Validate a specific query
                logger.info(f"Validating query: {args.query}")
                
                # Perform retrieval
                retrieved_chunks = retrieve_relevant_chunks(
                    args.query,
                    args.collection,
                    cohere_client,
                    qdrant_client,
                    args.top_k
                )
                
                # Validate source mappings
                source_validation = validate_chunk_source_mappings(retrieved_chunks)
                validation_report = create_validation_report(source_validation)
                
                print(f"Retrieved {len(retrieved_chunks)} chunks")
                print(f"Source mapping accuracy: {validation_report['accuracy_percentage']:.2f}%")
                
                # Perform consistency validation
                consistency_results = validate_consistency_across_runs(
                    args.query,
                    args.collection,
                    cohere_client,
                    qdrant_client,
                    num_runs=args.validation_runs,
                    top_k=args.top_k
                )
                
                score_variance = calculate_score_variance(consistency_results)
                consistency_score = calculate_consistency_score(consistency_results, score_variance)
                
                print(f"Consistency score: {consistency_score:.4f}")
                print(f"Score variance: {score_variance['variance']:.6f}")
                
                return {
                    'retrieved_chunks': retrieved_chunks,
                    'source_validation': validation_report,
                    'consistency_results': consistency_results,
                    'consistency_score': consistency_score
                }
        else:
            # Run retrieval mode (default)
            if not args.query:
                parser.error("--query is required for retrieval mode")
            
            logger.info(f"Retrieving for query: {args.query}")
            
            # Validate collection exists first
            if not validate_collection_exists(args.collection, qdrant_client):
                raise RAGError(f"Collection '{args.collection}' does not exist", "collection_not_found")
            
            # Perform retrieval
            retrieved_chunks = retrieve_relevant_chunks(
                args.query,
                args.collection,
                cohere_client,
                qdrant_client,
                args.top_k
            )
            
            # Validate source mappings
            source_validation = validate_chunk_source_mappings(retrieved_chunks)
            validation_report = create_validation_report(source_validation)
            
            print(f"Retrieved {len(retrieved_chunks)} chunks:")
            for i, chunk in enumerate(retrieved_chunks, 1):
                print(f"{i}. Score: {chunk.similarity_score:.4f}")
                print(f"   Content: {chunk.content[:100]}...")
                print(f"   Source: {chunk.source_url}")
                print(f"   Title: {chunk.page_title}")
                print()
            
            print(f"Source mapping validation: {validation_report['summary']}")
            
            return {
                'retrieved_chunks': retrieved_chunks,
                'source_validation': validation_report
            }
            
    except Exception as e:
        error_response = handle_error(e, "main")
        print(f"Error: {error_response}")
        return error_response


if __name__ == "__main__":
    main()
