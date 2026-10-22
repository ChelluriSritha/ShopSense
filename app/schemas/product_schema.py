from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    product_name: str
    category: str | None = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    vendor_id: int = Field(gt=0)


class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    category: str | None = None
    price: float
    stock: int
    vendor_id: int

    class Config:
        from_attributes = True