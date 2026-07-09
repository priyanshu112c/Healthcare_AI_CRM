from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.agents.state import AgentState
from app.agents.llm import get_llm
from app.agents.prompts import SYSTEM_PROMPT, INTENT_ROUTING_PROMPT
from app.agents.tools import tool_map, _normalize_fields
from app.agents.schemas import InteractionFields
import json
import re


def _last_user_message(state: AgentState) -> str:
    for msg in reversed(state.get("messages", [])):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def _parse_json(text: str) -> dict:
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    return {}


def call_model(state: AgentState) -> dict:
    llm = get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in state.get("messages", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))

    response = llm.invoke(messages)
    content = response.content if hasattr(response, 'content') else str(response)

    return {"messages": [{"role": "assistant", "content": content}]}


def detect_intent(state: AgentState) -> dict:
    llm = get_llm()
    last_message = _last_user_message(state)

    prompt = f"""{INTENT_ROUTING_PROMPT}

User message: {last_message}

Return ONLY a JSON object with keys "intent" and "confidence".
Intent must be one of: LOG_INTERACTION, EDIT_INTERACTION, CLEAR_FIELDS, SUGGEST_FOLLOW_UP, GENERATE_SUMMARY, SEARCH_HCP, GENERATE_EMAIL, GENERATE_NEXT_STEPS, COMPLIANCE_CHECK, GENERAL_CHAT
"""
    response = llm.invoke(prompt)
    content = response.content if hasattr(response, 'content') else str(response)
    result = _parse_json(content)

    return {
        "last_tool": result.get("intent", "GENERAL_CHAT"),
    }


def route_after_intent(state: AgentState) -> str:
    intent = state.get("last_tool", "GENERAL_CHAT")
    tool_intent_map = {
        "LOG_INTERACTION": "execute_log_interaction",
        "EDIT_INTERACTION": "execute_edit_interaction",
        "CLEAR_FIELDS": "execute_clear_fields",
        "SUGGEST_FOLLOW_UP": "execute_suggest_follow_up",
        "GENERATE_SUMMARY": "execute_interaction_summary",
        "SEARCH_HCP": "execute_search_hcp",
        "GENERATE_EMAIL": "execute_generate_email",
        "GENERATE_NEXT_STEPS": "execute_generate_next_steps",
        "COMPLIANCE_CHECK": "execute_compliance_check",
    }
    return tool_intent_map.get(intent, "respond_to_user")


def execute_log_interaction(state: AgentState) -> dict:
    last_message = _last_user_message(state)
    result = tool_map["log_interaction"].invoke({"user_input": last_message})

    fields = result.get("fields", {})
    current = state.get("current_interaction", InteractionFields())
    if isinstance(current, dict):
        current = InteractionFields(**current)

    for key, value in fields.items():
        if value is not None:
            setattr(current, key, value)

    return {
        "current_interaction": current,
        "last_tool": "log_interaction",
        "last_tool_result": result,
    }


def execute_edit_interaction(state: AgentState) -> dict:
    last_message = _last_user_message(state)
    current_fields = state.get("current_interaction", {})
    if isinstance(current_fields, InteractionFields):
        current_fields = current_fields.model_dump(exclude_none=True)

    result = tool_map["edit_interaction"].invoke({
        "current_fields": {k: v for k, v in current_fields.items() if v is not None},
        "correction_text": last_message,
    })

    updated_fields = result.get("fields", {})
    current = state.get("current_interaction", InteractionFields())
    if isinstance(current, dict):
        current = InteractionFields(**current)

    for key, value in updated_fields.items():
        if value is not None:
            setattr(current, key, value)

    return {
        "current_interaction": current,
        "last_tool": "edit_interaction",
        "last_tool_result": result,
    }


def execute_clear_fields(state: AgentState) -> dict:
    last_message = _last_user_message(state)
    current_fields = state.get("current_interaction", {})
    if isinstance(current_fields, InteractionFields):
        current_fields = current_fields.model_dump(exclude_none=True)

    llm = get_llm()
    prompt = f"""User wants to clear fields. Message: {last_message}
Current fields: {current_fields}
Return ONLY a JSON array of field names to clear.
"""
    response = llm.invoke(prompt)
    content = response.content if hasattr(response, 'content') else str(response)
    json_match = re.search(r'\[.*?\]', content, re.DOTALL)
    fields_to_clear = []
    if json_match:
        try:
            raw_list = json.loads(json_match.group(0))
            normalized = _normalize_fields({f: True for f in raw_list})
            fields_to_clear = list(normalized.keys())
        except (json.JSONDecodeError, TypeError):
            fields_to_clear = []

    result = tool_map["clear_fields"].invoke({
        "current_fields": current_fields,
        "fields_to_clear": fields_to_clear if isinstance(fields_to_clear, list) else [fields_to_clear],
    })

    updated = result.get("fields", {})
    current = state.get("current_interaction", InteractionFields())
    if isinstance(current, dict):
        current = InteractionFields(**current)
    for key, value in updated.items():
        setattr(current, key, value)

    return {
        "current_interaction": current,
        "last_tool": "clear_fields",
        "last_tool_result": result,
    }


def execute_suggest_follow_up(state: AgentState) -> dict:
    current = state.get("current_interaction", {})
    if isinstance(current, InteractionFields):
        current = current.model_dump(exclude_none=True)

    result = tool_map["suggest_follow_up"].invoke({"interaction_details": current})

    return {
        "last_tool": "suggest_follow_up",
        "last_tool_result": result,
    }


def execute_interaction_summary(state: AgentState) -> dict:
    current = state.get("current_interaction", {})
    if isinstance(current, InteractionFields):
        current = current.model_dump(exclude_none=True)

    result = tool_map["interaction_summary"].invoke({"interaction_data": current})

    return {
        "last_tool": "interaction_summary",
        "last_tool_result": result,
    }


def execute_search_hcp(state: AgentState) -> dict:
    last_message = _last_user_message(state)
    result = tool_map["search_hcp"].invoke({"query": last_message})

    return {
        "last_tool": "search_hcp",
        "last_tool_result": result,
    }


def execute_generate_email(state: AgentState) -> dict:
    last_message = state["messages"][-1]["content"] if state["messages"] else ""
    current = state.get("current_interaction", {})
    if isinstance(current, InteractionFields):
        current = current.model_dump(exclude_none=True)

    result = tool_map["generate_email"].invoke({
        "recipient": current.get("hcp_name", "HCP"),
        "context": current,
    })

    return {
        "last_tool": "generate_email",
        "last_tool_result": result,
    }


def execute_generate_next_steps(state: AgentState) -> dict:
    current = state.get("current_interaction", {})
    if isinstance(current, InteractionFields):
        current = current.model_dump(exclude_none=True)

    result = tool_map["generate_next_steps"].invoke({"interaction_data": current})

    return {
        "last_tool": "generate_next_steps",
        "last_tool_result": result,
    }


def execute_compliance_check(state: AgentState) -> dict:
    current = state.get("current_interaction", {})
    if isinstance(current, InteractionFields):
        current = current.model_dump(exclude_none=True)

    result = tool_map["compliance_check"].invoke({"interaction_data": current})

    return {
        "last_tool": "compliance_check",
        "last_tool_result": result,
    }


def respond_to_user(state: AgentState) -> dict:
    last_tool_result = state.get("last_tool_result")
    last_tool = state.get("last_tool")

    if last_tool_result and last_tool:
        tool_response = last_tool_result.get("message", "")
        fields = last_tool_result.get("fields", {})
        summary = last_tool_result.get("summary", "")
        reasoning = last_tool_result.get("reasoning", "")
        action_type = last_tool_result.get("action_type", "")
        description = last_tool_result.get("description", "")
        priority = last_tool_result.get("priority", "")
        steps = last_tool_result.get("steps", [])

        if last_tool == "log_interaction":
            fields_text = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in fields.items() if v)
            content = (
                f"✅ **Interaction Logged Successfully**\n\n"
                f"I've recorded your interaction. Here is what I extracted:\n\n"
                f"{fields_text}\n\n"
                f"The form on the left has been updated with these details. "
                f"You can review and click **Save Interaction** to store it in the database."
            )
        elif last_tool == "edit_interaction":
            fields_text = "\n".join(f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in fields.items() if v)
            content = (
                f"✏️ **Interaction Updated**\n\n"
                f"I've made the corrections you requested. Here are the updated fields:\n\n"
                f"{fields_text}\n\n"
                f"All other fields remain unchanged. You can click **Save** to persist the changes."
            )
        elif last_tool == "clear_fields":
            cleared = last_tool_result.get("fields_to_clear", [])
            cleared_text = ", ".join(f"**{f.replace('_', ' ').title()}**" for f in cleared)
            content = (
                f"🗑️ **Fields Cleared**\n\n"
                f"I've cleared the following fields: {cleared_text}.\n\n"
                f"All other fields are still there. Let me know if you need anything else."
            )
        elif last_tool == "suggest_follow_up":
            content = (
                f"📋 **Follow-Up Suggestion**\n\n"
                f"Based on this interaction, I recommend:\n\n"
                f"- **Action**: {action_type}\n"
                f"- **Description**: {description}\n"
                f"- **Priority**: {priority.capitalize()}\n\n"
                f"**Reasoning**: {reasoning}\n\n"
                f"Would you like me to update the Follow Up fields with this suggestion?"
            )
        elif last_tool == "interaction_summary":
            content = (
                f"📝 **CRM Summary Generated**\n\n"
                f"{summary}\n\n"
                f"This summary is ready for your CRM records."
            )
        elif last_tool == "generate_next_steps" and steps:
            steps_text = "\n".join(f"- {step}" for step in steps)
            content = (
                f"📌 **Next Steps**\n\n"
                f"Here are your recommended next steps:\n\n"
                f"{steps_text}"
            )
        elif last_tool == "compliance_check":
            is_compliant = last_tool_result.get("is_compliant", True)
            issues = last_tool_result.get("issues", [])
            recommendations = last_tool_result.get("recommendations", [])
            if is_compliant:
                content = "✅ **Compliance Check Passed**\n\nThis interaction meets all healthcare compliance requirements."
            else:
                issues_text = "\n".join(f"- {issue}" for issue in issues)
                recs_text = "\n".join(f"- {rec}" for rec in recommendations)
                content = (
                    f"⚠️ **Compliance Issues Found**\n\n"
                    f"**Issues:**\n{issues_text}\n\n"
                    f"**Recommendations:**\n{recs_text}"
                )
        else:
            content = f"**{tool_response}**\n\n{summary}"
            if reasoning:
                content += f"\n\n**Reasoning:** {reasoning}"
    else:
        llm = get_llm()
        messages = state.get("messages", [])
        chat_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                chat_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                chat_messages.append(AIMessage(content=content))

        response = llm.invoke(chat_messages)
        content = response.content if hasattr(response, 'content') else str(response)

    return {"messages": [{"role": "assistant", "content": content}]}
