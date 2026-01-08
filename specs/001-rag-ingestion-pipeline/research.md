# Research: RAG Ingestion Pipeline for Docusaurus-based Book Content

## 1. Architecture Research

### 1.1 Docusaurus Content Extraction
- Docusaurus sites typically have consistent HTML structure with content in `<main>` or `[class*="docItem"]` elements
- Navigation and footer elements are usually in separate containers with classes like `navbar`, `footer`, etc.
- Content is usually in markdown converted to HTML, making text extraction straightforward

### 1.2 Python Ecosystem Options
- **Web Scraping**: `requests` + `beautifulsoup4` is the standard approach for static content
- **Alternative**: `scrapy` for more complex crawling needs, but overkill for this use case
- **Alternative**: `playwright`/`selenium` for JavaScript-heavy sites, but Docusaurus content is typically static

### 1.3 Embedding Options
- **Cohere**: Reliable API, good for text embeddings, multiple model options
- **Alternative**: OpenAI embeddings API, but spec specifically mentions Cohere
- **Alternative**: Local models (SentenceTransformers), but spec specifies Cohere API

### 1.4 Vector Storage Options
- **Qdrant Cloud**: Managed vector database with Python client, good similarity search
- **Alternative**: Pinecone, Weaviate, or local Qdrant, but spec specifies Qdrant Cloud

## 2. Technical Implementation Research

### 2.1 Content Cleaning Strategy
- Use CSS selectors to target main content areas in Docusaurus sites
- Remove common non-content elements: navbars, footers, sidebars, headers
- Preserve text structure while removing HTML formatting
- Handle code blocks and special elements appropriately

### 2.2 Chunking Strategy
- Text should be chunked to optimal size for embedding models (typically 512-1024 tokens)
- Overlap chunks to preserve context across boundaries
- Consider semantic boundaries when chunking (paragraphs, sections)
- Maintain source document information for each chunk

### 2.3 Error Handling Research
- Implement retry logic for API calls (Cohere, HTTP requests)
- Handle rate limiting from embedding API providers
- Graceful degradation when individual URLs fail
- Proper logging for debugging and monitoring

## 3. Dependency Research

### 3.1 Required Packages
- `requests`: For HTTP requests to fetch web content
- `beautifulsoup4`: For HTML parsing and content extraction
- `cohere`: Official Cohere Python client for embeddings
- `qdrant-client`: Official Qdrant Python client
- `python-dotenv`: For environment variable management
- `tqdm`: For progress indication during processing

### 3.2 Development Dependencies
- `pytest`: For testing the ingestion pipeline
- `pytest-mock`: For mocking external services during tests
- `black`: For code formatting
- `flake8`: For code linting

## 4. Security & Configuration Research

### 4.1 Environment Variables
- `COHERE_API_KEY`: For Cohere API access
- `QDRANT_API_KEY`: For Qdrant Cloud access
- `QDRANT_URL`: Qdrant Cloud endpoint URL
- `CHUNK_SIZE`: Configurable chunk size (default: 512)
- `CHUNK_OVERLAP`: Configurable overlap (default: 50)

### 4.2 API Rate Limits
- Cohere API has rate limits that need to be considered
- Implement backoff and retry logic
- Process in batches to stay within limits

## 5. Testing Strategy Research

### 5.1 Unit Tests
- Test content extraction logic with sample HTML
- Test chunking algorithm with various text inputs
- Test metadata handling
- Mock external API calls for fast, reliable tests

### 5.2 Integration Tests
- Test with actual Docusaurus sites (when available)
- Test end-to-end pipeline with limited data
- Verify data is correctly stored in Qdrant