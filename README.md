# Healthcare CRM Interaction Logger

An AI-powered healthcare CRM assistant that helps pharmaceutical sales representatives log, edit, and manage interactions with Healthcare Professionals (HCPs) using natural language.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, LangChain, LangGraph, Groq (LLaMA 3.3 70B) |
| **Database** | PostgreSQL, SQLAlchemy (async) |
| **Frontend** | React 18, Vite, Redux Toolkit, Tailwind CSS, React Hook Form |

## Architecture

```
┌──────────────┐       HTTP/JSON       ┌──────────────────┐
│   Frontend    │ ◄──────────────────► │    Backend API   │
│  (React/Vite) │     localhost:5173    │  (FastAPI 8000)  │
│               │  ┌─────────────────┐  │                  │
│  ┌─────────┐  │  │  /api/v1/chat   │  │  ┌────────────┐  │
│  │  Chat   │──┼──┤  /api/v1/tool   ├──┼──│  LangGraph  │  │
│  │  Window │  │  │  /api/v1/inter- │  │  │   Agent    │  │
│  │         │  │  │  action/*       │  │  │  (Groq AI) │  │
│  └─────────┘  │  └─────────────────┘  │  └─────┬──────┘  │
│  ┌─────────┐  │                        │        │        │
│  │Interaction│ │                        │  ┌────▼──────┐  │
│  │  Form    │  │                        │  │ PostgreSQL │  │
│  └─────────┘  │                        │  └───────────┘  │
└──────────────┘                        └──────────────────┘
```

## LangGraph Workflow

The core AI logic is a LangGraph **StateGraph** with 11 nodes and a conditional routing architecture:

```
                    ┌─────────────────────┐
                    │    User Message     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    detect_intent    │
                    │  (LLM classifies)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  route_after_intent │
                    │  (conditional edge) │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ LOG_INTERACTION │  │ EDIT_INTERACTION│  │ CLEAR_FIELDS    │
│ execute_log_    │  │ execute_edit_   │  │ execute_clear_  │
│ interaction     │  │ interaction     │  │ fields          │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ SUGGEST_FOLLOW_ │  │ GENERATE_SUMMARY│  │ SEARCH_HCP      │
│ UP              │  │ execute_inter-  │  │ execute_search_ │
│ execute_suggest │  │ action_summary  │  │ hcp             │
│ _follow_up      │  │                 │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ GENERATE_EMAIL  │  │ GENERATE_NEXT_  │  │ COMPLIANCE_CHECK│
│ execute_generate│  │ STEPS           │  │ execute_compli- │
│ _email          │  │ execute_generate│  │ ance_check      │
│                 │  │ _next_steps     │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────┬───────┴──────────┬──────────┘
                      │                  │
                      ▼                  ▼
            ┌─────────────────┐  ┌─────────────────┐
            │ GENERAL_CHAT    │  │  respond_to_user│
            │ (direct LLM)    │◄─┘  (all tool nodes│
            │                 │      route here)    │
            └────────┬────────┘  └────────┬────────┘
                     │                    │
                     └──────────┬─────────┘
                                │
                     ┌──────────▼──────────┐
                     │        END          │
                     └─────────────────────┘
```

### Agent State

```python
class AgentState(TypedDict):
    messages:           Annotated[list[dict], operator.add]   # Chat history
    current_interaction: InteractionFields                    # Active form data
    last_tool:          str | None                            # Last tool used
    last_tool_result:   ToolCallResult | None                 # Last tool output
    history:            Annotated[list[dict], operator.add]   # Full interaction log
    user_id:            str | None                            # Current user
    error:              str | None                            # Error state
    retry_count:        int                                   # Retry tracking
```

### Intent Types

| Intent | Node | Description |
|--------|------|-------------|
| `LOG_INTERACTION` | `execute_log_interaction` | Extract HCP interaction fields from natural language |
| `EDIT_INTERACTION` | `execute_edit_interaction` | Correct/update specific fields |
| `CLEAR_FIELDS` | `execute_clear_fields` | Clear selected form fields |
| `SUGGEST_FOLLOW_UP` | `execute_suggest_follow_up` | Generate follow-up recommendations |
| `GENERATE_SUMMARY` | `execute_interaction_summary` | Create CRM summary |
| `SEARCH_HCP` | `execute_search_hcp` | Search HCP database |
| `GENERATE_EMAIL` | `execute_generate_email` | Compose follow-up email |
| `GENERATE_NEXT_STEPS` | `execute_generate_next_steps` | Generate actionable next steps |
| `COMPLIANCE_CHECK` | `execute_compliance_check` | Healthcare compliance verification |
| `GENERAL_CHAT` | `respond_to_user` | General conversation (bypasses tools) |

## Project Structure

```
├── backend/
│   ├── .env                          # Environment variables
│   ├── requirements.txt              # Python dependencies
│   ├── app/
│   │   ├── main.py                   # FastAPI entry point
│   │   ├── config.py                 # Settings via pydantic-settings
│   │   ├── agents/                   # LangGraph AI Agent
│   │   │   ├── state.py              # AgentState TypedDict
│   │   │   ├── graph.py              # StateGraph definition & compilation
│   │   │   ├── nodes.py              # Node functions (intent + tools)
│   │   │   ├── tools.py              # @tool functions (10 tools)
│   │   │   ├── router.py             # Agent invocation & streaming
│   │   │   ├── schemas.py            # Pydantic I/O models
│   │   │   ├── prompts.py           # LLM system prompts
│   │   │   ├── llm.py                # ChatGroq factory
│   │   │   └── memory.py             # MemorySaver checkpointing
│   │   └── services/
│   │       ├── api/
│   │       │   └── routes.py         # FastAPI REST endpoints
│   │       └── database/
│   │           ├── connection.py      # Async SQLAlchemy engine
│   │           └── models/            # ORM models (8 tables)
│   └── tests/                        # Test suite
│
└── frontend/
    ├── package.json                  # Node dependencies
    ├── vite.config.js               # Vite + proxy to backend
    ├── tailwind.config.js            # Tailwind CSS config
    └── src/
        ├── main.jsx                  # React entry point
        ├── App.jsx                   # Root component
        ├── pages/
        │   └── Home.jsx              # Main split layout page
        ├── redux/                    # Redux Toolkit slices
        │   ├── store.js
        │   ├── chatSlice.js
        │   ├── interactionSlice.js
        │   ├── agentSlice.js
        │   └── uiSlice.js
        ├── services/
        │   └── api.js                # API client
        └── components/               # 13 React components
```

## How to Run

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (running on `localhost:5432`)

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
# Edit .env with your credentials:
#   CRM_GROQ_API_KEY=your_groq_api_key
#   CRM_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db_name

# 5. Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```



### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Send message to AI agent |
| `POST` | `/api/v1/tool` | Execute tool directly |
| `GET` | `/api/v1/interaction` | List all interactions |
| `POST` | `/api/v1/interaction` | Save interaction to DB |
| `PUT` | `/api/v1/interaction/{id}` | Update interaction |
| `DELETE` | `/api/v1/interaction/{id}` | Delete interaction |
| `GET` | `/api/v1/langgraph` | LangGraph Mermaid visualization |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/schema` | All Pydantic schemas |
