# Tasks: RAG Website Ingestion Pipeline

## Feature Overview

Implementation of a RAG ingestion pipeline that crawls Docusaurus-based technical book websites, extracts clean text content, generates embeddings using Cohere models, and stores vectors with metadata in Qdrant Cloud. The pipeline will be idempotent and re-runnable without duplication, with deterministic chunking and stable chunk IDs.

**Target**: Python 3.11 with requests, beautifulsoup4, cohere, qdrant-client, python-dotenv, uv

## Dependencies

- User Story 2 depends on User Story 1 completion (need text content before generating embeddings)
- User Story 3 depends on User Story 1 completion (need text content before chunking)

## Parallel Execution Examples

- Within User Story 1: Crawler and text extraction components can be developed in parallel
- Within User Story 2: Cohere integration and Qdrant storage can be developed in parallel
- Within User Story 3: Chunking algorithm and ID generation can be developed in parallel

## Implementation Strategy

MVP will implement User Story 1 (basic crawling and text extraction) to provide core functionality. Subsequent stories will add embedding generation and chunking capabilities.

---

## Phase 1: Setup

**Goal**: Initialize project structure and dependencies

- [X] T001 Create backend directory structure
- [X] T002 Initialize pyproject.toml with uv for dependency management
- [X] T003 Add dependencies to pyproject.toml: requests, beautifulsoup4, cohere, qdrant-client, python-dotenv
- [X] T004 Generate requirements.txt from pyproject.toml
- [X] T005 Create .env and .env.example files with API key placeholders
- [X] T006 Create source directory structure: src/crawler, src/text_processor, src/embeddings, src/storage, src/utils
- [X] T007 Create tests directory structure: tests/unit, tests/integration, tests/fixtures
- [X] T008 Create main.py entry point file
- [X] T009 Create __init__.py files in all source subdirectories

## Phase 2: Foundational Components

**Goal**: Implement core utilities and configuration management

- [X] T010 [P] Create config_loader.py in src/utils to load environment variables
- [X] T011 [P] Create retry_handler.py in src/utils for handling network errors
- [X] T012 [P] Create id_generator.py in src/utils for generating stable chunk IDs
- [X] T013 Create base data models for entities (TextChunk, CrawledPage, etc.)

## Phase 3: User Story 1 - Crawl and Ingest Book Content (Priority: P1)

**Goal**: Implement URL discovery and text extraction from Docusaurus-based book websites

**Independent Test**: Run the crawler against a sample Docusaurus site and verify that clean text content is extracted without navigation elements, headers, footers, or other non-content parts.

- [X] T014 [P] [US1] Create url_discovery.py in src/crawler to identify all public URLs from a Docusaurus site
- [X] T015 [P] [US1] Create docusaurus_crawler.py in src/crawler to crawl identified URLs
- [X] T016 [P] [US1] Create content_extractor.py in src/text_processor to extract clean text from HTML
- [X] T017 [US1] Implement logic to preserve document hierarchy and section headings
- [X] T018 [US1] Add error handling for broken links or inaccessible pages
- [ ] T019 [US1] Implement basic text extraction test with sample Docusaurus page
- [ ] T020 [US1] Test crawling of nested sections and subsections
- [ ] T021 [US1] Verify content extraction excludes navigation, headers, footers
- [ ] T022 [US1] Implement URL validation and status tracking

## Phase 4: User Story 2 - Generate and Store Embeddings (Priority: P2)

**Goal**: Convert extracted text content into vector embeddings using Cohere models and store in Qdrant Cloud

**Independent Test**: Provide a sample text chunk and verify that a valid embedding vector is generated and stored in Qdrant with associated metadata.

**Depends on**: User Story 1 completion

- [X] T023 [P] [US2] Create cohere_client.py in src/embeddings to integrate with Cohere API
- [X] T024 [P] [US2] Create embedding_generator.py in src/embeddings to convert text to vectors
- [X] T025 [P] [US2] Create qdrant_client.py in src/storage to integrate with Qdrant Cloud
- [X] T026 [US2] Create vector_storage.py in src/storage to manage vector storage
- [X] T027 [US2] Implement embedding generation from TextChunk objects
- [X] T028 [US2] Store vectors with metadata (source URL, page title, section heading, chunk index)
- [ ] T029 [US2] Test embedding generation with sample text chunks
- [ ] T030 [US2] Test vector storage and retrieval from Qdrant
- [ ] T031 [US2] Verify metadata preservation in stored vectors
- [ ] T032 [US2] Implement rate limiting for Cohere API calls

## Phase 5: User Story 3 - Manage Content Chunking and IDs (Priority: P3)

**Goal**: Implement deterministic text chunking with stable chunk IDs for idempotent pipeline execution

**Independent Test**: Run the pipeline multiple times and verify that identical content produces the same chunk IDs and no duplicates are stored.

**Depends on**: User Story 1 completion

- [X] T033 [P] [US3] Create chunker.py in src/text_processor for deterministic text chunking
- [X] T034 [P] [US3] Enhance id_generator.py to create stable chunk IDs based on content
- [X] T035 [US3] Implement content hashing for duplicate detection
- [X] T036 [US3] Modify text processing to use chunking with stable IDs
- [X] T037 [US3] Implement idempotent storage to prevent duplicate vectors
- [ ] T038 [US3] Test multiple pipeline runs with identical content
- [ ] T039 [US3] Verify no duplicate vectors are stored for unchanged content
- [ ] T040 [US3] Test handling of updated content (only new/modified chunks processed)
- [ ] T041 [US3] Implement chunk size and overlap configuration options

## Phase 6: Main Pipeline Integration

**Goal**: Integrate all components into a single main() function orchestrating the full pipeline

- [X] T042 Update main.py to orchestrate URL discovery → text extraction → chunking → embedding generation → vector storage
- [X] T043 Add command-line argument parsing for URL and collection name
- [X] T044 Implement processing job tracking with status updates
- [X] T045 Add progress tracking and logging
- [X] T046 Create ProcessingJob model to track pipeline execution
- [X] T047 Implement comprehensive error handling across the pipeline

## Phase 7: Testing and Verification

**Goal**: Implement tests and verification mechanisms

- [ ] T048 Create unit tests for crawler components
- [ ] T049 Create unit tests for text processor components
- [ ] T050 Create unit tests for embedding generation components
- [ ] T051 Create unit tests for storage components
- [ ] T052 Create integration test for end-to-end pipeline
- [ ] T053 Implement vector retrieval verification by collection name
- [ ] T054 Test pipeline performance with sample book (100-500 pages)
- [ ] T055 Verify 99% URL crawl success rate
- [ ] T056 Test idempotent behavior with multiple runs

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Final touches and cross-cutting functionality

- [X] T057 Add comprehensive logging throughout the pipeline
- [X] T058 Implement memory usage optimization for large documents
- [X] T059 Add network connectivity issue handling
- [X] T060 Create documentation for the pipeline usage
- [X] T061 Add configuration options for chunk size, overlap, and other parameters
- [X] T062 Implement graceful shutdown and cleanup
- [ ] T063 Add metrics collection for pipeline performance
- [ ] T064 Final integration testing with real Docusaurus site
- [ ] T065 Update quickstart guide with final usage instructions