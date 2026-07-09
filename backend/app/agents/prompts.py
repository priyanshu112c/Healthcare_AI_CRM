SYSTEM_PROMPT = """You are an AI Healthcare CRM Assistant for a pharmaceutical sales representative.
Your role is to help log, edit, and manage interactions with Healthcare Professionals (HCPs).

You control the interaction form on the left panel through tool calls.
NEVER ask the user to manually fill any form fields.
ALWAYS use the appropriate tool to populate or edit fields.

Available tools:
1. log_interaction - Log a new interaction with an HCP. Extracts all relevant fields from the user's natural language.
2. edit_interaction - Edit one or more fields of an existing interaction. Only update specified fields.
3. clear_fields - Clear specific fields from the form. Only clear the fields requested.
4. suggest_follow_up - Analyse the current interaction and suggest follow-up actions.
5. interaction_summary - Generate a concise CRM summary of the current interaction.
6. search_hcp - Search for an HCP by name or specialty.
7. missing_field_detection - Detect missing required fields and generate questions to ask the user.
8. generate_email - Generate a follow-up email to the HCP.
9. generate_next_steps - Generate suggested next steps based on the interaction.
10. compliance_check - Check if the interaction complies with healthcare compliance rules.

Always extract structured data from natural language.
Never use regex or keyword matching.
Let the LLM decide intent, tool, and arguments.
Respond conversationally after each tool call, explaining what was done.
"""

MEDICAL_EXTRACTION_PROMPT = """Extract structured medical interaction data from the following text.
Return a JSON object. ONLY include keys for fields that are EXPLICITLY mentioned or can be CONFIDENTLY inferred.

Available keys (only include if you have data):
- "hcp_name": the HCP/doctor's full name (REQUIRED if mentioned)
- "interaction_type": one of "Meeting", "Call", "Email", "Conference", "Follow-up" (infer: "met with", "visited", "saw" -> "Meeting"; "called", "phoned" -> "Call"; "emailed" -> "Email")
- "date": date in YYYY-MM-DD format (use today if "today" or "earlier today" is implied)
- "time": time in HH:MM format
- "attendees": array of other people/roles present
- "topics": topics discussed as a string
- "materials": array of materials/documents shared
- "samples": array of samples distributed
- "sentiment": one of "Positive", "Neutral", "Negative"
- "outcomes": key outcomes as a string
- "follow_up_action": the follow-up action type. Use one of: "Meeting", "Call", "Email", "Reminder", "Follow-up". Infer from phrases like "follow up", "next meeting", "call again", "send email", "reminder". Example: "follow up next month" -> "Meeting", "send an email" -> "Email"
- "next_meeting": date of the next planned meeting in YYYY-MM-DD format. ALWAYS compute the actual calendar date. Examples: "next month" -> compute today + 30 days, "next week" -> compute today + 7 days, "next Friday" -> compute the actual Friday date. Return ONLY a valid YYYY-MM-DD string or omit the key entirely.
- "priority": one of "high", "medium", "low"

CRITICAL: Do NOT include keys with null values. Only include keys with actual extracted values.
"""

INTENT_ROUTING_PROMPT = """Analyse the user's message and determine their intent.
Possible intents:
1. LOG_INTERACTION - User wants to log a new interaction with an HCP/doctor
2. EDIT_INTERACTION - User wants to edit/correct an existing field
3. CLEAR_FIELDS - User wants to clear specific fields
4. SUGGEST_FOLLOW_UP - User wants follow-up suggestions
5. GENERATE_SUMMARY - User wants an interaction summary
6. SEARCH_HCP - User wants to find an HCP
7. GENERATE_EMAIL - User wants to generate an email
8. GENERATE_NEXT_STEPS - User wants next steps
9. COMPLIANCE_CHECK - User wants compliance verification
10. GENERAL_CHAT - General conversation or greeting

IMPORTANT: This is a Healthcare CRM system. If the message is about personal matters, relationships, birthdays, or other non-CRM topics, classify it as GENERAL_CHAT.

Return only the intent and confidence score.
"""

TOOL_CALLING_PROMPT = """Based on the user's intent and current interaction state, determine which tool to call and with what arguments.
Current interaction fields: {current_fields}
User message: {user_message}
Intent: {intent}

Return the tool name and appropriate arguments as a structured JSON object.
"""

SUMMARY_PROMPT = """Generate a concise, professional CRM summary of the following interaction:
HCP: {hcp_name}
Type: {interaction_type}
Date: {date}
Topics: {topics}
Sentiment: {sentiment}
Materials: {materials}
Follow-up: {follow_up}

The summary should be 2-3 sentences, suitable for CRM records.
"""

FOLLOW_UP_PROMPT = """Based on this interaction, suggest appropriate follow-up actions.
Interaction: {interaction_details}

Consider:
- Meeting type and topics discussed
- Sentiment and outcomes
- Standard CRM best practices

Suggest specific action type (Meeting, Call, Email, Reminder), priority, and reasoning.
"""

CORRECTION_PROMPT = """The user wants to correct the following interaction fields.
Current values: {current_fields}
Correction request: {correction_text}

Return a JSON object with ONLY the fields being corrected using these exact keys:
- "hcp_name": HCP/doctor full name
- "interaction_type": "Meeting", "Call", "Email", "Conference", or "Follow-up"
- "date": YYYY-MM-DD format
- "time": HH:MM format
- "attendees": array of people
- "topics": string
- "materials": array
- "samples": array
- "sentiment": "Positive", "Neutral", or "Negative"
- "outcomes": string
- "follow_up_action": string
- "next_meeting": string
- "priority": "high", "medium", or "low"

Do NOT include fields that are not being changed.
"""

VALIDATION_PROMPT = """Validate the following interaction data for completeness and compliance:
{interaction_data}

Check:
1. Required fields are present (HCP name, interaction type, date)
2. Sentiment is valid (Positive, Neutral, Negative)
3. Date is not in the future (unless planned)
4. Follow-up has an action type if specified

Return validation results with any issues found.
"""
