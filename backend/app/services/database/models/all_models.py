from app.services.database.models.hcp import HCP
from app.services.database.models.interaction import Interaction
from app.services.database.models.attendee import Attendee
from app.services.database.models.material import Material
from app.services.database.models.sample import Sample
from app.services.database.models.followup import FollowUp
from app.services.database.models.chat_history import ChatHistory
from app.services.database.models.tool_log import ToolLog
from app.services.database.models.user import User

all_models = [
    HCP,
    Interaction,
    Attendee,
    Material,
    Sample,
    FollowUp,
    ChatHistory,
    ToolLog,
    User,
]
