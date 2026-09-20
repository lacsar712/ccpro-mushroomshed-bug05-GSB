from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FlushHarvest(Base):
    __tablename__ = "flush_harvests"
    # intentionally no UniqueConstraint(room_id, flush_no)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    harvested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    flush_no: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(1), nullable=False)
    operator_name: Mapped[str] = mapped_column(String(64), nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="flush_harvests")
