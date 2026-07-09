from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import (
    detect_intent,
    route_after_intent,
    execute_log_interaction,
    execute_edit_interaction,
    execute_clear_fields,
    execute_suggest_follow_up,
    execute_interaction_summary,
    execute_search_hcp,
    execute_generate_email,
    execute_generate_next_steps,
    execute_compliance_check,
    respond_to_user,
)
from app.agents.memory import memory


def create_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("execute_log_interaction", execute_log_interaction)
    workflow.add_node("execute_edit_interaction", execute_edit_interaction)
    workflow.add_node("execute_clear_fields", execute_clear_fields)
    workflow.add_node("execute_suggest_follow_up", execute_suggest_follow_up)
    workflow.add_node("execute_interaction_summary", execute_interaction_summary)
    workflow.add_node("execute_search_hcp", execute_search_hcp)
    workflow.add_node("execute_generate_email", execute_generate_email)
    workflow.add_node("execute_generate_next_steps", execute_generate_next_steps)
    workflow.add_node("execute_compliance_check", execute_compliance_check)
    workflow.add_node("respond_to_user", respond_to_user)

    workflow.set_entry_point("detect_intent")

    workflow.add_conditional_edges(
        "detect_intent",
        route_after_intent,
        {
            "execute_log_interaction": "execute_log_interaction",
            "execute_edit_interaction": "execute_edit_interaction",
            "execute_clear_fields": "execute_clear_fields",
            "execute_suggest_follow_up": "execute_suggest_follow_up",
            "execute_interaction_summary": "execute_interaction_summary",
            "execute_search_hcp": "execute_search_hcp",
            "execute_generate_email": "execute_generate_email",
            "execute_generate_next_steps": "execute_generate_next_steps",
            "execute_compliance_check": "execute_compliance_check",
            "respond_to_user": "respond_to_user",
        },
    )

    tool_nodes = [
        "execute_log_interaction",
        "execute_edit_interaction",
        "execute_clear_fields",
        "execute_suggest_follow_up",
        "execute_interaction_summary",
        "execute_search_hcp",
        "execute_generate_email",
        "execute_generate_next_steps",
        "execute_compliance_check",
    ]
    for node in tool_nodes:
        workflow.add_edge(node, "respond_to_user")

    workflow.add_edge("respond_to_user", END)

    graph = workflow.compile(checkpointer=memory)
    return graph


agent_graph = create_agent_graph()
