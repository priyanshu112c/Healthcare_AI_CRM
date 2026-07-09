import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.services.database.connection import Base
from app.services.database.models.mixin import TimestampMixin


class Sample(Base, TimestampMixin):
    __tablename__ = "samples"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interaction_id: Mapped[str] = mapped_column(String, ForeignKey("interaction.id"), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    interaction = relationship("Interaction", back_populates="samples")
