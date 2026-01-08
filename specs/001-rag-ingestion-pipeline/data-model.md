# Data Model: RAG Ingestion Pipeline for Docusaurus-based Book Content

## 1. Core Data Structures

### 1.1 Document Chunk
```python
class DocumentChunk:
    id: str                    # Unique identifier for the chunk
    content: str               # The text content of the chunk
    source_url: str           # Original URL where content was found
    page_title: str           # Title of the source page
    section_info: str         # Section hierarchy if available
    chunk_index: int          # Position of chunk within the document
    embedding: List[float]    # Vector embedding of the content
    metadata: Dict[str, Any]  # Additional metadata (timestamps, etc.)
```

**Purpose**: Represents a segment of text extracted from a web page with associated metadata and embeddings.

### 1.2 Ingestion Job
```python
class IngestionJob:
    job_id: str                    # Unique identifier for the ingestion job
    urls: List[str]               # List of URLs to process
    status: str                   # Current status (pending, processing, completed, failed)
    started_at: datetime          # When the job started
    completed_at: datetime        # When the job completed (if finished)
    processed_count: int          # Number of URLs successfully processed
    failed_count: int             # Number of URLs that failed
    error_details: List[Dict]     # Details about any errors encountered
```

**Purpose**: Tracks the state and progress of an ingestion pipeline run.

### 1.3 Page Content
```python
class PageContent:
    url: str                      # Source URL
    title: str                    # Page title
    content: str                  # Clean, extracted content
    html: str                     # Raw HTML (for debugging, not stored long-term)
    metadata: Dict[str, Any]      # Additional page metadata
    extracted_at: datetime        # When content was extracted
```

**Purpose**: Represents the clean content extracted from a single web page before chunking.

## 2. Qdrant Collection Schema

### 2.1 Vector Collection: "book_content"
```json
{
  "collection_name": "book_content",
  "vectors_config": {
    "size": 1024,  // Based on Cohere embedding dimensions
    "distance": "Cosine"
  },
  "payload_schema": {
    "content": {"type": "keyword"},
    "source_url": {"type": "keyword"},
    "page_title": {"type": "keyword"},
    "section_info": {"type": "keyword"},
    "chunk_index": {"type": "integer"},
    "created_at": {"type": "datetime"}
  }
}
```

**Purpose**: Vector collection in Qdrant to store embeddings with associated metadata for RAG retrieval.

## 3. Configuration Schema

### 3.1 Environment Variables
```env
COHERE_API_KEY=str              # Cohere API key for embeddings
QDRANT_API_KEY=str              # Qdrant Cloud API key
QDRANT_URL=str                  # Qdrant Cloud endpoint URL
CHUNK_SIZE=int                  # Size of text chunks (default: 512)
CHUNK_OVERLAP=int               # Overlap between chunks (default: 50)
BATCH_SIZE=int                  # Number of chunks to process at once (default: 10)
REQUEST_TIMEOUT=int             # HTTP request timeout in seconds (default: 30)
MAX_RETRIES=int                 # Maximum retry attempts for failed requests (default: 3)
```

### 3.2 Runtime Configuration
```python
class IngestionConfig:
    cohere_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    chunk_size: int = 512
    chunk_overlap: int = 50
    batch_size: int = 10
    request_timeout: int = 30
    max_retries: int = 3
    cohere_model: str = "embed-multilingual-v2.0"  # Default Cohere model
```

## 4. Data Flow

### 4.1 Ingestion Pipeline Flow
1. **Input**: List of URLs → `IngestionJob` created
2. **Fetch**: URLs → `PageContent` objects with clean text
3. **Process**: `PageContent` → chunked into `DocumentChunk` objects
4. **Embed**: `DocumentChunk.content` → embedding vector
5. **Store**: `DocumentChunk` with embedding → Qdrant collection
6. **Output**: Job completion with statistics

### 4.2 Relationships
- One `IngestionJob` processes many URLs
- One URL produces one `PageContent`
- One `PageContent` creates many `DocumentChunk` objects
- One `DocumentChunk` corresponds to one vector in Qdrant

## 5. Validation Rules

### 5.1 Content Validation
- Content must be non-empty after cleaning
- URLs must be valid and accessible
- Embeddings must be generated successfully before storage
- Chunk size must be within reasonable limits (100-2000 characters)

### 5.2 Metadata Validation
- Source URL must be preserved for each chunk
- Page title should be extracted from HTML
- Creation timestamps must be recorded
- Error information must be captured for failed operations