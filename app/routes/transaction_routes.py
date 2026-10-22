
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.transaction import Transaction
from app.models.product import Product
from app.models.vendor import Vendor
from app.schemas.transaction_schema import TransactionCreate

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == transaction.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    vendor = db.query(Vendor).filter(
        Vendor.vendor_id == transaction.vendor_id
    ).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if transaction.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    new_transaction = Transaction(**transaction.model_dump())
    db.add(new_transaction)

    product.stock -= transaction.quantity

    db.commit()
    db.refresh(new_transaction)

    return {
        "message": "Transaction recorded successfully",
        "transaction_id": new_transaction.transaction_id,
        "product_id": new_transaction.product_id,
        "quantity": new_transaction.quantity,
        "amount": new_transaction.amount
    }
