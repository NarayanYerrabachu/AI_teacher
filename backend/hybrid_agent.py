"""LangGraph-based hybrid agent for PDF + Web search"""

import logging
import os
from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from .exa_search_tool import ExaSearchTool
from .vector_store import VectorStoreManager
from .config import Config

logger = logging.getLogger(__name__)


# Define the agent state
class AgentState(TypedDict):
    """State for the hybrid agent"""
    messages: Annotated[List[BaseMessage], add]  # Conversation messages
    query: str  # User's original query
    route_decision: Optional[str]  # "pdf", "web", "both", or "none"
    pdf_context: Optional[str]  # Context from PDF search
    web_context: Optional[str]  # Context from web search
    combined_context: Optional[str]  # Combined PDF + web context
    pdf_sources: Optional[List[Dict]]  # PDF source metadata
    web_sources: Optional[List[Dict]]  # Web source URLs
    final_answer: Optional[str]  # Generated answer
    needs_web_search: bool  # Whether web search is needed
    needs_pdf_search: bool  # Whether PDF search is needed
    is_enriched_followup: bool  # Whether query was enriched from short follow-up


class HybridRAGAgent:
    """
    LangGraph agent that intelligently routes between PDF search and web search
    """

    def __init__(
        self,
        vector_manager: Optional[VectorStoreManager] = None,
        exa_api_key: Optional[str] = None
    ):
        """
        Initialize the hybrid agent

        Args:
            vector_manager: Vector store manager for PDF search
            exa_api_key: Exa.ai API key for web search
        """
        self.vector_manager = vector_manager or VectorStoreManager()
        self.exa_tool = ExaSearchTool(api_key=exa_api_key)

        # Initialize LLM with explicit base URL to avoid routing issues
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            streaming=True,
            openai_api_base="https://api.openai.com/v1"
        )

        # Build the agent graph
        self.graph = self._build_graph()

        logger.info("HybridRAGAgent initialized with LangGraph")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("router", self._route_query)
        workflow.add_node("search_pdf", self._search_pdf)
        workflow.add_node("search_web", self._search_web)
        workflow.add_node("search_parallel", self._search_parallel)  # NEW: Parallel search node
        workflow.add_node("combine_context", self._combine_context)
        workflow.add_node("generate_answer", self._generate_answer)

        # Define the flow
        workflow.set_entry_point("router")

        # From router, decide which search(es) to use
        workflow.add_conditional_edges(
            "router",
            self._route_condition,
            {
                "pdf_only": "search_pdf",
                "web_only": "search_web",
                "both": "search_parallel",  # OPTIMIZED: Run both in parallel
                "none": "generate_answer"  # Direct answer for greetings etc.
            }
        )

        # After PDF-only search
        workflow.add_edge("search_pdf", "combine_context")

        # After web-only search
        workflow.add_edge("search_web", "combine_context")

        # After parallel search (both PDF and web)
        workflow.add_edge("search_parallel", "combine_context")

        # After combining context
        workflow.add_edge("combine_context", "generate_answer")

        # After generating answer, end
        workflow.add_edge("generate_answer", END)

        return workflow.compile()

    def _route_query(self, state: AgentState) -> AgentState:
        """
        Decide whether to search PDF, web, or both

        Uses LLM to analyze the query and determine routing
        """
        query = state["query"]
        is_enriched_followup = state.get("is_enriched_followup", False)

        # If this is an enriched follow-up (e.g., "yes" enriched with context),
        # route to PDF only since it's continuing a textbook discussion
        if is_enriched_followup:
            state["route_decision"] = "pdf_only"
            state["needs_pdf_search"] = True
            state["needs_web_search"] = False
            logger.info(f"Route decision: PDF only (enriched follow-up)")
            return state

        # Simple heuristic routing (can be enhanced with LLM)
        query_lower = query.lower().strip()

        # Very short follow-up responses - treat as textbook queries since we don't have history context
        # User might be responding "yes" to "Would you like to explore..." type questions
        short_followups = ["yes", "no", "sure", "ok", "okay", "please", "yep", "nope", "yeah", "nah"]
        if query_lower in short_followups:
            state["route_decision"] = "pdf_only"
            state["needs_pdf_search"] = True
            state["needs_web_search"] = False
            logger.info(f"Route decision: PDF only (detected follow-up: '{query}')")
            return state

        # Greetings and simple queries
        greetings = ["hello", "hi", "hey", "thanks", "thank you", "bye"]
        if any(greet in query_lower for greet in greetings) and len(query.split()) < 5:
            state["route_decision"] = "none"
            state["needs_pdf_search"] = False
            state["needs_web_search"] = False
            logger.info("Route decision: none (greeting/simple query)")
            return state

        # Non-educational keywords - reject immediately
        non_educational_keywords = [
            "order", "buy", "purchase", "shop", "pizza", "food", "restaurant",
            "delivery", "movie", "ticket", "booking", "hotel", "flight",
            "weather", "stock", "price", "game", "entertainment", "music",
            "sports", "news" , "dating", "social media", "instagram", "facebook"
        ]
        if any(keyword in query_lower for keyword in non_educational_keywords):
            # Check if it's combined with educational context
            educational_terms = ["teach", "learn", "study", "explain", "understand", "homework", "assignment", "exam"]
            has_educational_context = any(term in query_lower for term in educational_terms)

            if not has_educational_context:
                state["route_decision"] = "none"
                state["needs_pdf_search"] = False
                state["needs_web_search"] = False
                logger.info(f"Route decision: none (non-educational query: '{query}')")
                return state

        # Keywords indicating current/recent information
        recent_keywords = [
            "latest", "recent", "current", "today", "now", "2024", "2025",
            "news", "update", "breaking", "trend", "new development"
        ]

        # Keywords indicating textbook content
        textbook_keywords = [
            "chapter", "section", "exercise", "problem", "textbook",
            "page", "class 9", "ncert", "mathematics", "english", "beehive"
        ]

        has_recent_keyword = any(keyword in query_lower for keyword in recent_keywords)
        has_textbook_keyword = any(keyword in query_lower for keyword in textbook_keywords)

        # Decision logic
        if has_textbook_keyword and not has_recent_keyword:
            state["route_decision"] = "pdf_only"
            state["needs_pdf_search"] = True
            state["needs_web_search"] = False
            logger.info("Route decision: PDF only (textbook query)")

        elif has_recent_keyword and not has_textbook_keyword:
            state["route_decision"] = "web_only"
            state["needs_pdf_search"] = False
            state["needs_web_search"] = True
            logger.info("Route decision: Web only (recent information query)")

        else:
            # Default: try PDF first, then web if needed
            state["route_decision"] = "both"
            state["needs_pdf_search"] = True
            state["needs_web_search"] = True
            logger.info("Route decision: Both (comprehensive query)")

        return state

    def _route_condition(self, state: AgentState) -> str:
        """Determine which path to take from router"""
        decision = state.get("route_decision", "both")

        if decision == "pdf_only":
            return "pdf_only"
        elif decision == "web_only":
            return "web_only"
        elif decision == "both":
            return "both"
        else:
            return "none"

    def _search_pdf(self, state: AgentState) -> AgentState:
        """Search the PDF knowledge base"""
        query = state["query"]

        try:
            vectorstore = self.vector_manager.load_vector_store()
            results = vectorstore.similarity_search_with_relevance_scores(
                query,
                k=Config.DEFAULT_SEARCH_K
            )

            # Filter by relevance threshold
            RELEVANCE_THRESHOLD = 0.2
            relevant_docs = [
                (doc, score) for doc, score in results
                if score >= RELEVANCE_THRESHOLD
            ]

            if relevant_docs:
                # Extract context
                docs = [doc for doc, score in relevant_docs]
                context = "\n\n".join([doc.page_content for doc in docs])
                state["pdf_context"] = context

                # Extract sources
                state["pdf_sources"] = [
                    {
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata,
                        "relevance_score": f"{score:.2f}",
                        "source": "pdf"
                    }
                    for doc, score in relevant_docs
                ]

                logger.info(f"PDF search: Found {len(relevant_docs)} relevant documents")

                # If we got good PDF results and don't need recent info, skip web
                if state.get("route_decision") == "both" and relevant_docs[0][1] > 0.35:
                    state["needs_web_search"] = False
                    logger.info("PDF results sufficient, skipping web search")
            else:
                logger.info("PDF search: No relevant documents found")
                state["pdf_context"] = None
                state["pdf_sources"] = []

        except Exception as e:
            logger.error(f"PDF search failed: {e}")
            state["pdf_context"] = None
            state["pdf_sources"] = []

        return state

    def _search_web(self, state: AgentState) -> AgentState:
        """Search the web using Exa.ai"""
        query = state["query"]

        try:
            # Determine if we need recent results
            query_lower = query.lower()
            recent_keywords = ["latest", "recent", "current", "today", "2024", "2025"]
            needs_recent = any(keyword in query_lower for keyword in recent_keywords)

            if needs_recent:
                results = self.exa_tool.search_recent(
                    query=query,
                    num_results=3,
                    days_back=90
                )
            else:
                results = self.exa_tool.search_educational(
                    query=query,
                    num_results=3
                )

            if results:
                # Format context
                context = self.exa_tool.format_results_for_llm(results)
                state["web_context"] = context

                # Store sources
                state["web_sources"] = [
                    {
                        "title": result["title"],
                        "url": result["url"],
                        "published_date": result.get("published_date"),
                        "score": result.get("score", 0.0),
                        "source": "web"
                    }
                    for result in results
                ]

                logger.info(f"Web search: Found {len(results)} results")
            else:
                logger.info("Web search: No results found")
                state["web_context"] = None
                state["web_sources"] = []

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            state["web_context"] = None
            state["web_sources"] = []

        return state

    def _search_parallel(self, state: AgentState) -> AgentState:
        """
        Execute PDF and web searches in parallel for maximum speed

        This runs both searches concurrently using Python's concurrent execution,
        significantly reducing response time when both sources are needed.
        """
        import concurrent.futures
        import time

        query = state["query"]
        logger.info(f"🚀 Starting PARALLEL search for: '{query[:100]}...'")
        start_time = time.time()

        # Create copies of state for each search to avoid conflicts
        pdf_state = state.copy()
        web_state = state.copy()

        # Execute both searches in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks
            pdf_future = executor.submit(self._search_pdf, pdf_state)
            web_future = executor.submit(self._search_web, web_state)

            # Wait for both to complete
            pdf_result = pdf_future.result()
            web_result = web_future.result()

        # Merge results back into main state
        state["pdf_context"] = pdf_result.get("pdf_context")
        state["pdf_sources"] = pdf_result.get("pdf_sources", [])
        state["web_context"] = web_result.get("web_context")
        state["web_sources"] = web_result.get("web_sources", [])

        elapsed_time = time.time() - start_time
        logger.info(f"✅ PARALLEL search completed in {elapsed_time:.2f}s "
                   f"(PDF: {len(state['pdf_sources'])} sources, "
                   f"Web: {len(state['web_sources'])} sources)")

        return state

    def _format_response_with_spacing(self, text: str) -> str:
        """
        Post-process LLM response to add proper blank lines between sections
        and fix LaTeX formatting

        This function:
        - Adds blank lines after section markers
        - Converts plain parentheses with LaTeX commands to proper LaTeX delimiters
        """
        import re

        # Log the first 500 chars to see what we're working with
        logger.info(f"LaTeX processing - input preview: {text[:500]}")

        # First, fix LaTeX formatting: Convert (math) to \( math \) if it contains LaTeX commands
        # Strategy: Only convert PLAIN parentheses ( ) that contain LaTeX, not already-correct \( \)

        # Step 1: Temporarily replace already-correct math delimiters with placeholders
        correct_latex = []
        def save_correct_latex(match):
            correct_latex.append(match.group(0))
            return f'<<<LATEX{len(correct_latex)-1}>>>'

        # Match both $...$ and \( ... \) - save them to restore later
        text = re.sub(r'\$[^$]+\$', save_correct_latex, text)
        text = re.sub(r'\\\(.*?\\\)', save_correct_latex, text)

        # Step 2: Now fix plain parentheses that contain LaTeX commands or mathematical notation
        # Need to handle nested parentheses like ( 2 \times (-1) = -2 )
        def fix_plain_latex(match):
            content = match.group(1).strip()

            # Skip conversion for very long text (likely prose, not math)
            if len(content) > 50:
                return match.group(0)

            # Skip conversion for text that looks like prose (multiple words without math)
            words = content.split()
            if len(words) > 5 and not any(c in content for c in r'\^_=<>≥≤≠±×÷+-*/'):
                return match.group(0)

            # Clean up malformed LaTeX delimiters before conversion
            # Remove \left(, \right), \left[, \right], \left\{, \right\} that appear without proper pairing
            content = re.sub(r'\\left[\(\[\{]', '(', content)
            content = re.sub(r'\\right[\)\]\}]', ')', content)

            # Convert if it contains:
            # 1. LaTeX commands: \frac, \times, \geq, \leq, \neq, etc.
            # 2. Superscripts ^ or subscripts _
            # 3. Single mathematical variables (single letter or letter with number)
            # 4. Mathematical expressions with variables and operators (including unicode)

            has_latex_command = bool(re.search(r'\\[a-zA-Z]+', content))
            has_super_sub = bool(re.search(r'[\^_]', content))
            is_single_var = bool(re.match(r'^[a-zA-Z](\d+)?$', content))  # Single letter like x, y, z, x2
            is_math_expr = bool(re.search(r'[a-zA-Z]\s*[=<>≥≤≠±×÷+\-*/]|[=<>≥≤≠±×÷+\-*/]\s*[a-zA-Z]', content))  # Has variables with operators

            if has_latex_command or has_super_sub or is_single_var or is_math_expr:
                return f'${content}$'
            return match.group(0)  # Return original if no mathematical content

        # Match plain parentheses - allow nested parens by matching balanced groups
        # This pattern matches ( ... ) where ... can contain nested (...)
        # We'll do multiple passes to handle all levels
        max_iterations = 5  # Prevent infinite loops
        conversions_made = 0
        for iteration in range(max_iterations):
            # Match outer parentheses that might contain LaTeX
            # Use negative lookbehind to avoid matching LaTeX delimiters
            pattern = r'(?<!\\)\(([^()]*(?:\([^()]*\)[^()]*)*)\)'
            new_text = re.sub(pattern, fix_plain_latex, text)
            if new_text == text:
                break  # No more changes
            conversions_made += 1
            text = new_text

        if conversions_made > 0:
            logger.info(f"LaTeX conversion: made {conversions_made} passes with changes")
        else:
            logger.info("LaTeX conversion: no changes made")

        # Step 3: Restore the already-correct LaTeX
        for i, latex in enumerate(correct_latex):
            text = text.replace(f'<<<LATEX{i}>>>', latex)

        # Log a sample of the output
        logger.info(f"LaTeX processing - output preview: {text[:500]}")

        lines = text.split('\n')
        formatted_lines = []

        for i, line in enumerate(lines):
            # Add current line
            formatted_lines.append(line)

            # Skip if this is the last line
            if i == len(lines) - 1:
                continue

            # Skip if next line is already blank
            if i + 1 < len(lines) and lines[i + 1].strip() == '':
                continue

            stripped = line.strip()

            # Add blank line after bold headers (e.g., **Understanding Integers** 📚)
            if stripped.startswith('**') and stripped.endswith(('📚', '💡', '✨', '🎓', '🌟')):
                formatted_lines.append('')

            # Add blank line after "According to" citations
            elif 'According to' in stripped and stripped.endswith(('.', '!')):
                formatted_lines.append('')

            # Add blank line after section headers
            elif stripped in ['**Detailed Explanation:**', '**Examples:**', '**Summary:**', '**Key Points:**']:
                formatted_lines.append('')

            # Add blank line after numbered list items (1., 2., 3.)
            elif re.match(r'^\d+\.\s+\*\*', stripped):
                formatted_lines.append('')

            # Add blank line after bullet points (• **Example)
            elif stripped.startswith('•') or stripped.startswith('-'):
                formatted_lines.append('')

            # Add blank line before section headers (if not already preceded by blank)
            next_stripped = lines[i + 1].strip() if i + 1 < len(lines) else ''
            if next_stripped in ['**Detailed Explanation:**', '**Examples:**', '**Summary:**'] and stripped != '':
                formatted_lines.append('')

        return '\n'.join(formatted_lines)

    def _combine_context(self, state: AgentState) -> AgentState:
        """Combine context from PDF and web sources"""
        logger.info("=== COMBINE_CONTEXT CALLED ===")

        pdf_context = state.get("pdf_context")
        web_context = state.get("web_context")

        logger.info(f"pdf_context exists: {pdf_context is not None}, web_context exists: {web_context is not None}")

        if pdf_context and web_context:
            combined = f"""TEXTBOOK CONTENT:
{pdf_context}

{web_context}

Please synthesize information from both the textbook and web sources to provide a comprehensive answer."""
            state["combined_context"] = combined
            logger.info("Combined PDF and web context")

        elif pdf_context:
            state["combined_context"] = f"TEXTBOOK CONTENT:\n{pdf_context}"
            logger.info("Using PDF context only")

        elif web_context:
            state["combined_context"] = web_context
            logger.info("Using web context only")

        else:
            state["combined_context"] = None
            logger.info("No context available")

        return state

    def _generate_answer(self, state: AgentState) -> AgentState:
        """Generate the final answer using LLM"""

        query = state["query"]
        context = state.get("combined_context")

        # Debug logging
        logger.info(f"Generating answer with context present: {context is not None}")
        if context:
            logger.info(f"Context length: {len(context)} chars")
            logger.info(f"Context preview: {context[:200]}...")

        # Build system message with enhanced answer quality guidance
        if context:
            system_message = f"""You are an expert AI teacher assistant with access to educational textbooks and current web information.

AVAILABLE CONTEXT:
{context}

CRITICAL: You HAVE context from textbooks/sources. You MUST provide an educational answer using the format below.
DO NOT give a generic greeting or say you can't help. You MUST analyze the context and answer educationally.

YOUR MISSION:
Provide comprehensive, well-structured, and student-friendly answers that demonstrate deep understanding.

CRITICAL FORMATTING - YOU MUST ADD BLANK LINES BETWEEN EVERY SECTION!

To add a blank line: OUTPUT TWO NEWLINE CHARACTERS (\\n\\n) or press Enter TWICE

MANDATORY STRUCTURE - Copy this EXACTLY with ALL the spacing:

**[Opening sentence with bold key concept]** 📚


According to the textbook/material, [add citation from context].


**Detailed Explanation:**


1. **First key point** - Explanation in 2-3 sentences based on the context


2. **Second key point** - Explanation in 2-3 sentences based on the context


3. **Third key point** - Explanation in 2-3 sentences based on the context


**Examples:**


• **Example 1:** $[math notation]$ - Brief explanation


• **Example 2:** $[math notation]$ - Brief explanation


• **Example 3:** $[math notation]$ - Brief explanation


**Summary:** [1-2 sentence conclusion] ✨


Would you like to explore [related concept]? 🎓

SPACING RULES - ABSOLUTELY CRITICAL:
→ After opening statement: ADD BLANK LINE
→ After citation: ADD BLANK LINE
→ After "**Detailed Explanation:**": ADD BLANK LINE
→ After EACH numbered point (1., 2., 3.): ADD BLANK LINE
→ After "**Examples:**": ADD BLANK LINE
→ After EACH bullet (•): ADD BLANK LINE
→ After summary: ADD BLANK LINE

ABSOLUTE REQUIREMENTS - CRITICAL FORMATTING:
✓ START with **bold concept** and 📚 emoji, then BLANK LINE
✓ CITE "According to the textbook..." with BLANK LINE before AND after
✓ "**Detailed Explanation:**" header with BLANK LINE before AND after
✓ Each numbered item (1., 2., 3.) MUST have BLANK LINE after it
✓ "**Examples:**" header with BLANK LINE before AND after
✓ Each bullet point (•) MUST have BLANK LINE after it
✓ "**Summary:**" line with BLANK LINE before AND after
✓ Final question with BLANK LINE before it
✓ USE LaTeX with $ delimiters: $\\frac{{a}}{{b}}$, $x^2$, $x \\geq 1$ for ALL math expressions
✓ USE emojis throughout (📚, 🎓, ✨, 💡)

FORBIDDEN:
✗ DO NOT give generic "I'm here to help" responses
✗ DO NOT say you don't understand if context is provided
✗ DO NOT skip the numbered explanation section
✗ DO NOT omit examples when relevant

Remember: The user asked a specific question and you have context to answer it. ANSWER THE QUESTION EDUCATIONALLY."""
        else:
            system_message = f"""You are a specialized AI teacher assistant for Class 9 Mathematics and English (Beehive textbook).

USER QUERY: "{query}"

CRITICAL: You can ONLY answer questions about:
1. Educational topics (mathematics, science, literature, language)
2. Content from uploaded textbooks and educational materials
3. Current educational trends and learning methods

IF THIS IS A GREETING (hello, hi, hey, thanks):
- Warmly introduce yourself with emojis 👋📚
- State: "I'm your AI teacher specialized in Class 9 Mathematics and English"
- Explain: "I can help with questions from your textbooks or educational topics"
- Be enthusiastic and encouraging! ✨

IF THIS IS A FOLLOW-UP (yes, no, more):
- Acknowledge: "I'd love to help, but I need more specific information!"
- Explain: "Could you please rephrase your question with more detail?"
- Suggest: "For example, ask about specific math concepts, chapters, or topics from your textbook."

FOR NON-EDUCATIONAL QUESTIONS (ordering food, shopping, entertainment, etc.):
YOU MUST FIRMLY DECLINE. Use this EXACT format:

"I apologize, but I can only answer questions related to educational content. 📚

I'm specialized in:
• Class 9 Mathematics and English textbooks
• Educational topics and learning methods
• Academic concepts and problem-solving

Please ask me about topics from your textbooks or educational subjects! 🎓"

FORBIDDEN:
✗ DO NOT try to help with non-educational questions
✗ DO NOT suggest how non-educational topics relate to education
✗ DO NOT be "helpful" about ordering pizza, shopping, etc.
✗ DO NOT give generic "I'm here to help" for off-topic questions

FORMATTING:
- Use clear structure with line breaks
- Be friendly but firm about scope
- Use relevant emojis (📚, 🎓, 💡, ✨)"""

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=query)
        ]

        try:
            response = self.llm.invoke(messages)
            # Apply post-processing to add blank lines and fix LaTeX
            raw_answer = response.content
            formatted_answer = self._format_response_with_spacing(raw_answer)
            state["final_answer"] = formatted_answer

            # Debug logging to check LaTeX conversion
            if '(' in raw_answer and '\\' in raw_answer:
                logger.info("Raw answer contained plain parentheses with LaTeX")
                # Find examples of plain parens with LaTeX
                import re
                plain_latex = re.findall(r'(?<!\\)\([^()]*\\[a-zA-Z]+[^()]*\)', raw_answer)
                if plain_latex:
                    logger.info(f"Found plain LaTeX to convert: {plain_latex[:3]}")

            logger.info("Generated and formatted final answer")

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            state["final_answer"] = "I apologize, but I encountered an error generating a response. Please try again."

        return state

    def query(self, user_query: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Process a user query through the agent

        Args:
            user_query: User's question
            conversation_history: Optional list of previous messages [{"role": "user/assistant", "content": "..."}]

        Returns:
            Dict with answer, sources, and metadata
        """
        logger.info(f"Processing query: '{user_query}'")

        # Enrich query with conversation context if it's a short follow-up
        enriched_query = user_query
        is_enriched_followup = False  # Track if this is an enriched follow-up

        if conversation_history and len(conversation_history) > 0:
            query_lower = user_query.lower().strip()
            short_followups = ["yes", "no", "sure", "ok", "okay", "please", "yep", "nope", "yeah", "nah", "more", "tell me more"]

            if query_lower in short_followups or len(user_query.split()) <= 2:
                # Get the last assistant message to understand context
                for msg in reversed(conversation_history):
                    if msg.get("role") == "assistant":
                        last_response = msg.get("content", "")
                        # Extract the topic from "Would you like to explore..." question
                        if "would you like" in last_response.lower() or "explore" in last_response.lower():
                            # Find the topic mentioned
                            lines = last_response.split("\n")
                            for line in lines:
                                if "would you like" in line.lower() or "explore" in line.lower():
                                    # Extract topic from the question
                                    enriched_query = f"{user_query} - Continue discussion about the previous topic mentioned in: {line}"
                                    is_enriched_followup = True
                                    logger.info(f"Enriched short query '{user_query}' with context: '{enriched_query[:100]}...'")
                                    break
                        break

        # Initialize state
        initial_state = {
            "messages": [],
            "query": enriched_query,  # Use enriched query with conversation context
            "route_decision": None,
            "pdf_context": None,
            "web_context": None,
            "combined_context": None,
            "pdf_sources": [],
            "web_sources": [],
            "final_answer": None,
            "needs_web_search": False,
            "needs_pdf_search": False,
            "is_enriched_followup": is_enriched_followup
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        # Compile response
        response = {
            "answer": final_state.get("final_answer", "No answer generated"),
            "route_used": final_state.get("route_decision", "unknown"),
            "sources": {
                "pdf": final_state.get("pdf_sources", []),
                "web": final_state.get("web_sources", [])
            },
            "has_pdf_context": final_state.get("pdf_context") is not None,
            "has_web_context": final_state.get("web_context") is not None
        }

        logger.info(
            f"Query completed: route={response['route_used']}, "
            f"pdf_sources={len(response['sources']['pdf'])}, "
            f"web_sources={len(response['sources']['web'])}"
        )

        return response


# Example usage
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv

    load_dotenv()

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    try:
        agent = HybridRAGAgent()

        # Test queries
        test_queries = [
            "What are rational numbers?",  # PDF only
            "What are the latest developments in AI?",  # Web only
            "Explain machine learning",  # Both
            "Hello",  # None (greeting)
        ]

        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"Query: {query}")
            print(f"{'='*80}\n")

            result = agent.query(query)

            print(f"Route: {result['route_used']}")
            print(f"PDF Sources: {len(result['sources']['pdf'])}")
            print(f"Web Sources: {len(result['sources']['web'])}")
            print(f"\nAnswer:\n{result['answer'][:500]}...")
            print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
