
from pydantic import BaseModel, Field
from datetime import date

class TransactionCreate(BaseModel):
    product_id: int = Field(gt=0)
    vendor_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    amount: float = Field(gt=0)
    transaction_date: date
