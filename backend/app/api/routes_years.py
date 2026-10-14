from fastapi import APIRouter

from app.core.years import year_options
from app.models.schemas import YearOption

router = APIRouter(tags=["Yıl"])


@router.get("/years", response_model=list[YearOption])
def get_year_options():
    return year_options()
