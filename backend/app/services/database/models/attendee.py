import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.services.database.connection import Base
from app.services.database.models.mixin import TimestampMixin


class Attendee(Base, TimestampMixin):
    __tablename__ = "attendees"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interaction_id: Mapped[str] = mapped_column(String, ForeignKey("interaction.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    interaction = relationship("Interaction", back_populates="attendees")
