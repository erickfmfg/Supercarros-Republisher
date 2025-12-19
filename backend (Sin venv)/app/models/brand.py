
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    schedules = relationship("ScheduleBrand", back_populates="brand")
    runs = relationship("RepublicationRun", back_populates="brand")
