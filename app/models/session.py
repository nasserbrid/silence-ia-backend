from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type_discours: Mapped[str] = mapped_column(String(50), nullable=False)
    type_discours_label: Mapped[str] = mapped_column(String(100), nullable=False)
    duree_prevue_min: Mapped[float] = mapped_column(Float, nullable=False)
    duree_effective_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    transcription: Mapped[str] = mapped_column(Text, nullable=False)
    analyse: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="sessions")  # noqa: F821
