"""Simple chat service without problematic LangChain dependencies"""

import logging
import uuid
import os
from typing import List, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI

from .config import Config
from .vector_store import VectorStoreManager

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
            # No relevant documents found - but allow greetings and test messages
            system_content = """You are an AI teacher assistant with access to educational materials (Mathematics and English Class 9 textbooks).

IMPORTANT: The knowledge base does NOT contain any information relevant to the user's question.

INSTRUCTIONS:
1. If the user's message is a greeting (hello, hi, hey) or test message (test, testing, AI test, etc.):
   - Respond warmly and introduce yourself
   - Mention that you can help with Mathematics and English Beehive textbook questions for Class 9
   - Encourage them to ask about specific topics, chapters, or lessons

2. If the user asks a substantive question about topics NOT in the textbooks (e.g., history, science, current events):
   - Politely explain that you can only answer questions about the Mathematics and English textbooks
   - Suggest they ask about specific topics from those subjects

3. DO NOT use your general knowledge to answer questions outside the textbooks."""
            messages.append({"role": "system", "content": system_content})
        elif context:
            system_content = f"""You are an AI teacher assistant with access to Mathematics and English Beehive textbooks for Class 9.

CONTEXT FROM KNOWLEDGE BASE:
{context}

INSTRUCTIONS:
1. The context above has been retrieved from the textbooks because it matches the user's question
2. Use the information from the context to answer the question
3. If the user asks about a chapter, lesson, poem, or topic:
   - Check if the context contains information about it
   - If yes, provide a helpful answer based on the context
   - You can explain, summarize, and provide insights based on what's in the context
4. Use simple, clear language appropriate for Class 9 students
5. Format mathematical expressions simply: use 3/2 instead of \\frac{{3}}{{2}}

If the context seems completely unrelated to the question (e.g., mathematics content for a question about English literature), then politely indicate that the retrieved context doesn't match the question topic.

Now answer the user's question based on the context provided."""
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
                    # Use similarity_search_with_relevance_scores to get scores
                    results = vectorstore.similarity_search_with_relevance_scores(message, k=Config.DEFAULT_SEARCH_K)

                    # Filter by relevance threshold (0.2 = 20% similarity minimum - allows chapter title queries)
                    RELEVANCE_THRESHOLD = 0.2
                    relevant_docs = [(doc, score) for doc, score in results if score >= RELEVANCE_THRESHOLD]

                    if relevant_docs:
                        # We have relevant documents
                        docs = [doc for doc, score in relevant_docs]
                        context = "\n\n".join([doc.page_content for doc in docs])
                        sources = [
                            {
                                "content": doc.page_content[:200] + "...",
                                "metadata": doc.metadata,
                                "relevance_score": f"{score:.2f}"
                            }
                            for doc, score in relevant_docs
                        ]
                        logger.info(f"Found {len(relevant_docs)} relevant documents (scores: {[f'{s:.2f}' for _, s in relevant_docs]})")
                        logger.info(f"Context preview (first 500 chars): {context[:500]}")
                    else:
                        # No relevant documents found - RAG mode should not answer
                        logger.info(f"No relevant documents found (best score: {results[0][1]:.2f} < threshold {RELEVANCE_THRESHOLD})")
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
                    # Use similarity_search_with_relevance_scores to get scores
                    results = vectorstore.similarity_search_with_relevance_scores(message, k=Config.DEFAULT_SEARCH_K)

                    # Filter by relevance threshold (0.2 = 20% similarity minimum - allows chapter title queries)
                    RELEVANCE_THRESHOLD = 0.2
                    relevant_docs = [(doc, score) for doc, score in results if score >= RELEVANCE_THRESHOLD]

                    if relevant_docs:
                        # We have relevant documents
                        docs = [doc for doc, score in relevant_docs]
                        context = "\n\n".join([doc.page_content for doc in docs])
                        sources = [
                            {
                                "content": doc.page_content[:200] + "...",
                                "metadata": doc.metadata,
                                "relevance_score": f"{score:.2f}"
                            }
                            for doc, score in relevant_docs
                        ]
                        logger.info(f"Found {len(relevant_docs)} relevant documents (scores: {[f'{s:.2f}' for _, s in relevant_docs]})")
                        logger.info(f"Context preview (first 500 chars): {context[:500]}")
                    else:
                        # No relevant documents found - RAG mode should not answer
                        logger.info(f"No relevant documents found (best score: {results[0][1]:.2f} < threshold {RELEVANCE_THRESHOLD})")
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
