
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_active_user
from app.models.run import RepublicationRun
from app.models.brand import Brand
from app.schemas.common import BrandStatsItem

router = APIRouter()


@router.get("/brands/last-month", response_model=List[BrandStatsItem])
def brand_stats_last_month(
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user),
):
    now = datetime.utcnow()
    from_date = now - timedelta(days=30)

    q = (
        db.query(
            Brand.name.label("brand_name"),
            func.date(RepublicationRun.run_at).label("date"),
            func.sum(RepublicationRun.vehicles_count).label("vehicles_count"),
        )
        .join(Brand, Brand.id == RepublicationRun.brand_id)
        .filter(RepublicationRun.run_at >= from_date)
        .group_by(Brand.name, func.date(RepublicationRun.run_at))
        .order_by(func.date(RepublicationRun.run_at).asc())
    )

    results = []
    for row in q.all():
        results.append(
            BrandStatsItem(
                brand_name=row.brand_name,
                date=row.date,
                vehicles_count=row.vehicles_count,
            )
        )
    return results
