# Quickstart: RAG Ingestion Pipeline for Docusaurus-based Book Content

## Prerequisites

- Python 3.11 or higher
- `uv` package manager installed
- Cohere API key
- Qdrant Cloud account and API credentials

## Setup

### 1. Clone and Navigate to Project
```bash
cd your-project-directory
```

### 2. Create Backend Directory
```bash
mkdir backend
cd backend
```

### 3. Initialize Project with uv
```bash
uv init
```

### 4. Install Dependencies
```bash
uv add requests beautifulsoup4 cohere qdrant-client python-dotenv tqdm
uv add --dev pytest pytest-mock black flake8
```

### 5. Create Environment File
Create `.env` file in the backend directory:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
CHUNK_SIZE=512
CHUNK_OVERLAP=50
BATCH_SIZE=10
```

**Note**: Never commit the `.env` file to version control. It should be gitignored.

## Configuration

### 1. Environment Variables
The following environment variables are required:

- `COHERE_API_KEY`: Your Cohere API key for embedding generation
- `QDRANT_URL`: Your Qdrant Cloud cluster URL
- `QDRANT_API_KEY`: Your Qdrant Cloud API key
- `CHUNK_SIZE`: Size of text chunks (default: 512)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `BATCH_SIZE`: Number of chunks to process at once (default: 10)

## Usage

### 1. Run the Ingestion Pipeline
```bash
cd backend
python main.py --urls "https://book.example.com/page1" "https://book.example.com/page2" "https://book.example.com/page3"
```

### 2. Alternative: Run with URLs from a file
Create a text file with URLs (one per line):
```txt
https://book.example.com/page1
https://book.example.com/page2
https://book.example.com/page3
```

Then run:
```bash
python main.py --url-file urls.txt
```

## Example Output
```
Starting ingestion pipeline for 3 URLs...
Processing: https://book.example.com/page1
✓ Extracted content (1,245 characters)
✓ Created 3 chunks
✓ Generated embeddings for all chunks
Processing: https://book.example.com/page2
✓ Extracted content (2,301 characters)
✓ Created 5 chunks
✓ Generated embeddings for all chunks
Processing: https://book.example.com/page3
✓ Extracted content (890 characters)
✓ Created 2 chunks
✓ Generated embeddings for all chunks
Ingestion completed! 10 chunks stored in Qdrant.
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your Cohere and Qdrant API keys are correct and have proper permissions
2. **URL Access Errors**: Verify that the URLs are accessible and return valid HTML content
3. **Rate Limiting**: If you encounter rate limiting, reduce the batch size or add delays between API calls

### Testing the Setup
Run the tests to verify your setup:
```bash
python -m pytest tests/
```

## Next Steps

1. Customize chunk size and overlap based on your content characteristics
2. Monitor the ingestion process and adjust batch size for optimal performance
3. Verify that embeddings are correctly stored in Qdrant and can be retrieved for RAG applications