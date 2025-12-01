"""Generate LangGraph visualization for the Hybrid RAG Agent"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path so we can import backend as a module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.hybrid_agent import HybridRAGAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_graph_visualization():
    """Generate and save the LangGraph diagram"""

    logger.info("Initializing HybridRAGAgent...")

    # Initialize the agent (without actually needing the vector store or API keys for graph viz)
    # We just need the graph structure
    try:
        agent = HybridRAGAgent()
    except Exception as e:
        logger.warning(f"Full initialization failed ({e}), but we can still visualize the graph structure")
        # Create a minimal instance just for visualization
        agent = HybridRAGAgent.__new__(HybridRAGAgent)
        agent.vector_manager = None
        agent.exa_tool = None
        agent.llm = None
        agent.graph = agent._build_graph()

    logger.info("Generating Mermaid diagram...")

    # Get the graph
    app = agent.graph

    # Generate the PNG
    png_data = app.get_graph().draw_mermaid_png()

    # Save to file
    output_path = Path(__file__).parent.parent / "hybrid_agent_graph.png"
    with open(output_path, "wb") as f:
        f.write(png_data)

    logger.info(f"Graph visualization saved to: {output_path}")
    logger.info(f"File size: {len(png_data)} bytes")

    # Also save the Mermaid code as text
    mermaid_code = app.get_graph().draw_mermaid()
    mermaid_path = Path(__file__).parent.parent / "hybrid_agent_graph.mmd"
    with open(mermaid_path, "w") as f:
        f.write(mermaid_code)

    logger.info(f"Mermaid code saved to: {mermaid_path}")

    return output_path

if __name__ == "__main__":
    try:
        output_path = generate_graph_visualization()
        logger.info(f"Success! Open the image at: {output_path}")
    except Exception as e:
        logger.error(f"Error generating visualization: {e}", exc_info=True)
        sys.exit(1)
