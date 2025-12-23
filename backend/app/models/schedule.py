from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # ya no usamos interval_minutes para la lógica nueva, pero lo dejamos opcional
    interval_minutes = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)

    # NUEVO: configuración de días y horas
    # días como string CSV, ej: "mon,wed,fri"
    days_of_week = Column(String(50), nullable=True)
    # horas como string CSV, ej: "09:00,14:30"
    times_of_day = Column(String(200), nullable=True)

    # relación con la tabla puente
    brands = relationship("ScheduleBrand", back_populates="schedule")
    runs = relationship("RepublicationRun", back_populates="schedule")

    @property
    def brands_list(self):
        """
        Lista de Brand asociados a este schedule.
        Esto es lo que usamos en el esquema ScheduleOut.brands.
        """
        return [sb.brand for sb in self.brands if sb.brand is not None]


class ScheduleBrand(Base):
    __tablename__ = "schedule_brands"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)

    schedule = relationship("Schedule", back_populates="brands")
    brand = relationship("Brand", back_populates="schedules")
