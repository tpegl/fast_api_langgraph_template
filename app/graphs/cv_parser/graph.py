import logging

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from app.graphs.cv_parser.nodes import handle_failures, validate_input
from app.graphs.cv_parser.routing import route_after_validation
from app.graphs.cv_parser.state import CVParserState

logger = logging.getLogger(__name__)


load_dotenv()

def create_graph():
    logger.info("Creating UV Parser graph")

    graph = StateGraph(CVParserState)

    graph.add_node("validate_input", validate_input)
    graph.add_node("handle_failure", handle_failures)
    _ = graph.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {
            "handle_failure": "handle_failure"
        }
    )

    return graph.compile()


graph = create_graph()
