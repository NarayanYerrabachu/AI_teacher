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

from .config import Config, setup_logging
from .models import StatusResponse, WebPageRequest, QueryResponse, QueryRequest, ChatRequest, ChatResponse, StudioGenerateRequest, StudioGenerateResponse, ExplanationGenerateRequest, ExplanationGenerateResponse
from .simple_chat_service import SimpleChatService
from .hybrid_chat_service import HybridChatService
from .studio_service import StudioService

# Import design patterns
# TEMPORARILY DISABLED due to memory allocation error in sentence-transformers
# from patterns import (
#     DocumentLoaderFactory,
#     EmbeddingFactory,
#     ChunkingContext,
#     RecursiveChunkingStrategy,
#     create_vector_repository,
#     VectorStoreManagerSingleton
# )

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Validate config
try:
    Config.validate()
    # Always set OPENAI_API_KEY if configured (needed for both embeddings and LLM)
    if Config.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        logger.info("OpenAI API key loaded")

    if Config.USE_OPENAI_EMBEDDINGS:
        logger.info("Using OpenAI embeddings")
    else:
        logger.info("Using FREE local HuggingFace embeddings")
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

# Initialize components using Design Patterns
# TEMPORARILY DISABLED - will use simple loaders directly

# # Singleton Pattern - Vector Store Manager (ensures single instance)
# vector_manager = VectorStoreManagerSingleton()

# # Repository Pattern - Clean data access layer
# vector_repository = create_vector_repository(
#     repository_type="chroma",
#     vector_store_manager=vector_manager
# )

# # Strategy Pattern - Chunking strategy (can be changed at runtime)
# chunking_context = ChunkingContext(
#     RecursiveChunkingStrategy(
#         chunk_size=Config.CHUNK_SIZE,
#         chunk_overlap=Config.CHUNK_OVERLAP
#     )
# )

# Chat service - Using Hybrid Agent (PDF + Web Search)
# Switch between SimpleChatService (PDF only) and HybridChatService (PDF + Web)
USE_HYBRID = os.getenv("USE_HYBRID_AGENT", "true").lower() == "true"

if USE_HYBRID:
    try:
        chat_service = HybridChatService()
        logger.info("✅ Using HybridChatService (PDF + Web Search with LangGraph)")
    except Exception as e:
        logger.warning(f"Failed to initialize HybridChatService: {e}")
        logger.info("Falling back to SimpleChatService (PDF only)")
        chat_service = SimpleChatService()
else:
    chat_service = SimpleChatService()
    logger.info("Using SimpleChatService (PDF only)")

# Initialize Studio Service
studio_service = StudioService()
logger.info("StudioService initialized")

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
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from .vector_store import VectorStoreManager

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
        all_documents = []
        for pdf_path in pdf_paths:
            try:
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                all_documents.extend(documents)
                logger.info(f"Loaded {len(documents)} pages from {Path(pdf_path).name}")
            except Exception as e:
                logger.error(f"Error loading {pdf_path}: {e}")
                raise HTTPException(status_code=400, detail=f"Error loading {Path(pdf_path).name}: {str(e)}")

        if not all_documents:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the PDFs"
            )

        logger.info(
            f"Loaded {len(all_documents)} pages with total characters: {sum(len(doc.page_content) for doc in all_documents)}")

        # Chunk documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(all_documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks created from documents. Documents may be empty."
            )

        total_chunks = len(chunks)
        logger.info(f"Created {total_chunks} chunks")

        # Add to vector store in small batches to avoid memory issues
        import gc
        vector_manager = VectorStoreManager()
        BATCH_SIZE = 20  # Process only 20 chunks at a time

        try:
            # Try to load existing store
            vectorstore = vector_manager.load_vector_store()
            action = "updated"
        except:
            # Create new store with first batch
            first_batch = chunks[:BATCH_SIZE]
            vectorstore = vector_manager.create_vector_store(first_batch)
            action = "created"
            chunks = chunks[BATCH_SIZE:]  # Remove processed chunks
            logger.info(f"Created vector store with {len(first_batch)} chunks")
            gc.collect()  # Force garbage collection

        # Add remaining chunks in batches
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i+BATCH_SIZE]
            logger.info(f"Processing batch {i//BATCH_SIZE + 1}: {len(batch)} chunks")
            vector_manager.add_documents(vectorstore, batch)
            gc.collect()  # Force garbage collection after each batch

        logger.info(f"Successfully processed {len(files)} PDFs. Vector store {action}.")
        return StatusResponse(
            status="success",
            message=f"PDFs processed successfully. Vector store {action}.",
            details={
                "files_processed": len(files),
                "total_chunks": total_chunks,
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
        # Load web pages using WebBaseLoader
        from langchain_community.document_loaders import WebBaseLoader

        all_documents = []
        for url in urls:
            try:
                web_loader = WebBaseLoader(url)
                documents = web_loader.load()
                all_documents.extend(documents)
                logger.info(f"Loaded content from {url}")
            except Exception as e:
                logger.error(f"Error loading {url}: {e}")
                raise HTTPException(status_code=400, detail=f"Error loading {url}: {str(e)}")

        if not all_documents:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the URLs"
            )

        # Strategy Pattern: Chunk documents using configured strategy
        chunks = chunking_context.chunk_documents(all_documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks created from documents. Documents may be empty."
            )

        logger.info(f"Created {len(chunks)} chunks using {chunking_context.strategy.__class__.__name__}")

        # Repository Pattern: Add documents to vector store
        vector_repository.add_documents(chunks)

        logger.info(f"Successfully processed {len(urls)} web pages. Vector store updated.")
        return StatusResponse(
            status="success",
            message=f"Web pages processed successfully. Vector store updated.",
            details={
                "urls_processed": len(urls),
                "total_chunks": len(chunks),
                "urls": urls
            }
        )

    except HTTPException:
        raise
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
        # Repository Pattern: Search for similar documents
        results = vector_repository.search(request.query, k=request.k)

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
    - **image_data**: Optional base64 encoded image
    - **extracted_text**: Optional OCR extracted text from image
    """
    logger.info(f"Received chat request: '{request.message[:50]}...' with RAG={request.use_rag}")
    if request.image_data:
        logger.info("Chat request includes image data")
    try:
        # Check if it's HybridChatService
        if isinstance(chat_service, HybridChatService):
            response, session_id, sources_dict = await chat_service.chat(
                message=request.message,
                session_id=request.session_id,
                use_hybrid=request.use_rag,
                image_data=request.image_data,
                extracted_text=request.extracted_text
            )
            # Extract flat sources list from dict for ChatResponse model
            sources = sources_dict.get("sources", []) if sources_dict else []
        else:
            # SimpleChatService doesn't support image yet, just use message
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
    - **image_data**: Optional base64 encoded image
    - **extracted_text**: Optional OCR extracted text from image
    """
    logger.info(f"Received streaming chat request: '{request.message[:50]}...'")
    if request.image_data:
        logger.info("Streaming chat request includes image data")

    async def event_generator():
        try:
            # Check if it's HybridChatService or SimpleChatService
            if isinstance(chat_service, HybridChatService):
                async for chunk, session_id, sources in chat_service.chat_stream(
                    message=request.message,
                    session_id=request.session_id,
                    use_hybrid=request.use_rag,  # HybridChatService uses use_hybrid
                    image_data=request.image_data,
                    extracted_text=request.extracted_text
                ):
                    # Send text chunks
                    if chunk:
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

                    # Send sources in final message
                    if sources is not None:
                        logger.info(f"📡 Sending sources to frontend - keys: {list(sources.keys())}")
                        logger.info(f"📡 Has explanation_animation: {('explanation_animation' in sources)}, has explanation_audio: {('explanation_audio' in sources)}")
                        if 'explanation_animation' in sources:
                            logger.info(f"📡 Animation has {len(sources['explanation_animation'].get('steps', []))} steps")
                        yield f"data: {json.dumps({'type': 'sources', 'sources': sources, 'session_id': session_id})}\n\n"
            else:
                async for chunk, session_id, sources in chat_service.chat_stream(
                    message=request.message,
                    session_id=request.session_id,
                    use_rag=request.use_rag  # SimpleChatService uses use_rag
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


@app.post("/explanation/generate", response_model=ExplanationGenerateResponse)
async def generate_explanation(request: ExplanationGenerateRequest):
    """
    Generate animated explanation for a message on-demand

    - **message**: The user's question
    - **answer**: The assistant's answer
    """
    logger.info(f"Generating explanation for question: '{request.message[:50]}...'")

    try:
        # Only HybridChatService has the explanation generation method
        if not isinstance(chat_service, HybridChatService):
            return ExplanationGenerateResponse(
                success=False,
                message="Explanation generation not available with current chat service"
            )

        explanation = await chat_service.generate_explanation(
            message=request.message,
            answer=request.answer
        )

        if explanation:
            logger.info("✓ Explanation generated successfully")
            return ExplanationGenerateResponse(
                success=True,
                animation=explanation["animation"],
                audio=explanation["audio"],
                duration=explanation["duration"],
                message="Explanation generated successfully"
            )
        else:
            logger.info("No explanation generated (not applicable for this message)")
            return ExplanationGenerateResponse(
                success=False,
                message="Explanation not applicable for this message type"
            )

    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}", exc_info=True)
        return ExplanationGenerateResponse(
            success=False,
            message=f"Error generating explanation: {str(e)}"
        )


@app.post("/studio/generate", response_model=StudioGenerateResponse)
async def generate_studio_content(request: StudioGenerateRequest):
    """
    Generate Studio content (summary, quiz, flashcards, report, or analyzemap)

    - **session_id**: Session ID to generate content from
    - **content_type**: Type of content to generate ("summary", "quiz", "flashcards", "report", "analyzemap")
    """
    logger.info(f"Generating {request.content_type} for session {request.session_id}")

    try:
        # Get conversation history from chat service
        history = chat_service.get_session_history(request.session_id)

        if not history:
            raise HTTPException(status_code=404, detail="Session not found or empty")

        # Generate content based on type
        if request.content_type == "summary":
            result = await studio_service.generate_summary(history, request.session_id)
        elif request.content_type == "quiz":
            result = await studio_service.generate_quiz(history, request.session_id)
        elif request.content_type == "flashcards":
            result = await studio_service.generate_flashcards(history, request.session_id)
        elif request.content_type == "report":
            result = await studio_service.generate_report(history, request.session_id)
        elif request.content_type == "analyzemap":
            result = await studio_service.generate_analyze_map(history, request.session_id)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid content_type: {request.content_type}")

        logger.info(f"Successfully generated {request.content_type} for session {request.session_id}")

        return StudioGenerateResponse(
            success=True,
            data=result,
            message=f"{request.content_type.capitalize()} generated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating studio content: {str(e)}", exc_info=True)
        return StudioGenerateResponse(
            success=False,
            data={},
            message=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server...")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )