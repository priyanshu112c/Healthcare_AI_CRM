import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.services.database.connection import Base
from app.services.database.models.mixin import TimestampMixin, SoftDeleteMixin


class HCP(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "hcp"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    specialty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hospital: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    interactions = relationship("Interaction", back_populates="hcp", lazy="selectin")
