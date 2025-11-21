"""Simple chat service without problematic LangChain dependencies"""

import logging
import uuid
import os
from typing import List, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI

from config import Config
from vector_store import VectorStoreManager

logger = logging.getLogger(__name__)


class SimpleChatService:
    """Lightweight chat service using direct OpenAI API calls"""

    def __init__(self):
        self.vector_manager = VectorStoreManager()
        self.sessions: Dict[str, List[Dict]] = {}  # Simple dict-based session storage
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("SimpleChatService initialized")

    def _get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, List[Dict]]:
        """Get existing session or create new one"""
        if not session_id or session_id not in self.sessions:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = []
            logger.info(f"Created new chat session: {session_id}")
        return session_id, self.sessions[session_id]

    def _format_messages(self, history: List[Dict], new_message: str, context: Optional[str] = None) -> List[Dict]:
        """Format messages for OpenAI API"""
        messages = []

        # System message with context if using RAG
        if context == "NO_DOCUMENTS_FOUND":
            # No relevant documents found - instruct to refuse
            system_content = """You are a helpful AI assistant that ONLY answers questions based on a knowledge base.

The knowledge base does not contain any information relevant to the user's question.

You MUST respond with: "I don't have information about that in my knowledge base. I can only answer questions based on the documents provided to me."

DO NOT use your general knowledge or provide any other answer."""
            messages.append({"role": "system", "content": system_content})
        elif context:
            system_content = f"""You are an AI teacher assistant with access to educational materials.

CONTEXT PROVIDED:
{context}

INSTRUCTIONS:
1. The context above was retrieved from the knowledge base and is RELEVANT to the user's question
2. Use the information from the context to answer the question
3. You can explain and elaborate using your knowledge, but stay grounded in what the context says
4. Use simple text formatting: write fractions as 3/2, not \\frac{{3}}{{2}}
5. If the user is quoting or asking about text that appears in the context, acknowledge it and provide helpful information

ONLY refuse to answer if the context is completely unrelated or empty.

Now answer the user's question based on the context above."""
            messages.append({"role": "system", "content": system_content})
        else:
            messages.append({"role": "system", "content": "You are a helpful AI assistant."})

        # Add conversation history (last N messages)
        recent_history = history[-Config.MAX_HISTORY_MESSAGES*2:] if history else []
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add new message
        messages.append({"role": "user", "content": new_message})

        return messages

    async def chat(self, message: str, session_id: Optional[str] = None, use_rag: bool = True) -> tuple[str, str, Optional[List[dict]]]:
        """
        Process a chat message

        Returns:
            tuple: (response, session_id, sources)
        """
        session_id, history = self._get_or_create_session(session_id)
        sources = None
        context = None

        try:
            # Get context from RAG if enabled
            if use_rag:
                try:
                    vectorstore = self.vector_manager.load_vector_store()
                    docs = vectorstore.similarity_search(message, k=Config.DEFAULT_SEARCH_K)

                    if docs:
                        context = "\n\n".join([doc.page_content for doc in docs])
                        sources = [
                            {
                                "content": doc.page_content[:200] + "...",
                                "metadata": doc.metadata
                            }
                            for doc in docs
                        ]
                        logger.info(f"Context preview (first 500 chars): {context[:500]}")
                    else:
                        # No documents found - RAG mode should not answer
                        logger.info("No documents found in vector store for RAG query")
                        context = "NO_DOCUMENTS_FOUND"
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}, treating as no documents available")
                    context = "NO_DOCUMENTS_FOUND"

            # Format messages and get response
            messages = self._format_messages(history, message, context)
            completion = await self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=Config.LLM_TEMPERATURE
            )
            response = completion.choices[0].message.content

            # Update session history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})

            logger.info(f"Chat response generated for session {session_id}")
            return response, session_id, sources

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            raise

    async def chat_stream(self, message: str, session_id: Optional[str] = None, use_rag: bool = True) -> AsyncGenerator[tuple[str, str, Optional[List[dict]]], None]:
        """
        Stream chat response

        Yields:
            tuple: (chunk, session_id, sources) - sources only in last chunk
        """
        session_id, history = self._get_or_create_session(session_id)
        sources = None
        context = None
        full_response = ""

        try:
            # Get context from RAG if enabled
            if use_rag:
                try:
                    vectorstore = self.vector_manager.load_vector_store()
                    docs = vectorstore.similarity_search(message, k=Config.DEFAULT_SEARCH_K)
                    logger.info(f"Similarity search found {len(docs)} documents for query: '{message[:50]}'")
                    if docs:
                        doc_sources = [doc.metadata.get('source', 'unknown') for doc in docs]
                        logger.info(f"Document sources: {doc_sources}")

                    if docs:
                        context = "\n\n".join([doc.page_content for doc in docs])
                        sources = [
                            {
                                "content": doc.page_content[:200] + "...",
                                "metadata": doc.metadata
                            }
                            for doc in docs
                        ]
                        logger.info(f"Using {len(docs)} documents as context")
                        logger.info(f"Context preview (first 500 chars): {context[:500]}")
                    else:
                        # No documents found - RAG mode should not answer
                        logger.info("No documents found in vector store for RAG query")
                        context = "NO_DOCUMENTS_FOUND"
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}, treating as no documents available")
                    context = "NO_DOCUMENTS_FOUND"

            # Format messages and stream response
            messages = self._format_messages(history, message, context)

            stream = await self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=Config.LLM_TEMPERATURE,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content, session_id, None

            # Update session history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_response})

            # Send sources in final message
            yield "", session_id, sources

        except Exception as e:
            logger.error(f"Error in streaming chat: {str(e)}", exc_info=True)
            # Fallback demo mode when OpenAI is unavailable
            if "503" in str(e) or "Service Temporarily Unavailable" in str(e):
                logger.warning("OpenAI unavailable, using demo mode")
                demo_response = f"I'm currently in demo mode as the AI service is temporarily unavailable. Your question was: '{message[:50]}...' In demo mode, I can show you the mindmap feature working with mock data. Try uploading documents and asking questions to see the knowledge graph populate!"

                # Create mock sources for demonstration
                demo_sources = [
                    {
                        "content": "This is a demo source document. In normal mode, this would show actual content from your uploaded PDFs...",
                        "metadata": {"source": "demo_document.pdf", "page": 1}
                    },
                    {
                        "content": "Another demo source showing how the mindmap connects multiple sources...",
                        "metadata": {"source": "demo_document.pdf", "page": 2}
                    }
                ]

                # Stream the demo response
                for word in demo_response.split():
                    yield word + " ", session_id, None
                    import asyncio
                    await asyncio.sleep(0.05)

                # Update session history
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": demo_response})

                # Send sources
                yield "", session_id, demo_sources
            else:
                raise

    def clear_session(self, session_id: str) -> bool:
        """Clear a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared chat session: {session_id}")
            return True
        return False

    def get_session_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Get chat history for a session"""
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id]
