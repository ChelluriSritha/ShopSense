from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.product import Product
from app.models.vendor import Vendor
from app.schemas.product_schema import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(
        Vendor.vendor_id == product.vendor_id
    ).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()