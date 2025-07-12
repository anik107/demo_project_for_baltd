from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from location_utils import get_all_divisions, get_districts_by_division, get_thanas_by_district
from schemas import Division, District, Thana

router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/divisions", response_model=list[Division])
async def get_divisions(db: Session = Depends(get_db)):
    """Get all divisions"""
    divisions = get_all_divisions(db)
    return divisions

@router.get("/divisions/{division_id}/districts", response_model=list[District])
async def get_districts(division_id: int, db: Session = Depends(get_db)):
    """Get districts by division"""
    districts = get_districts_by_division(db, division_id)
    return districts

@router.get("/districts/{district_id}/thanas", response_model=list[Thana])
async def get_thanas(district_id: int, db: Session = Depends(get_db)):
    """Get thanas by district"""
    thanas = get_thanas_by_district(db, district_id)
    return thanas
