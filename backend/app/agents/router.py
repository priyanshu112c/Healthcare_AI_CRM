import uuid
from typing import Any
from app.agents.graph import agent_graph
from app.agents.state import AgentState
from app.agents.schemas import InteractionFields


def run_agent(user_message: str, session_id: str | None = None, user_id: str | None = None) -> dict[str, Any]:
    if not session_id:
        session_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": session_id}}

    initial_state: AgentState = {
        "messages": [{"role": "user", "content": user_message}],
        "current_interaction": InteractionFields(),
        "last_tool": None,
        "last_tool_result": None,
        "history": [],
        "user_id": user_id,
        "error": None,
        "retry_count": 0,
    }

    try:
        result = agent_graph.invoke(initial_state, config)
    except Exception as e:
        result = {
            **initial_state,
            "error": str(e),
            "messages": [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": f"I encountered an error: {str(e)}. Please try again."},
            ],
        }

    messages = result.get("messages", [])
    current_interaction = result.get("current_interaction", InteractionFields())
    last_tool_result = result.get("last_tool_result")
    last_tool = result.get("last_tool")

    if isinstance(current_interaction, InteractionFields):
        current_interaction = current_interaction.model_dump(exclude_none=True)

    return {
        "session_id": session_id,
        "response": messages[-1]["content"] if messages else "",
        "interaction": current_interaction,
        "tool_called": last_tool,
        "tool_result": last_tool_result,
        "full_history": messages,
    }


async def run_agent_stream(user_message: str, session_id: str | None = None, user_id: str | None = None):
    if not session_id:
        session_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": session_id}}

    initial_state: AgentState = {
        "messages": [{"role": "user", "content": user_message}],
        "current_interaction": InteractionFields(),
        "last_tool": None,
        "last_tool_result": None,
        "history": [],
        "user_id": user_id,
        "error": None,
        "retry_count": 0,
    }

    try:
        async for event in agent_graph.astream_events(initial_state, config, version="v1"):
            kind = event.get("event")
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk", {})
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    yield {"type": "token", "content": content}
            elif kind == "on_tool_start":
                yield {"type": "tool_start", "tool": event.get("name", "")}
            elif kind == "on_tool_end":
                yield {"type": "tool_end", "tool": event.get("name", "")}
    except Exception as e:
        yield {"type": "error", "content": str(e)}
