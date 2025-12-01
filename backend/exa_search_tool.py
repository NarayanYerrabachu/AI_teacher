"""Exa.ai web search integration for real-time information retrieval"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ExaSearchTool:
    """Tool for searching the web using Exa.ai API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Exa search tool

        Args:
            api_key: Exa.ai API key (or from EXA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("EXA_API_KEY not found. Set it in .env file or pass as parameter")

        try:
            from exa_py import Exa
            self.client = Exa(api_key=self.api_key)
            logger.info("Exa search tool initialized successfully")
        except ImportError:
            raise ImportError(
                "exa-py not installed. Install with: pip install exa-py"
            )

    def search(
        self,
        query: str,
        num_results: int = 5,
        use_autoprompt: bool = True,
        search_type: str = "auto",
        days_back: Optional[int] = None
    ) -> List[Dict]:
        """
        Search the web using Exa.ai

        Args:
            query: Search query
            num_results: Number of results to return (max 10)
            use_autoprompt: Let Exa optimize the query for better results
            search_type: "auto", "neural" (semantic), or "keyword" (traditional)
            days_back: Limit results to last N days (None = no limit)

        Returns:
            List of search results with title, url, text, and score
        """
        try:
            # Prepare date filter if specified
            start_published_date = None
            if days_back:
                start_date = datetime.now() - timedelta(days=days_back)
                start_published_date = start_date.strftime("%Y-%m-%d")

            logger.info(
                f"Searching Exa: query='{query}', num_results={num_results}, "
                f"type={search_type}, days_back={days_back}"
            )

            # Perform search with contents
            search_params = {
                "query": query,
                "num_results": num_results,
                "use_autoprompt": use_autoprompt,
                "type": search_type,
                "contents": {
                    "text": {"max_characters": 2000},  # Get page content
                    "highlights": {"num_sentences": 3},  # Get key highlights
                }
            }

            if start_published_date:
                search_params["start_published_date"] = start_published_date

            response = self.client.search_and_contents(**search_params)

            # Format results
            results = []
            for result in response.results:
                results.append({
                    "title": result.title,
                    "url": result.url,
                    "text": result.text if hasattr(result, 'text') else "",
                    "highlights": result.highlights if hasattr(result, 'highlights') else [],
                    "published_date": result.published_date if hasattr(result, 'published_date') else None,
                    "score": result.score if hasattr(result, 'score') else 0.0,
                    "source": "web"
                })

            logger.info(f"Exa search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Exa search failed: {str(e)}")
            return []

    def search_recent(self, query: str, num_results: int = 5, days_back: int = 30) -> List[Dict]:
        """
        Search for recent information (last N days)

        Args:
            query: Search query
            num_results: Number of results
            days_back: How many days back to search (default: 30)

        Returns:
            List of recent search results
        """
        return self.search(
            query=query,
            num_results=num_results,
            use_autoprompt=True,
            search_type="auto",
            days_back=days_back
        )

    def search_educational(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search for educational content with semantic search

        Args:
            query: Educational query
            num_results: Number of results

        Returns:
            List of educational search results
        """
        # Add educational context to query
        enhanced_query = f"educational explanation tutorial: {query}"

        return self.search(
            query=enhanced_query,
            num_results=num_results,
            use_autoprompt=True,
            search_type="neural"  # Semantic search for better understanding
        )

    def format_results_for_llm(self, results: List[Dict]) -> str:
        """
        Format search results into a string for LLM context

        Args:
            results: List of search results

        Returns:
            Formatted string with all results
        """
        if not results:
            return "No web results found."

        formatted = "WEB SEARCH RESULTS:\n\n"

        for i, result in enumerate(results, 1):
            formatted += f"[{i}] {result['title']}\n"
            formatted += f"URL: {result['url']}\n"

            if result.get('published_date'):
                formatted += f"Published: {result['published_date']}\n"

            # Add highlights if available
            if result.get('highlights'):
                formatted += "Key points:\n"
                for highlight in result['highlights'][:3]:
                    formatted += f"  - {highlight}\n"

            # Add text content
            if result.get('text'):
                text = result['text'][:500]  # Limit to 500 chars
                formatted += f"\nContent:\n{text}...\n"

            formatted += "\n" + "="*80 + "\n\n"

        return formatted


# Example usage and testing
if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Test the tool
    try:
        exa = ExaSearchTool()

        # Test search
        logger.info("\n=== Testing Exa Search ===\n")
        results = exa.search("latest developments in artificial intelligence", num_results=3)

        logger.info(f"Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. {result['title']}")
            logger.info(f"   URL: {result['url']}")
            logger.info(f"   Score: {result['score']:.3f}")
            logger.info("")

        # Test formatted output
        logger.info("\n=== Formatted for LLM ===\n")
        formatted = exa.format_results_for_llm(results[:2])
        logger.info(formatted)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
