from datetime import datetime, timedelta, time
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.schedule import Schedule, ScheduleBrand
from app.models.brand import Brand
from app.models.run import RepublicationRun
from app.services.supercarros import run_republication_job

scheduler: Optional[BackgroundScheduler] = None
JOB_PREFIX = "schedule_"


def compute_next_run_for_schedule(
    schedule: Schedule, from_dt: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calcula la próxima ejecución en base a days_of_week y times_of_day.
    Devuelve un datetime o None si no hay configuración válida.
    """
    if not schedule.days_of_week or not schedule.times_of_day:
        return None

    now = from_dt or datetime.utcnow()
    today = now.date()
    now_weekday = now.weekday()

    # mapear strings a números de día (lunes=0 ... domingo=6)
    weekday_map = {
        "mon": 0,
        "monday": 0,
        "tue": 1,
        "tuesday": 1,
        "wed": 2,
        "wednesday": 2,
        "thu": 3,
        "thursday": 3,
        "fri": 4,
        "friday": 4,
        "sat": 5,
        "saturday": 5,
        "sun": 6,
        "sunday": 6,
    }

    days = [
        d.strip().lower()
        for d in schedule.days_of_week.split(",")
        if d and d.strip()
    ]
    times = [
        t.strip()
        for t in schedule.times_of_day.split(",")
        if t and t.strip()
    ]

    if not days or not times:
        return None

    candidates = []

    for d in days:
        if d not in weekday_map:
            continue
        target_w = weekday_map[d]
        days_ahead = (target_w - now_weekday) % 7

        for time_str in times:
            try:
                hour, minute = [int(x) for x in time_str.split(":", 1)]
            except Exception:
                continue

            candidate_date = today + timedelta(days=days_ahead)
            candidate_dt = datetime.combine(
                candidate_date, time(hour=hour, minute=minute)
            )
            # si ya pasó hoy, empuja a la próxima semana
            if candidate_dt <= now:
                candidate_dt = candidate_dt + timedelta(days=7)
            candidates.append(candidate_dt)

    if not candidates:
        return None

    return min(candidates)


def _schedule_job(schedule_id: int):
    """
    Función que ejecuta realmente la republicación programada para un schedule.
    """
    db: Session = SessionLocal()
    try:
        schedule = db.query(Schedule).get(schedule_id)
        if not schedule or not schedule.is_active:
            return

        links = (
            db.query(ScheduleBrand)
            .filter(ScheduleBrand.schedule_id == schedule.id)
            .all()
        )
        brand_names = []
        for link in links:
            brand = db.query(Brand).get(link.brand_id)
            if brand:
                brand_names.append(brand.name)

        if not brand_names:
            return

        results = run_republication_job(brand_names)
        now = datetime.utcnow()

        # guardar corridas
        for brand_name, count in results.items():
            brand = (
                db.query(Brand).filter(Brand.name == brand_name).first()
            )
            if brand and count >= 0:
                run = RepublicationRun(
                    schedule_id=schedule.id,
                    brand_id=brand.id,
                    vehicles_count=count,
                    run_at=now,
                    status="completed",
                    is_manual=False,
                )
                db.add(run)

        schedule.last_run_at = now
        schedule.next_run_at = compute_next_run_for_schedule(schedule, now)
        db.add(schedule)
        db.commit()
    finally:
        db.close()


def refresh_schedule_job(schedule_id: int, db: Session):
    """
    Crea o actualiza uno o varios jobs de APScheduler para una programación,
    basado en days_of_week y times_of_day.
    """
    global scheduler
    if scheduler is None:
        return

    schedule = db.query(Schedule).get(schedule_id)
    if not schedule:
        return

    # eliminar jobs existentes de este schedule
    prefix = f"{JOB_PREFIX}{schedule.id}_"
    for job in list(scheduler.get_jobs()):
        if job.id.startswith(prefix):
            try:
                scheduler.remove_job(job.id)
            except Exception:
                pass

    if not schedule.is_active or not schedule.days_of_week or not schedule.times_of_day:
        return

    # construir trigger cron por cada hora configurada
    days_str = schedule.days_of_week  # ej: "mon,wed,fri"
    time_strings = [
        t.strip()
        for t in schedule.times_of_day.split(",")
        if t and t.strip()
    ]

    for t_str in time_strings:
        try:
            hour, minute = [int(x) for x in t_str.split(":", 1)]
        except Exception:
            continue

        trigger = CronTrigger(
            day_of_week=days_str,
            hour=hour,
            minute=minute,
        )
        job_id = f"{JOB_PREFIX}{schedule.id}_{hour:02d}{minute:02d}"
        scheduler.add_job(
            _schedule_job,
            trigger=trigger,
            id=job_id,
            args=[schedule.id],
            replace_existing=True,
        )


def remove_schedule_job(schedule_id: int):
    global scheduler
    if scheduler is None:
        return
    prefix = f"{JOB_PREFIX}{schedule_id}_"
    for job in list(scheduler.get_jobs()):
        if job.id.startswith(prefix):
            try:
                scheduler.remove_job(job.id)
            except Exception:
                pass


def load_all_schedules():
    db: Session = SessionLocal()
    try:
        schedules = db.query(Schedule).filter(Schedule.is_active == True).all()
        for s in schedules:
            refresh_schedule_job(s.id, db)
    finally:
        db.close()


def start_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.start()
        load_all_schedules()


def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
