from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ==== USERS ====


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str = "user"
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ==== BRANDS ====


class BrandBase(BaseModel):
    name: str
    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class BrandOut(BrandBase):
    id: int

    class Config:
        orm_mode = True


# ==== SCHEDULES ====


class ScheduleBase(BaseModel):
    name: str
    # intervalo ya no es obligatorio, lo dejamos opcional por compatibilidad
    interval_minutes: Optional[int] = None
    is_active: bool = True
    brand_ids: List[int]

    # NUEVO: días y horas como strings CSV
    # días: "mon,tue,wed", horas: "09:00,14:30"
    days_of_week: str
    times_of_day: str


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    interval_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    brand_ids: Optional[List[int]] = None
    days_of_week: Optional[str] = None
    times_of_day: Optional[str] = None


class ScheduleOut(BaseModel):
    id: int
    name: str
    interval_minutes: Optional[int]
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    days_of_week: Optional[str] = None
    times_of_day: Optional[str] = None
    # tomamos de la propiedad brands_list del modelo SQLAlchemy
    brands: List[BrandOut] = Field(default_factory=list, alias="brands_list")

    class Config:
        orm_mode = True
        populate_by_name = True


# ==== STATS ====


class BrandStatsItem(BaseModel):
    brand_name: str
    date: datetime
    vehicles_count: int


# ==== MANUAL RUNS ====


class ManualRunRequest(BaseModel):
    brand_ids: Optional[List[int]] = None
    all_brands: bool = False


class ManualRunOut(BaseModel):
    brand_name: str
    vehicles_count: int
    run_at: datetime
    status: str
