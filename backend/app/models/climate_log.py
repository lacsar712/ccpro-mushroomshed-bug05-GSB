from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClimateLog(Base):
    __tablename__ = "climate_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temp_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    co2_ppm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    room: Mapped["Room"] = relationship("Room", back_populates="climate_logs")
