"""FastAPI application for document processing"""

import os
import logging
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import json
import shutil
from pathlib import Path

from config import Config, setup_logging
# from ocr_document_loader import OCRDocumentLoader  # TEMP: Causes std::bad_alloc with langchain_community
from simple_document_loader import SimplePDFLoader
from simple_chunker import SimpleDocumentChunker
from models import StatusResponse, WebPageRequest, QueryResponse, QueryRequest, ChatRequest, ChatResponse
from vector_store import VectorStoreManager
from simple_chat_service import SimpleChatService

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Validate config
try:
    Config.validate()
    if Config.USE_OPENAI_EMBEDDINGS:
        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        logger.info("Using OpenAI embeddings - API key loaded")
    else:
        logger.info("Using FREE local HuggingFace embeddings - no API key needed!")
except ValueError as e:
    logger.error(str(e))
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing API",
    description="API for processing PDFs and web pages with LangChain and Chroma DB",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
loader = SimplePDFLoader()
chunker = SimpleDocumentChunker()
vector_manager = VectorStoreManager()
chat_service = SimpleChatService()

# Create uploads directory
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logger.info("Document Processing API initialized")


@app.on_event("startup")
async def startup_event():
    """Log startup event"""
    logger.info("FastAPI application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown event"""
    logger.info("FastAPI application shutting down")


@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return StatusResponse(
        status="success",
        message="Document Processing API is running",
        details={
            "endpoints": [
                "/docs - API documentation",
                "/health - Health check",
                "/test-embeddings - Test embeddings",
                "/upload-pdf - Upload and process PDF files",
                "/process-webpages - Process web pages from URLs",
                "/query - Query the vector store",
                "/chat - Chat with AI (with optional RAG)",
                "/chat/stream - Stream chat responses",
                "/chat/history/{session_id} - Get chat history",
                "/chat/clear/{session_id} - Clear chat session",
                "/clear-vector-store - Clear all documents"
            ]
        }
    )


@app.get("/health", response_model=StatusResponse)
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return StatusResponse(
        status="healthy",
        message="Service is operational"
    )


@app.get("/test-embeddings", response_model=StatusResponse)
async def test_embeddings():
    """Test if embeddings are working"""
    logger.info("Testing embeddings...")
    try:
        # Use the same embeddings as VectorStoreManager
        if Config.USE_OPENAI_EMBEDDINGS:
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
            embedding_type = "OpenAI"
        else:
            from langchain_huggingface import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL
            )
            embedding_type = f"HuggingFace ({Config.EMBEDDING_MODEL})"

        # Test embedding generation
        test_text = "This is a test sentence for embeddings."
        logger.info(f"Generating test embedding with {embedding_type}...")
        embedding = embeddings.embed_query(test_text)

        logger.info(f"Embedding test successful. Type: {embedding_type}, Dimension: {len(embedding)}")
        return StatusResponse(
            status="success",
            message="Embeddings are working correctly",
            details={
                "embedding_type": embedding_type,
                "embedding_dimension": len(embedding),
                "test_text": test_text
            }
        )
    except Exception as e:
        logger.error(f"Embedding test failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Embedding test failed: {str(e)}"
        )


@app.post("/upload-pdf", response_model=StatusResponse)
async def upload_pdf(files: List[UploadFile] = File(...)):
    """
    Upload and process PDF files

    - **files**: List of PDF files to upload and process
    """
    logger.info(f"Received request to upload {len(files)} PDF files")
    try:
        pdf_paths = []

        # Save uploaded files
        for file in files:
            if not file.filename.endswith('.pdf'):
                logger.warning(f"Rejected non-PDF file: {file.filename}")
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a PDF"
                )

            file_path = UPLOAD_DIR / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            pdf_paths.append(str(file_path))
            logger.info(f"Saved uploaded file: {file.filename}")

        # Load PDFs
        documents = loader.load_pdfs(pdf_paths)

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the PDFs"
            )

        logger.info(
            f"Loaded {len(documents)} pages with total characters: {sum(len(doc.page_content) for doc in documents)}")

        # Chunk documents
        chunks = chunker.chunk_documents(documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks created from documents. Documents may be empty."
            )

        logger.info(f"Created {len(chunks)} chunks")

        # Create or update vector store
        try:
            vectorstore = vector_manager.load_vector_store()
            vector_manager.add_documents(vectorstore, chunks)
            action = "updated"
        except Exception as load_error:
            logger.info(f"Creating new vector store (could not load existing: {str(load_error)})")
            vectorstore = vector_manager.create_vector_store(chunks)
            action = "created"

        logger.info(f"Successfully processed {len(files)} PDFs. Vector store {action}.")
        return StatusResponse(
            status="success",
            message=f"PDFs processed successfully. Vector store {action}.",
            details={
                "files_processed": len(files),
                "total_chunks": len(chunks),
                "filenames": [f.filename for f in files]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-webpages", response_model=StatusResponse)
async def process_webpages(request: WebPageRequest):
    """
    Process web pages from URLs

    - **urls**: List of URLs to process
    """
    urls = [str(url) for url in request.urls]
    logger.info(f"Received request to process {len(urls)} web pages")
    try:
        # Load web pages
        documents = loader.load_web_pages(urls)

        # Chunk documents
        chunks = chunker.chunk_documents(documents)

        # Create or update vector store
        try:
            vectorstore = vector_manager.load_vector_store()
            vector_manager.add_documents(vectorstore, chunks)
            action = "updated"
        except Exception:
            vectorstore = vector_manager.create_vector_store(chunks)
            action = "created"

        logger.info(f"Successfully processed {len(urls)} web pages. Vector store {action}.")
        return StatusResponse(
            status="success",
            message=f"Web pages processed successfully. Vector store {action}.",
            details={
                "urls_processed": len(urls),
                "total_chunks": len(chunks),
                "urls": urls
            }
        )

    except Exception as e:
        logger.error(f"Error processing web pages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_vector_store(request: QueryRequest):
    """
    Query the vector store for similar documents

    - **query**: Search query string
    - **k**: Number of results to return (default: 4)
    """
    logger.info(f"Received query request: '{request.query}' with k={request.k}")
    try:
        # Load vector store
        vectorstore = vector_manager.load_vector_store()

        # Perform query
        results = vector_manager.query(vectorstore, request.query, request.k)

        # Format results
        formatted_results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in results
        ]

        logger.info(f"Query completed successfully. Returning {len(formatted_results)} results")
        return QueryResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )

    except Exception as e:
        logger.error(f"Error querying vector store: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear-vector-store", response_model=StatusResponse)
async def clear_vector_store():
    """Clear the vector store (delete all documents)"""
    logger.warning("Received request to clear vector store")
    try:
        chroma_dir = Path(Config.CHROMA_PERSIST_DIR)

        if chroma_dir.exists():
            shutil.rmtree(chroma_dir)
            logger.info("Vector store cleared successfully")
            return StatusResponse(
                status="success",
                message="Vector store cleared successfully"
            )
        else:
            logger.info("Vector store was already empty")
            return StatusResponse(
                status="success",
                message="Vector store was already empty"
            )

    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI assistant

    - **message**: User message
    - **session_id**: Optional session ID for conversation continuity
    - **use_rag**: Whether to use RAG (default: true)
    """
    logger.info(f"Received chat request: '{request.message[:50]}...' with RAG={request.use_rag}")
    try:
        response, session_id, sources = await chat_service.chat(
            message=request.message,
            session_id=request.session_id,
            use_rag=request.use_rag
        )

        logger.info(f"Chat response generated for session {session_id}")
        return ChatResponse(
            response=response,
            session_id=session_id,
            sources=sources
        )

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the AI assistant

    - **message**: User message
    - **session_id**: Optional session ID for conversation continuity
    - **use_rag**: Whether to use RAG (default: true)
    """
    logger.info(f"Received streaming chat request: '{request.message[:50]}...'")

    async def event_generator():
        try:
            async for chunk, session_id, sources in chat_service.chat_stream(
                message=request.message,
                session_id=request.session_id,
                use_rag=request.use_rag
            ):
                # Send text chunks
                if chunk:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

                # Send sources in final message
                if sources is not None:
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources, 'session_id': session_id})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming chat: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    logger.info(f"Retrieving history for session {session_id}")
    try:
        history = chat_service.get_session_history(session_id)

        if history is None:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "history": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chat/clear/{session_id}", response_model=StatusResponse)
async def clear_chat_session(session_id: str):
    """Clear a chat session"""
    logger.info(f"Clearing session {session_id}")
    try:
        success = chat_service.clear_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return StatusResponse(
            status="success",
            message=f"Session {session_id} cleared successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )