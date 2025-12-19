from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class RepublicationRun(Base):
    __tablename__ = "republication_runs"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    vehicles_count = Column(Integer, nullable=False, default=0)
    run_at = Column(DateTime, default=datetime.utcnow)

    # NUEVO: estado y si fue manual
    status = Column(String(20), default="completed")  # completed, running, failed
    is_manual = Column(Boolean, default=False)

    schedule = relationship("Schedule", back_populates="runs")
    brand = relationship("Brand", back_populates="runs")
    user = relationship("User", back_populates="runs")
