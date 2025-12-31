# Data Model: RAG Retrieval and Validation

## Key Entities

### Query
- **Description**: A natural language input from a user that needs to be matched against stored vectors
- **Fields**:
  - `text`: string - The natural language query text
  - `embedding`: list[float] - Vector representation of the query
  - `collection_name`: string - Name of the Qdrant collection to search
  - `top_k`: int - Number of results to retrieve (default: 5)
- **Validation Rules**:
  - `text` must not be empty
  - `top_k` must be positive integer
  - `collection_name` must be valid Qdrant collection name format

### RetrievedChunk
- **Description**: A text segment returned by the similarity search, including content, source metadata, and similarity score
- **Fields**:
  - `content`: string - The text content of the chunk
  - `source_url`: string - Original URL where the content was found
  - `page_title`: string - Title of the original page
  - `section_hierarchy`: string - Section hierarchy in the original document
  - `chunk_index`: int - Position of the chunk in the original text
  - `similarity_score`: float - Similarity score between query and chunk
  - `vector_id`: string - Unique identifier of the stored vector
- **Validation Rules**:
  - `content` must not be empty
  - `similarity_score` must be between 0 and 1
  - `source_url` must be a valid URL format
  - All metadata fields must be present

### QueryEmbedding
- **Description**: The vector representation of a user query generated using Cohere models
- **Fields**:
  - `vector`: list[float] - The embedding vector (dimension depends on Cohere model)
  - `model`: string - The model used to generate the embedding
  - `query_text`: string - Original text that was embedded
- **Validation Rules**:
  - `vector` must have consistent dimensions with stored embeddings
  - `model` must match the model used for stored embeddings

### ValidationResult
- **Description**: The outcome of a validation check, including success/failure status and detailed metrics
- **Fields**:
  - `success`: bool - Whether the validation passed
  - `message`: string - Description of validation result
  - `metrics`: dict - Additional metrics about the validation
  - `retrieved_chunks`: list[RetrievedChunk] - Chunks returned by the retrieval
  - `query`: Query - The original query used for validation
- **Validation Rules**:
  - `success` must be boolean
  - `message` must be non-empty when success is false
  - `retrieved_chunks` must match expected count when success is true

## Relationships
- A `Query` produces one `QueryEmbedding`
- A `QueryEmbedding` retrieves multiple `RetrievedChunk` objects
- A `ValidationResult` contains a `Query` and multiple `RetrievedChunk` objects
- Multiple `RetrievedChunk` objects can originate from the same source document