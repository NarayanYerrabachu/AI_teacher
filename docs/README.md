# AI Teacher

A document processing API that leverages LangChain and ChromaDB to process, embed, and query documents from PDFs and web pages.

## Features

- PDF document processing and chunking
- Web page content extraction and processing
- Vector embeddings for semantic search
- Document querying with configurable parameters
- FastAPI-based REST API

## Architecture

The system consists of several components:

- **DocumentLoader**: Handles loading documents from PDFs and web pages
- **DocumentChunker**: Splits documents into manageable chunks
- **VectorStoreManager**: Manages the ChromaDB vector store operations
- **FastAPI Application**: Provides REST endpoints for document processing and querying

## Setup

### Prerequisites

- Python 3.8+
- Pipenv (for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AI_teacher.git
   cd AI_teacher
   ```

2. Install dependencies:
   ```bash
   pipenv install
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

### Running the Application

Start the FastAPI server:

```bash
uvicorn main:app -reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /`: Root endpoint, returns basic status
- `GET /health`: Health check endpoint
- `GET /test-embeddings`: Test the embedding functionality
- `POST /upload-pdf`: Upload and process PDF files
- `POST /process-webpages`: Process web pages from provided URLs
- `POST /query`: Query the vector store with natural language
- `DELETE /clear-vector-store`: Clear all documents from the vector store

## Usage Examples

### Upload and Process PDFs

```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf"
```

### Process Web Pages

```bash
curl -X POST "http://localhost:8000/process-webpages" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/page1", "https://example.com/page2"]}'
```

### Query Documents

```bash
curl -X POST "http://localhost:8000/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is LangChain?", "k": 3}'
```

## Configuration

The application's configuration is managed through the `Config` class in `config.py`. Key configurable parameters include:

- `CHUNK_SIZE`: Size of document chunks
- `CHUNK_OVERLAP`: Overlap between chunks
- `CHROMA_PERSIST_DIR`: Directory for ChromaDB persistence
- `DEFAULT_SEARCH_K`: Default number of results to return in queries

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
