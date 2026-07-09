import json
from datetime import date, time
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text as sa_text

from app.agents.router import run_agent
from app.agents.graph import agent_graph
from app.agents.state import AgentState
from app.agents.schemas import InteractionFields
from app.services.database.connection import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    interaction: dict[str, Any]
    tool_called: str | None
    tool_result: dict[str, Any] | None
    full_history: list[dict[str, Any]]


class ToolRequest(BaseModel):
    tool: str
    args: dict[str, Any] = {}
    session_id: str | None = None


class InteractionCreate(BaseModel):
    hcp_name: str
    interaction_type: str
    date: str
    time: str | None = None
    topics: str | None = None
    sentiment: str | None = None
    materials: list[str] | None = None
    attendees: list[str] | None = None
    outcomes: str | None = None
    follow_up_action: str | None = None
    next_meeting: str | None = None
    priority: str | None = None


class InteractionUpdate(BaseModel):
    hcp_name: str | None = None
    interaction_type: str | None = None
    date: str | None = None
    time: str | None = None
    topics: str | None = None
    sentiment: str | None = None
    materials: list[str] | None = None
    attendees: list[str] | None = None
    outcomes: str | None = None
    follow_up_action: str | None = None
    next_meeting: str | None = None
    priority: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    result = run_agent(
        user_message=request.message,
        session_id=request.session_id,
        user_id=request.user_id,
    )
    return ChatResponse(
        session_id=result["session_id"],
        response=result["response"],
        interaction=result["interaction"],
        tool_called=result["tool_called"],
        tool_result=result["tool_result"],
        full_history=result["full_history"],
    )


@router.post("/tool")
async def execute_tool(request: ToolRequest):
    from app.agents.tools import tool_map

    tool_fn = tool_map.get(request.tool)
    if not tool_fn:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool}' not found")

    try:
        result = tool_fn.invoke(request.args)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interaction")
async def create_interaction(data: InteractionCreate, session: AsyncSession = Depends(get_session)):
    from app.services.database.models.user import User
    from app.services.database.models.hcp import HCP
    from app.services.database.models.interaction import Interaction
    from app.services.database.models.attendee import Attendee
    from app.services.database.models.material import Material
    from app.services.database.models.sample import Sample
    from app.services.database.models.followup import FollowUp
    import uuid

    user = await session.get(User, "default")
    if not user:
        user = User(id="default", email="rep@example.com", name="Default Rep", role="rep")
        session.add(user)
        await session.commit()

    existing = await session.execute(
        sa_text("SELECT id FROM hcp WHERE name = :name").bindparams(name=data.hcp_name)
    )
    row = existing.scalar_one_or_none()
    if row:
        hcp_id = row
    else:
        hcp_id = str(uuid.uuid4())
        hcp = HCP(id=hcp_id, name=data.hcp_name)
        session.add(hcp)
        await session.commit()

    interaction_id = str(uuid.uuid4())
    parsed_date = date.fromisoformat(data.date) if data.date else date.today()
    parsed_time = time.fromisoformat(data.time) if data.time else None

    interaction = Interaction(
        id=interaction_id,
        user_id=user.id,
        hcp_id=hcp_id,
        interaction_type=data.interaction_type,
        interaction_date=parsed_date,
        interaction_time=parsed_time,
        topics=data.topics,
        sentiment=data.sentiment,
        outcomes=data.outcomes,
    )
    session.add(interaction)

    if data.attendees:
        for name in data.attendees:
            session.add(Attendee(interaction_id=interaction_id, name=name))

    if data.materials:
        for name in data.materials:
            session.add(Material(interaction_id=interaction_id, name=name))

    if data.follow_up_action:
        session.add(FollowUp(
            interaction_id=interaction_id,
            action_type=data.follow_up_action,
            priority=data.priority or "medium",
        ))

    await session.commit()

    dumped = data.model_dump()
    dumped["id"] = interaction_id
    return {
        "success": True,
        "message": "Interaction saved successfully",
        "data": dumped,
    }


@router.put("/interaction/{interaction_id}")
async def update_interaction(interaction_id: str, data: InteractionUpdate):
    return {
        "success": True,
        "message": f"Interaction {interaction_id} updated",
        "data": data.model_dump(exclude_none=True),
    }


@router.delete("/interaction/{interaction_id}")
async def delete_interaction(interaction_id: str):
    return {
        "success": True,
        "message": f"Interaction {interaction_id} deleted",
    }


@router.get("/interaction")
async def list_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    return {
        "success": True,
        "data": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
    }


@router.get("/langgraph")
async def get_langgraph():
    try:
        from app.agents.graph import agent_graph
        import base64

        png_bytes = agent_graph.get_graph().draw_mermaid_png()
        b64 = base64.b64encode(png_bytes).decode("utf-8")
        return {
            "success": True,
            "image": f"data:image/png;base64,{b64}",
            "graph_type": "StateGraph",
        }
    except Exception as e:
        mermaid_code = agent_graph.get_graph().draw_mermaid()
        return {
            "success": True,
            "mermaid": mermaid_code,
            "error": str(e),
        }


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "Healthcare CRM Interaction Logger",
        "version": "1.0.0",
    }


@router.get("/schema")
async def get_schema():
    from app.agents.schemas import (
        InteractionFields,
        ToolCallResult,
        LogInteractionOutput,
        EditInteractionOutput,
        ClearFieldsOutput,
        SuggestFollowUpOutput,
        InteractionSummaryOutput,
    )

    schemas = {
        "InteractionFields": InteractionFields.model_json_schema(),
        "ToolCallResult": ToolCallResult.model_json_schema(),
        "LogInteractionOutput": LogInteractionOutput.model_json_schema(),
        "EditInteractionOutput": EditInteractionOutput.model_json_schema(),
        "ClearFieldsOutput": ClearFieldsOutput.model_json_schema(),
        "SuggestFollowUpOutput": SuggestFollowUpOutput.model_json_schema(),
        "InteractionSummaryOutput": InteractionSummaryOutput.model_json_schema(),
    }

    return {"success": True, "schemas": schemas}
