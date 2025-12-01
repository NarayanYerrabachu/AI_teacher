"""Chat service with RAG integration"""

import logging
import uuid
from typing import List, Dict, Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

from .config import Config
from .vector_store import VectorStoreManager

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat with RAG capabilities"""

    def __init__(self):
        self.vector_manager = VectorStoreManager()
        self.sessions: Dict[str, ConversationBufferWindowMemory] = {}
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            streaming=True
        )

        # Custom prompt template for RAG
        self.qa_template = """You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Always be concise and helpful in your responses.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Helpful Answer:"""

        self.qa_prompt = PromptTemplate(
            template=self.qa_template,
            input_variables=["context", "chat_history", "question"]
        )

    def _get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, ConversationBufferWindowMemory]:
        """Get existing session or create new one"""
        if not session_id or session_id not in self.sessions:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = ConversationBufferWindowMemory(
                k=Config.MAX_HISTORY_MESSAGES,
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            logger.info(f"Created new chat session: {session_id}")
        return session_id, self.sessions[session_id]

    async def chat(self, message: str, session_id: Optional[str] = None, use_rag: bool = True) -> tuple[str, str, Optional[List[dict]]]:
        """
        Process a chat message with optional RAG

        Returns:
            tuple: (response, session_id, sources)
        """
        session_id, memory = self._get_or_create_session(session_id)
        sources = None

        try:
            if use_rag:
                # Load vector store and create retrieval chain
                vectorstore = self.vector_manager.load_vector_store()
                retriever = vectorstore.as_retriever(search_kwargs={"k": Config.DEFAULT_SEARCH_K})

                # Create conversational retrieval chain
                qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=retriever,
                    memory=memory,
                    return_source_documents=True,
                    combine_docs_chain_kwargs={"prompt": self.qa_prompt}
                )

                # Get response
                result = await qa_chain.ainvoke({"question": message})
                response = result["answer"]

                # Extract sources
                if result.get("source_documents"):
                    sources = [
                        {
                            "content": doc.page_content[:200] + "...",  # Truncate for brevity
                            "metadata": doc.metadata
                        }
                        for doc in result["source_documents"]
                    ]

            else:
                # Direct chat without RAG
                chat_history = memory.load_memory_variables({}).get("chat_history", [])
                messages = chat_history + [HumanMessage(content=message)]

                result = await self.llm.ainvoke(messages)
                response = result.content

                # Manually update memory
                memory.save_context({"question": message}, {"answer": response})

            logger.info(f"Chat response generated for session {session_id}")
            return response, session_id, sources

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            raise

    async def chat_stream(self, message: str, session_id: Optional[str] = None, use_rag: bool = True) -> AsyncGenerator[tuple[str, str, Optional[List[dict]]], None]:
        """
        Stream chat response with optional RAG

        Yields:
            tuple: (chunk, session_id, sources) - sources only in last chunk
        """
        session_id, memory = self._get_or_create_session(session_id)
        sources = None
        full_response = ""

        try:
            if use_rag:
                # Load vector store
                vectorstore = self.vector_manager.load_vector_store()
                retriever = vectorstore.as_retriever(search_kwargs={"k": Config.DEFAULT_SEARCH_K})

                # Get relevant documents
                docs = await retriever.ainvoke(message)
                context = "\n\n".join([doc.page_content for doc in docs])

                # Extract sources
                sources = [
                    {
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata
                    }
                    for doc in docs
                ]

                # Get chat history
                chat_history_vars = memory.load_memory_variables({})
                chat_history = chat_history_vars.get("chat_history", [])

                # Format chat history for prompt
                formatted_history = ""
                for msg in chat_history:
                    if isinstance(msg, HumanMessage):
                        formatted_history += f"Human: {msg.content}\n"
                    elif isinstance(msg, AIMessage):
                        formatted_history += f"Assistant: {msg.content}\n"

                # Format prompt
                prompt = self.qa_prompt.format(
                    context=context,
                    chat_history=formatted_history,
                    question=message
                )

                # Stream response
                async for chunk in self.llm.astream(prompt):
                    full_response += chunk.content
                    yield chunk.content, session_id, None

                # Save to memory
                memory.save_context({"question": message}, {"answer": full_response})

                # Send sources in final message
                yield "", session_id, sources

            else:
                # Direct chat without RAG
                chat_history = memory.load_memory_variables({}).get("chat_history", [])
                messages = chat_history + [HumanMessage(content=message)]

                async for chunk in self.llm.astream(messages):
                    full_response += chunk.content
                    yield chunk.content, session_id, None

                # Save to memory
                memory.save_context({"question": message}, {"answer": full_response})

        except Exception as e:
            logger.error(f"Error in streaming chat: {str(e)}", exc_info=True)
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

        memory = self.sessions[session_id]
        chat_history = memory.load_memory_variables({}).get("chat_history", [])

        return [
            {
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content
            }
            for msg in chat_history
        ]
