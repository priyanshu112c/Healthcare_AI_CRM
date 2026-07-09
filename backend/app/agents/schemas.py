from datetime import date, time
from pydantic import BaseModel, Field


class InteractionFields(BaseModel):
    hcp_name: str | None = None
    interaction_type: str | None = None
    date: str | None = None
    time: str | None = None
    attendees: list[str] | None = None
    topics: str | None = None
    materials: list[str] | None = None
    samples: list[str] | None = None
    sentiment: str | None = None
    outcomes: str | None = None
    follow_up_action: str | None = None
    next_meeting: str | None = None
    priority: str | None = None


class ToolCallResult(BaseModel):
    tool: str = Field(description="Name of the tool that was called")
    success: bool = True
    message: str = ""
    fields: InteractionFields | None = None
    summary: str | None = None
    suggestions: list[str] | None = None
    reasoning: str | None = None


class LogInteractionOutput(BaseModel):
    tool: str = "log_interaction"
    fields: InteractionFields


class EditInteractionOutput(BaseModel):
    tool: str = "edit_interaction"
    fields: InteractionFields


class ClearFieldsOutput(BaseModel):
    tool: str = "clear_fields"
    fields_to_clear: list[str]


class SuggestFollowUpOutput(BaseModel):
    tool: str = "suggest_follow_up"
    action_type: str
    description: str
    priority: str
    reasoning: str


class InteractionSummaryOutput(BaseModel):
    tool: str = "interaction_summary"
    summary: str


class SearchHCPOutput(BaseModel):
    tool: str = "search_hcp"
    query: str


class MissingFieldDetectionOutput(BaseModel):
    tool: str = "missing_field_detection"
    missing_fields: list[str]
    questions: list[str]


class GenerateEmailOutput(BaseModel):
    tool: str = "generate_email"
    recipient: str
    subject: str
    body: str


class GenerateNextStepsOutput(BaseModel):
    tool: str = "generate_next_steps"
    steps: list[str]


class ComplianceCheckOutput(BaseModel):
    tool: str = "compliance_check"
    is_compliant: bool
    issues: list[str]
    recommendations: list[str]


class ConversationState(BaseModel):
    messages: list[dict] = []
    current_interaction: InteractionFields = Field(default_factory=InteractionFields)
    last_tool: str | None = None
    last_tool_result: ToolCallResult | None = None
    history: list[dict] = []
