# Implementation Plan: RAG Ingestion Pipeline

**Feature**: RAG Ingestion Pipeline for Docusaurus-based Book Content
**Branch**: `008-rag-ingestion-pipeline`
**Created**: 2026-01-08
**Status**: Draft

## Overview

This plan outlines the implementation of a RAG ingestion pipeline that crawls Docusaurus-based book websites, extracts meaningful content, chunks it appropriately, generates embeddings using all-MiniLM-L6-v2, and stores the data in Qdrant Cloud.

## Scope & Dependencies

### In Scope
- Create backend directory structure and project initialization
- Web crawling functionality for Docusaurus-based sites
- Content extraction and cleaning (remove nav, footer, scripts)
- Text chunking with consistent size and overlap
- Embedding generation using all-MiniLM-L6-v2 model
- Qdrant Cloud integration for vector storage
- Single-file implementation in main.py
- Environment variable configuration
- Main entry point function

### Out of Scope
- Retrieval or querying logic
- RAG answer generation
- Frontend UI
- Evaluation or benchmarking pipelines
- Agent or FastAPI integration

### External Dependencies
- Python 3.8+
- uv (project manager)
- Qdrant Cloud account and API key
- Sentence Transformers library (for all-MiniLM-L6-v2 model)
- Requests/BeautifulSoup or Playwright (for web crawling)
- Python-dotenv (for environment management)

## Key Technical Decisions & Rationale

### Architecture Decision: Single File Approach
- **Option 1**: Single main.py file (selected) - Simple, easy to deploy, good for focused pipeline
- **Option 2**: Modular approach with multiple files - More maintainable but adds complexity
- **Rationale**: Aligns with constraints specifying single ingestion file for simplicity

### Architecture Decision: Web Scraping Method
- **Option 1**: Requests + BeautifulSoup (selected) - Lightweight, good for static content
- **Option 2**: Selenium/Playwright - Better for JS-heavy sites but more resource intensive
- **Rationale**: Docusaurus sites are typically static, so requests+BeautifulSoup should suffice

### Architecture Decision: Embedding Model Loading
- **Option 1**: Load once globally (selected) - More efficient for multiple chunks
- **Option 2**: Load per request - Cleaner separation but slower
- **Rationale**: Efficiency is important for processing many text chunks

### Architecture Decision: Qdrant Integration
- **Option 1**: Direct HTTP API (selected) - No additional dependencies
- **Option 2**: Qdrant Python client - More convenient but adds dependency
- **Rationale**: Minimize dependencies as per single-file constraint

## Implementation Approach

### Phase 1: Project Setup
1. Create backend directory
2. Initialize project with uv
3. Set up environment variables
4. Create main.py file structure

### Phase 2: Web Crawling & Content Extraction
1. Implement URL validation and crawling
2. Extract meaningful content from Docusaurus pages
3. Remove non-content elements (nav, footer, scripts)
4. Handle multiple pages and site structure

### Phase 3: Text Processing & Chunking
1. Implement text cleaning functions
2. Create chunking algorithm with consistent size and overlap
3. Preserve document structure information in metadata

### Phase 4: Embedding Generation
1. Integrate all-MiniLM-L6-v2 model
2. Generate embeddings for each text chunk
3. Optimize for batch processing

### Phase 5: Vector Storage
1. Connect to Qdrant Cloud
2. Store embeddings with metadata
3. Implement error handling and retry logic

### Phase 6: Main Entry Point & Configuration
1. Create main() function
2. Add command-line argument parsing
3. Implement full pipeline orchestration

## Interface Specifications

### Public API
- `main()` - Entry point function that orchestrates the entire pipeline
- Accepts command-line arguments: `--urls` (list of URLs to crawl), `--chunk-size`, `--overlap`, etc.

### Internal Functions
- `crawl_docusaurus_site(url)` - Returns list of content objects with text and metadata
- `extract_content(html_content)` - Returns clean text content from HTML
- `chunk_text(text, chunk_size, overlap)` - Returns list of text chunks with metadata
- `generate_embeddings(chunks)` - Returns list of embedding vectors
- `store_in_qdrant(vectors, metadata)` - Stores vectors in Qdrant Cloud

## Non-Functional Requirements

### Performance
- Process medium-sized books (100-500 pages) within 30 minutes
- Embedding generation should be batch-optimized
- Crawler should respect robots.txt and implement rate limiting

### Reliability
- Handle network errors gracefully with retry logic
- Ensure deterministic processing across runs
- Implement proper error logging and reporting

### Security
- Secure handling of API keys via environment variables
- Validate URLs to prevent SSRF attacks
- Sanitize extracted content to prevent injection

### Cost
- Efficient use of Qdrant Cloud resources
- Batch operations to minimize API calls

## Data Management

### Source of Truth
- Docusaurus-based book websites serve as the primary source
- Qdrant Cloud serves as the vector store for embeddings

### Schema Evolution
- Vector schema: [embedding_vector, source_url, chunk_text, metadata]
- Metadata will include: URL, page_title, chunk_position, crawl_timestamp

### Migration Strategy
- Not applicable - this is a new implementation

### Data Retention
- Determined by Qdrant Cloud configuration
- Source tracking maintained for provenance

## Operational Considerations

### Observability
- Log processing steps and progress
- Monitor embedding generation performance
- Track successful vs failed URL processing

### Error Handling
- Network timeouts and retries
- Invalid URL validation
- Qdrant Cloud connection failures
- Model loading errors

### Configuration
- Environment variables for Qdrant Cloud credentials
- Configurable chunk size and overlap parameters
- Adjustable rate limiting for crawling

## Risk Analysis & Mitigation

### Risk 1: Large Website Processing
- **Impact**: Memory exhaustion or timeout during crawling
- **Mitigation**: Implement streaming processing and memory management
- **Blast Radius**: Single ingestion run
- **Guardrail**: Size limits and chunking validation

### Risk 2: Rate Limiting or Anti-Bot Measures
- **Impact**: Crawling failures or IP blocking
- **Mitigation**: Respect robots.txt and implement delays
- **Blast Radius**: Individual website processing
- **Guardrail**: Configurable delay settings

### Risk 3: Qdrant Cloud Unavailability
- **Impact**: Ingestion pipeline failures
- **Mitigation**: Retry logic and error handling
- **Blast Radius**: Entire pipeline
- **Guardrail**: Offline processing capability with queue

## Implementation Tasks

### 1. Project Setup
- [ ] Create backend/ directory
- [ ] Initialize project with uv
- [ ] Set up requirements.txt with dependencies
- [ ] Configure environment variables (QDRANT_API_KEY, QDRANT_URL)

### 2. Web Crawling Module
- [ ] Implement URL validation function
- [ ] Create Docusaurus-specific content extractor
- [ ] Build multi-page site crawler
- [ ] Add robots.txt compliance and rate limiting

### 3. Text Processing Module
- [ ] Create text cleaning utility functions
- [ ] Implement chunking algorithm with configurable size/overlap
- [ ] Add metadata preservation (source URL, position, etc.)

### 4. Embedding Module
- [ ] Integrate sentence-transformers library
- [ ] Load all-MiniLM-L6-v2 model
- [ ] Create embedding generation function
- [ ] Implement batch processing for efficiency

### 5. Storage Module
- [ ] Connect to Qdrant Cloud via API
- [ ] Create collection schema for embeddings
- [ ] Implement vector storage with metadata
- [ ] Add error handling and retry logic

### 6. Main Pipeline
- [ ] Create main() entry point function
- [ ] Implement command-line argument parsing
- [ ] Orchestrate full pipeline flow
- [ ] Add progress logging and monitoring

## Success Criteria

### Functional Verification
- [ ] Successfully crawl sample Docusaurus-based book websites
- [ ] Extract clean content while removing non-content elements
- [ ] Generate text chunks with consistent size and overlap
- [ ] Create embeddings using all-MiniLM-L6-v2 model
- [ ] Store vectors and metadata successfully in Qdrant Cloud
- [ ] Process multiple URLs in single run
- [ ] Maintain deterministic output across runs

### Performance Verification
- [ ] Process 100-page site within 5 minutes
- [ ] Handle 500-page site without memory issues
- [ ] Embedding generation performs efficiently
- [ ] Qdrant storage operations complete successfully

### Quality Verification
- [ ] All modules properly handle errors
- [ ] Environment variables securely managed
- [ ] URL validation prevents security issues
- [ ] Logging provides adequate operational visibility