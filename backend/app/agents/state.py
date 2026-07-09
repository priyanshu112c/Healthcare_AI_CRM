import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from app.agents.schemas import InteractionFields, ToolCallResult


class AgentState(TypedDict):
    messages: Annotated[list[dict], operator.add]
    current_interaction: InteractionFields
    last_tool: str | None
    last_tool_result: ToolCallResult | None
    history: Annotated[list[dict], operator.add]
    user_id: str | None
    error: str | None
    retry_count: int
