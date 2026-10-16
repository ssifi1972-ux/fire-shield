from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import (
    detection_node,
    analysis_node,
    dispatch_node,
    intervention_node,
    coordination_node,
    publish_node,
)


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("detection", detection_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("dispatch", dispatch_node)
    workflow.add_node("intervention", intervention_node)
    workflow.add_node("coordination", coordination_node)
    workflow.add_node("publish", publish_node)

    workflow.add_edge(START, "detection")
    workflow.add_edge("detection", "analysis")
    workflow.add_edge("analysis", "dispatch")
    workflow.add_edge("dispatch", "intervention")
    workflow.add_edge("intervention", "coordination")
    workflow.add_edge("coordination", "publish")
    workflow.add_edge("publish", END)

    return workflow.compile()


app = build_graph()