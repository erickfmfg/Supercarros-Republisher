
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, require_admin
from app.models.brand import Brand
from app.schemas.common import BrandCreate, BrandOut, BrandUpdate

router = APIRouter()


@router.get("/", response_model=List[BrandOut])
def list_brands(db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Brand).all()


@router.post("/", response_model=BrandOut)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
    existing = db.query(Brand).filter(Brand.name == brand_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="La marca ya existe")
    brand = Brand(name=brand_in.name, is_active=brand_in.is_active)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.put("/{brand_id}", response_model=BrandOut)
def update_brand(
    brand_id: int,
    brand_in: BrandUpdate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
    brand = db.query(Brand).get(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    if brand_in.name is not None:
        brand.name = brand_in.name
    if brand_in.is_active is not None:
        brand.is_active = brand_in.is_active
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin),
):
    brand = db.query(Brand).get(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    db.delete(brand)
    db.commit()
    return {"detail": "Marca eliminada"}
