# Quickstart: RAG Website Ingestion Pipeline

## Prerequisites

- Python 3.11+
- `uv` package manager installed
- Cohere API key
- Qdrant Cloud account and API key

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

3. **Install dependencies using uv**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_URL=your_qdrant_cluster_url
   ```

## Usage

### Run the ingestion pipeline

```bash
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name"
```

### Additional options

```bash
# With custom chunk size
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name" --chunk-size 1000

# With custom overlap
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name" --chunk-overlap 200

# Verbose logging
python main.py --url "https://your-docusaurus-book.com" --collection "your-book-name" --verbose
```

## Configuration

The pipeline can be configured via:
- Environment variables in `.env`
- Command-line arguments to `main.py`
- Optional configuration file (config.yaml)

## Verification

After running the pipeline, verify the results:
1. Check that all pages were crawled successfully
2. Verify vectors are stored in Qdrant collection
3. Test vector retrieval functionality

## Troubleshooting

- **API Rate Limits**: The pipeline includes built-in rate limiting and retry logic
- **Network Issues**: The pipeline handles network connectivity issues gracefully
- **Large Documents**: The chunking algorithm handles large documents by splitting them appropriately