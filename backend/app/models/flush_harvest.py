from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FlushHarvest(Base):
    __tablename__ = "flush_harvests"
    # 同一间出菇房内，潮次序号不可重复
    __table_args__ = (
        UniqueConstraint("room_id", "flush_no", name="uq_flush_harvest_room_flush"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    harvested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    flush_no: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(1), nullable=False)
    operator_name: Mapped[str] = mapped_column(String(64), nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="flush_harvests")
