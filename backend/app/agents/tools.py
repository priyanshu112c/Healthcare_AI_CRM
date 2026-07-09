from datetime import date, datetime, time
from typing import Any
from langchain_core.tools import tool
from app.agents.schemas import (
    InteractionFields,
    LogInteractionOutput,
    EditInteractionOutput,
    ClearFieldsOutput,
    SuggestFollowUpOutput,
    InteractionSummaryOutput,
    SearchHCPOutput,
    MissingFieldDetectionOutput,
    GenerateEmailOutput,
    GenerateNextStepsOutput,
    ComplianceCheckOutput,
)
from app.agents.llm import get_llm
from app.agents.prompts import (
    MEDICAL_EXTRACTION_PROMPT,
    SUMMARY_PROMPT,
    FOLLOW_UP_PROMPT,
    CORRECTION_PROMPT,
    VALIDATION_PROMPT,
)


FIELD_NAME_MAP = {
    "hcp_name": "hcp_name", "hcp name": "hcp_name", "hcp/doctor name": "hcp_name",
    "doctor name": "hcp_name", "doctor_name": "hcp_name", "name": "hcp_name",
    "interaction_type": "interaction_type", "interaction type": "interaction_type",
    "type": "interaction_type",
    "date": "date",
    "time": "time",
    "attendees": "attendees", "attendee": "attendees",
    "topics": "topics", "topic": "topics",
    "materials": "materials", "material": "materials",
    "samples": "samples", "sample": "samples",
    "sentiment": "sentiment",
    "outcomes": "outcomes", "outcome": "outcomes",
    "follow_up_action": "follow_up_action", "follow up action": "follow_up_action",
    "follow_up": "follow_up_action", "follow up": "follow_up_action",
    "next_meeting": "next_meeting", "next meeting": "next_meeting",
    "priority": "priority",
}


def _normalize_fields(data: dict) -> dict:
    normalized = {}
    for key, value in data.items():
        mapped = FIELD_NAME_MAP.get(key.lower().strip())
        if mapped:
            normalized[mapped] = value
    return normalized


def _call_llm_for_extraction(prompt: str, text: str) -> dict:
    llm = get_llm()
    response = llm.invoke(f"{prompt}\n\nText: {text}\n\nReturn ONLY valid JSON.")
    import json
    import re
    content = response.content if hasattr(response, 'content') else str(response)
    json_match = re.search(r'```(?:json)?\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    else:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
    content = content.strip()
    try:
        return _normalize_fields(json.loads(content))
    except json.JSONDecodeError:
        return {}


def _get_current_date() -> str:
    return date.today().isoformat()


def _get_current_time() -> str:
    return datetime.now().strftime("%H:%M")


def _first_of(value, *alternatives):
    if value is not None and value != "" and value != []:
        return value
    for alt in alternatives:
        if alt is not None and alt != "" and alt != []:
            return alt
    return None


@tool
def log_interaction(user_input: str) -> dict[str, Any]:
    """Log a new interaction with an HCP. Extracts all fields from natural language."""
    extracted = _call_llm_for_extraction(MEDICAL_EXTRACTION_PROMPT, user_input)

    fields = InteractionFields()
    fields.hcp_name = _first_of(
        extracted.get("hcp_name"), extracted.get("doctor_name"), extracted.get("name")
    )
    fields.interaction_type = _first_of(
        extracted.get("interaction_type"), extracted.get("type")
    )
    fields.date = extracted.get("date") or _get_current_date()
    fields.time = extracted.get("time") or _get_current_time()
    fields.topics = _first_of(extracted.get("topics"), extracted.get("topic"))
    fields.sentiment = extracted.get("sentiment")
    fields.materials = _first_of(extracted.get("materials"), extracted.get("material"))
    fields.samples = _first_of(extracted.get("samples"), extracted.get("sample"))
    fields.attendees = _first_of(extracted.get("attendees"), extracted.get("attendee"))
    fields.outcomes = _first_of(extracted.get("outcomes"), extracted.get("outcome"))
    fields.follow_up_action = _first_of(
        extracted.get("follow_up_action"), extracted.get("follow_up")
    )
    fields.next_meeting = extracted.get("next_meeting")
    fields.priority = extracted.get("priority")

    dumped = fields.model_dump(exclude_none=True)

    if not fields.hcp_name:
        return {
            "tool": "log_interaction",
            "fields": dumped,
            "message": "I couldn't identify the HCP name. Could you please tell me the HCP's name?",
        }

    if not fields.interaction_type:
        return {
            "tool": "log_interaction",
            "fields": dumped,
            "message": f"I have the HCP name as {fields.hcp_name}, but what type of interaction was this? (Meeting, Call, Email, Conference, Follow-up)",
        }

    return {
        "tool": "log_interaction",
        "fields": dumped,
        "message": f"I've logged a {fields.interaction_type} with {fields.hcp_name}. The form has been updated with all the extracted information.",
    }


@tool
def edit_interaction(current_fields: dict[str, Any], correction_text: str) -> dict[str, Any]:
    """Edit one or more fields of an existing interaction. Only updates specified fields."""
    prompt = CORRECTION_PROMPT.format(current_fields=current_fields, correction_text=correction_text)
    extracted = _call_llm_for_extraction(prompt, correction_text)

    updated = dict(current_fields)
    for key, value in extracted.items():
        if value is not None and value != "" and key != "tool":
            updated[key] = value

    changed = [k for k, v in extracted.items() if v is not None and v != ""]
    return {
        "tool": "edit_interaction",
        "fields": updated,
        "message": f"I've updated the following fields: {', '.join(changed)}. Everything else stays the same.",
    }


@tool
def clear_fields(current_fields: dict[str, Any], fields_to_clear: list[str]) -> dict[str, Any]:
    """Clear specific fields from the form. Only clears requested fields."""
    updated = dict(current_fields)
    cleared = []
    for field in fields_to_clear:
        if field in updated:
            updated[field] = None
            cleared.append(field)

    return {
        "tool": "clear_fields",
        "fields": updated,
        "message": f"Cleared fields: {', '.join(cleared)}",
        "fields_to_clear": fields_to_clear,
    }


@tool
def suggest_follow_up(interaction_details: dict[str, Any]) -> dict[str, Any]:
    """Analyse the current interaction and suggest follow-up actions."""
    prompt = FOLLOW_UP_PROMPT.format(interaction_details=interaction_details)
    result = _call_llm_for_extraction(prompt, str(interaction_details))

    return {
        "tool": "suggest_follow_up",
        "action_type": result.get("action_type", "Follow-up"),
        "description": result.get("description", "Schedule a follow-up meeting"),
        "priority": result.get("priority", "medium"),
        "reasoning": result.get("reasoning", "Based on interaction context"),
        "message": f"I suggest a {result.get('action_type', 'Follow-up')} with {result.get('priority', 'medium')} priority. {result.get('reasoning', '')}",
    }


@tool
def interaction_summary(interaction_data: dict[str, Any]) -> dict[str, Any]:
    """Generate a concise CRM summary of the current interaction."""
    prompt = SUMMARY_PROMPT.format(
        hcp_name=interaction_data.get("hcp_name", "Unknown"),
        interaction_type=interaction_data.get("interaction_type", "Unknown"),
        date=interaction_data.get("date", "Unknown"),
        topics=interaction_data.get("topics", "N/A"),
        sentiment=interaction_data.get("sentiment", "N/A"),
        materials=interaction_data.get("materials", "N/A"),
        follow_up=interaction_data.get("follow_up_action", "N/A"),
    )
    llm = get_llm()
    response = llm.invoke(prompt)
    summary = response.content if hasattr(response, 'content') else str(response)

    return {
        "tool": "interaction_summary",
        "summary": summary,
        "message": f"I've generated a CRM-ready summary for this interaction with {interaction_data.get('hcp_name', 'the HCP')}.",
    }


@tool
def search_hcp(query: str) -> dict[str, Any]:
    """Search for an HCP by name or specialty."""
    return {
        "tool": "search_hcp",
        "query": query,
        "message": f"Searching for HCP: {query}",
    }


@tool
def missing_field_detection(interaction_data: dict[str, Any]) -> dict[str, Any]:
    """Detect missing required fields and generate questions to ask the user."""
    required_fields = ["hcp_name", "interaction_type", "date"]
    missing = []
    questions = []

    for field in required_fields:
        if not interaction_data.get(field):
            missing.append(field)

    field_questions = {
        "hcp_name": "What is the HCP's name?",
        "interaction_type": "What type of interaction was this? (Meeting, Call, Email, Conference, Follow-up)",
        "date": "When did this interaction take place?",
        "topics": "What topics were discussed?",
        "sentiment": "What was the observed sentiment?",
    }

    for field in missing:
        if field in field_questions:
            questions.append(field_questions[field])

    return {
        "tool": "missing_field_detection",
        "missing_fields": missing,
        "questions": questions,
        "message": f"Missing {len(missing)} required field(s).",
    }


@tool
def generate_email(recipient: str, context: dict[str, Any]) -> dict[str, Any]:
    """Generate a follow-up email to the HCP."""
    llm = get_llm()
    prompt = f"""Generate a professional follow-up email to {recipient}.
Context: {context}
The email should be polite, professional, and reference the interaction.
"""
    response = llm.invoke(prompt)
    body = response.content if hasattr(response, 'content') else str(response)

    return {
        "tool": "generate_email",
        "recipient": recipient,
        "subject": f"Follow-up regarding our recent discussion",
        "body": body,
        "message": "Email generated.",
    }


@tool
def generate_next_steps(interaction_data: dict[str, Any]) -> dict[str, Any]:
    """Generate suggested next steps based on the interaction."""
    llm = get_llm()
    prompt = f"""Based on this healthcare interaction:
{interaction_data}

Generate 3-5 specific next steps for the sales representative.
Return as a JSON array of strings.
"""
    response = llm.invoke(prompt)
    content = response.content if hasattr(response, 'content') else str(response)
    import json, re
    json_match = re.search(r'\[.*?\]', content, re.DOTALL)
    steps = []
    if json_match:
        try:
            steps = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            steps = [content]
    else:
        steps = [content]

    return {
        "tool": "generate_next_steps",
        "steps": steps if isinstance(steps, list) else [str(steps)],
        "message": "Next steps generated.",
    }


@tool
def compliance_check(interaction_data: dict[str, Any]) -> dict[str, Any]:
    """Check if the interaction complies with healthcare compliance rules."""
    llm = get_llm()
    prompt = f"""Perform a healthcare compliance check on this interaction:
{interaction_data}

Check for:
1. Samples distribution compliance
2. Data privacy concerns
3. Appropriate interaction documentation
4. Follow-up scheduling compliance

Return JSON with: is_compliant (bool), issues (list), recommendations (list)
"""
    response = llm.invoke(prompt)
    content = response.content if hasattr(response, 'content') else str(response)
    import json, re
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    result = {"is_compliant": True, "issues": [], "recommendations": []}
    if json_match:
        try:
            result = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return {
        "tool": "compliance_check",
        "is_compliant": result.get("is_compliant", True),
        "issues": result.get("issues", []),
        "recommendations": result.get("recommendations", []),
        "message": "Compliance check complete.",
    }


tools = [
    log_interaction,
    edit_interaction,
    clear_fields,
    suggest_follow_up,
    interaction_summary,
    search_hcp,
    missing_field_detection,
    generate_email,
    generate_next_steps,
    compliance_check,
]

tool_map = {t.name: t for t in tools}
