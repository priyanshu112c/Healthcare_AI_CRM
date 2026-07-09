import uuid
from datetime import date, time
from sqlalchemy import String, Date, Time, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.services.database.connection import Base
from app.services.database.models.mixin import TimestampMixin, SoftDeleteMixin


class Interaction(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "interaction"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    hcp_id: Mapped[str] = mapped_column(String, ForeignKey("hcp.id"), nullable=False, index=True)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    interaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    interaction_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    topics: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    outcomes: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="interactions", lazy="selectin")
    hcp = relationship("HCP", back_populates="interactions", lazy="selectin")
    attendees = relationship("Attendee", back_populates="interaction", lazy="selectin", cascade="all, delete-orphan")
    materials = relationship("Material", back_populates="interaction", lazy="selectin", cascade="all, delete-orphan")
    samples = relationship("Sample", back_populates="interaction", lazy="selectin", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="interaction", lazy="selectin", cascade="all, delete-orphan")
