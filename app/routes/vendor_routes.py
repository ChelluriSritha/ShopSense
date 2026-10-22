from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.vendor import Vendor
from app.schemas.vendor_schema import VendorCreate, VendorResponse

router = APIRouter(prefix="/vendors", tags=["Vendors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=VendorResponse)
def register_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    existing_vendor = db.query(Vendor).filter(
        Vendor.email == vendor.email
    ).first()

    if existing_vendor:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_vendor = Vendor(**vendor.model_dump())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return new_vendor

@router.get("/")
def get_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).order_by(Vendor.vendor_id).all()
