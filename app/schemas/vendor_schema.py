from pydantic import BaseModel, EmailStr


class VendorCreate(BaseModel):
    business_name: str
    owner_name: str
    email: EmailStr
    phone: str
    category: str | None = None


class VendorResponse(BaseModel):
    vendor_id: int
    business_name: str
    owner_name: str
    email: EmailStr
    phone: str
    category: str | None = None
    status: str

    class Config:
        from_attributes = True