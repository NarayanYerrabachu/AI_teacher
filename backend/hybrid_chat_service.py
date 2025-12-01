"""Enhanced chat service with hybrid PDF + Web search using LangGraph"""

import logging
import uuid
import os
from typing import List, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI

from .config import Config
from .hybrid_agent import HybridRAGAgent

logger = logging.getLogger(__name__)


class HybridChatService:
    """
    Chat service with hybrid RAG (PDF + Web search) using LangGraph agent
    """

    def __init__(self):
        """Initialize hybrid chat service"""
        self.agent = HybridRAGAgent()
        self.sessions: Dict[str, List[Dict]] = {}
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("HybridChatService initialized with LangGraph agent")

    def _get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, List[Dict]]:
        """Get existing session or create new one"""
        if not session_id or session_id not in self.sessions:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = []
            logger.info(f"Created new chat session: {session_id}")
        return session_id, self.sessions[session_id]

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        use_hybrid: bool = True
    ) -> tuple[str, str, Optional[Dict]]:
        """
        Process a chat message with hybrid search

        Args:
            message: User's message
            session_id: Optional session ID
            use_hybrid: Whether to use hybrid agent (True) or basic mode (False)

        Returns:
            tuple: (response, session_id, sources_dict)
        """
        session_id, history = self._get_or_create_session(session_id)

        try:
            if use_hybrid:
                # Use the hybrid agent with conversation history
                result = self.agent.query(message, conversation_history=history)

                response = result["answer"]

                # Format sources for frontend
                pdf_sources = result["sources"]["pdf"]
                web_sources = result["sources"]["web"]

                sources_dict = {
                    "route_used": result["route_used"],
                    "pdf_sources": pdf_sources,
                    "web_sources": web_sources,
                    "sources": pdf_sources + web_sources,  # Flat array for Knowledge Map
                    "total_sources": len(pdf_sources) + len(web_sources),
                    "has_pdf": result["has_pdf_context"],
                    "has_web": result["has_web_context"]
                }

            else:
                # Basic mode without agent (for testing)
                from simple_chat_service import SimpleChatService
                simple_service = SimpleChatService()
                response, session_id, sources = await simple_service.chat(
                    message, session_id, use_rag=True
                )
                sources_dict = {"pdf_sources": sources or [], "web_sources": []}

            # Update session history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})

            logger.info(f"Chat response generated for session {session_id}")
            return response, session_id, sources_dict

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            raise

    async def chat_stream(
        self,
        message: str,
        session_id: Optional[str] = None,
        use_hybrid: bool = True
    ) -> AsyncGenerator[tuple[str, str, Optional[Dict]], None]:
        """
        Stream chat response with hybrid search

        Args:
            message: User's message
            session_id: Optional session ID
            use_hybrid: Whether to use hybrid agent

        Yields:
            tuple: (chunk, session_id, sources_dict) - sources only in last chunk
        """
        session_id, history = self._get_or_create_session(session_id)
        full_response = ""
        sources_dict = None

        try:
            if use_hybrid:
                # Get agent response with conversation history (non-streaming for now)
                result = self.agent.query(message, conversation_history=history)

                response = result["answer"]

                # Format sources - combine PDF and web sources into flat array for Knowledge Map
                pdf_sources = result["sources"]["pdf"]
                web_sources = result["sources"]["web"]

                sources_dict = {
                    "route_used": result["route_used"],
                    "pdf_sources": pdf_sources,
                    "web_sources": web_sources,
                    "sources": pdf_sources + web_sources,  # Flat array for Knowledge Map
                    "total_sources": len(pdf_sources) + len(web_sources),
                    "has_pdf": result["has_pdf_context"],
                    "has_web": result["has_web_context"]
                }

                # Simulate streaming while preserving newlines
                import asyncio
                import re

                # Split on spaces but preserve newlines
                parts = re.split(r'( |\n)', response)
                for part in parts:
                    if part:  # Skip empty strings
                        full_response += part
                        yield part, session_id, None

                        # Small delay only for words, not for newlines
                        if part not in [' ', '\n']:
                            await asyncio.sleep(0.02)

            else:
                # Fallback to simple service
                from simple_chat_service import SimpleChatService
                simple_service = SimpleChatService()

                async for chunk, sid, sources in simple_service.chat_stream(
                    message, session_id, use_rag=True
                ):
                    full_response += chunk if chunk else ""
                    yield chunk, sid, sources

                sources_dict = {"pdf_sources": sources or [], "web_sources": []}
                session_id = sid

            # Update session history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": full_response})

            # Send sources in final message
            yield "", session_id, sources_dict

        except Exception as e:
            logger.error(f"Error in streaming chat: {str(e)}", exc_info=True)

            # Error fallback
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            for word in error_response.split():
                yield word + " ", session_id, None

            yield "", session_id, {"error": str(e)}

    def clear_session(self, session_id: str) -> bool:
        """Clear a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared chat session: {session_id}")
            return True
        return False

    def get_session_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Get chat history for a session"""
        return self.sessions.get(session_id)


# Testing
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def test():
        service = HybridChatService()

        # Test queries
        queries = [
            "What are rational numbers?",  # PDF
            "What's the latest in AI research?",  # Web
            "Hello!",  # Greeting
        ]

        for query in queries:
            logger.info(f"\n{'='*80}")
            logger.info(f"Query: {query}")
            logger.info(f"{'='*80}\n")

            logger.info("Streaming response:")
            response_parts = []
            async for chunk, session_id, sources in service.chat_stream(query):
                response_parts.append(chunk)
                # For demo purposes, still print chunks for real-time display
                print(chunk, end="", flush=True)

            if sources:
                logger.info(f"\n\nSources: {sources}")
            logger.info("")

    asyncio.run(test())
