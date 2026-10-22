from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models.transaction import Transaction
from app.models.product import Product

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def get_sales_summary(db: Session = Depends(get_db)):
    total_revenue = db.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()

    total_transactions = db.query(Transaction).count()

    total_products = db.query(Product).count()

    return {
        "total_revenue": float(total_revenue),
        "total_transactions": total_transactions,
        "total_products": total_products
    }


@router.get("/product-performance")
def get_product_performance(db: Session = Depends(get_db)):
    results = (
        db.query(
            Product.product_id,
            Product.product_name,
            func.coalesce(func.sum(Transaction.quantity), 0).label("units_sold"),
            func.coalesce(func.sum(Transaction.amount), 0).label("revenue")
        )
        .outerjoin(
            Transaction,
            Product.product_id == Transaction.product_id
        )
        .group_by(Product.product_id, Product.product_name)
        .all()
    )

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "units_sold": int(row.units_sold),
            "revenue": float(row.revenue)
        }
        for row in results
    ]