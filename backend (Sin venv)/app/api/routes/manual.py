from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.brand import Brand
from app.models.run import RepublicationRun
from app.schemas.common import ManualRunRequest, ManualRunOut
from app.services.supercarros import run_republication_job

router = APIRouter()


@router.post("/run", response_model=List[ManualRunOut])
def run_manual_republication(
    request: ManualRunRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Ejecuta republicación manual:
      - Si all_brands = True => todas las marcas activas
      - Si brand_ids => solo esas marcas
    """
    if request.all_brands:
        brands = db.query(Brand).filter(Brand.is_active == True).all()
    else:
        if not request.brand_ids:
            raise HTTPException(
                status_code=400,
                detail="Debes seleccionar al menos una marca o marcar all_brands=true",
            )
        brands = (
            db.query(Brand)
            .filter(Brand.id.in_(request.brand_ids))
            .all()
        )

    if not brands:
        raise HTTPException(status_code=400, detail="No se encontraron marcas")

    brand_names = [b.name for b in brands]

    now = datetime.utcnow()
    outputs: List[ManualRunOut] = []

    try:
        results = run_republication_job(brand_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en republicación: {e}")

    for b in brands:
        count = int(results.get(b.name, 0))
        run = RepublicationRun(
            schedule_id=None,
            brand_id=b.id,
            user_id=current_user.id,
            vehicles_count=count,
            run_at=now,
            status="completed",
            is_manual=True,
        )
        db.add(run)

        outputs.append(
            ManualRunOut(
                brand_name=b.name,
                vehicles_count=count,
                run_at=now,
                status="Ejecutado",
            )
        )

    db.commit()
    return outputs


@router.get("/history", response_model=List[ManualRunOut])
def manual_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Historial de republicaciones manuales (últimas 100).
    """
    q = (
        db.query(RepublicationRun, Brand)
        .join(Brand, Brand.id == RepublicationRun.brand_id)
        .filter(RepublicationRun.is_manual == True)
        .order_by(RepublicationRun.run_at.desc())
        .limit(100)
    )

    results: List[ManualRunOut] = []
    for run, brand in q.all():
        status_label = {
            "completed": "Ejecutado",
            "running": "En proceso",
            "failed": "Fallido",
        }.get(run.status or "completed", "Ejecutado")
        results.append(
            ManualRunOut(
                brand_name=brand.name,
                vehicles_count=run.vehicles_count,
                run_at=run.run_at,
                status=status_label,
            )
        )
    return results
