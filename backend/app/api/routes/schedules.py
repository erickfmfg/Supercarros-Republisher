from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, require_admin
from app.models.brand import Brand
from app.models.schedule import Schedule, ScheduleBrand
from app.models.run import RepublicationRun
from app.schemas.common import ScheduleCreate, ScheduleOut, ScheduleUpdate
from app.services.scheduler import (
    refresh_schedule_job,
    remove_schedule_job,
    compute_next_run_for_schedule,
)
from app.services.supercarros import run_republication_job

router = APIRouter()


@router.get("/", response_model=List[ScheduleOut])
def list_schedules(
    db: Session = Depends(get_db), user=Depends(get_current_active_user)
):
    schedules = db.query(Schedule).all()
    return schedules


@router.post("/", response_model=ScheduleOut)
def create_schedule(
    schedule_in: ScheduleCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    # Validaciones básicas
    if not schedule_in.days_of_week:
        raise HTTPException(
            status_code=400,
            detail="Debes seleccionar al menos un día de la semana",
        )
    if not schedule_in.times_of_day:
        raise HTTPException(
            status_code=400,
            detail="Debes seleccionar al menos una hora",
        )
    if not schedule_in.brand_ids:
        raise HTTPException(
            status_code=400,
            detail="Debes seleccionar al menos una marca",
        )

    schedule = Schedule(
        name=schedule_in.name,
        interval_minutes=schedule_in.interval_minutes,
        is_active=schedule_in.is_active,
        days_of_week=schedule_in.days_of_week,
        times_of_day=schedule_in.times_of_day,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    # Asociar marcas
    for brand_id in schedule_in.brand_ids:
        brand = db.query(Brand).get(brand_id)
        if brand:
            sb = ScheduleBrand(schedule_id=schedule.id, brand_id=brand.id)
            db.add(sb)
    db.commit()
    db.refresh(schedule)

    # Calcular próxima ejecución y registrar job
    schedule.next_run_at = compute_next_run_for_schedule(schedule)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    refresh_schedule_job(schedule.id, db)
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleOut)
def update_schedule(
    schedule_id: int,
    schedule_in: ScheduleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    schedule = db.query(Schedule).get(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Programación no encontrada")

    if schedule_in.name is not None:
        schedule.name = schedule_in.name
    if schedule_in.interval_minutes is not None:
        schedule.interval_minutes = schedule_in.interval_minutes
    if schedule_in.is_active is not None:
        schedule.is_active = schedule_in.is_active
    if schedule_in.days_of_week is not None:
        schedule.days_of_week = schedule_in.days_of_week
    if schedule_in.times_of_day is not None:
        schedule.times_of_day = schedule_in.times_of_day

    db.add(schedule)
    db.commit()

    # actualizar marcas si llegan
    if schedule_in.brand_ids is not None:
        db.query(ScheduleBrand).filter(
            ScheduleBrand.schedule_id == schedule.id
        ).delete()
        for brand_id in schedule_in.brand_ids:
            brand = db.query(Brand).get(brand_id)
            if brand:
                sb = ScheduleBrand(schedule_id=schedule.id, brand_id=brand.id)
                db.add(sb)
        db.commit()

    db.refresh(schedule)

    # recalcular próxima ejecución y actualizar jobs
    schedule.next_run_at = compute_next_run_for_schedule(schedule)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    refresh_schedule_job(schedule.id, db)
    return schedule


@router.post("/{schedule_id}/run-once")
def run_schedule_once(
    schedule_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user),
):
    schedule = db.query(Schedule).get(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Programación no encontrada")

    # obtener nombres de marcas
    brand_links = (
        db.query(ScheduleBrand)
        .filter(ScheduleBrand.schedule_id == schedule.id)
        .all()
    )
    brand_names = []
    for bl in brand_links:
        brand = db.query(Brand).get(bl.brand_id)
        if brand:
            brand_names.append(brand.name)

    if not brand_names:
        raise HTTPException(
            status_code=400, detail="La programación no tiene marcas asociadas"
        )

    # correr playwright
    results = run_republication_job(brand_names)

    now = datetime.utcnow()
    for brand_name, count in results.items():
        brand = db.query(Brand).filter(Brand.name == brand_name).first()
        if brand and count >= 0:
            run = RepublicationRun(
                schedule_id=schedule.id,
                brand_id=brand.id,
                user_id=user.id,
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
    db.refresh(schedule)

    return {"detail": "Ejecución manual completada", "results": results}


@router.post("/{schedule_id}/pause")
def pause_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    schedule = db.query(Schedule).get(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    schedule.is_active = False
    db.add(schedule)
    db.commit()
    remove_schedule_job(schedule.id)
    return {"detail": "Programación pausada"}


@router.post("/{schedule_id}/resume")
def resume_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    schedule = db.query(Schedule).get(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    schedule.is_active = True
    db.add(schedule)
    db.commit()
    refresh_schedule_job(schedule.id, db)
    return {"detail": "Programación reanudada"}


@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    schedule = db.query(Schedule).get(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Programación no encontrada")

    # Detener y eliminar jobs del scheduler
    remove_schedule_job(schedule.id)

    # 1) Borrar explícitamente las relaciones ScheduleBrand
    #    para que no intente poner schedule_id = NULL (que viola NOT NULL)
    for sb in list(schedule.brands):
        db.delete(sb)
    db.commit()

    # 2) Ahora sí, borrar la programación
    db.delete(schedule)
    db.commit()

    return {"detail": "Programación eliminada"}

