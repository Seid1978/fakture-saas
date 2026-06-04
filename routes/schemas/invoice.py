from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# =========================
# CREATE INVOICE
# =========================
class InvoiceCreate(BaseModel):
    client: str
    amount: float
    status: Optional[str] = "Pending"
    description: Optional[str] = None


# =========================
# UPDATE INVOICE
# =========================
class InvoiceUpdate(BaseModel):
    client: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None


# =========================
# RESPONSE MODEL (API OUTPUT)
# =========================
class InvoiceOut(BaseModel):
    id: int
    client: str
    amount: float
    status: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }