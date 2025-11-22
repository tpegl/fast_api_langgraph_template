import logging

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from app.graphs.cv_parser.nodes import (
    finalise_processing,
    handle_failures,
    parse_document,
    validate_input,
)
from app.graphs.cv_parser.routing import route_after_validation
from app.graphs.cv_parser.state import CVParserState

logger = logging.getLogger(__name__)


load_dotenv()


def create_graph():
    logger.info("Creating UV Parser graph")

    graph = StateGraph(CVParserState)

    graph.add_node("validate_input", validate_input)
    graph.add_node("handle_failure", handle_failures)
    graph.add_node("parse_document", parse_document)
    graph.add_node("finalise", finalise_processing)

    graph.add_edge(START, "validate_input")

    _ = graph.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {"handle_failure": "handle_failure", "parse_document": "parse_document"},
    )

    graph.add_edge("handle_failure", "finalise")
    graph.add_edge("parse_document", "finalise")
    graph.add_edge("finalise", END)

    return graph.compile()


graph = create_graph()
