from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from auth.auth_utils import get_current_user
from models.user import User
from models.invoice import Invoice

router = APIRouter(prefix="/user", tags=["User"])


# =========================
# DB SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# GET CURRENT USER (/me)
# =========================
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "invoice_limit": current_user.invoice_limit,
    }


# =========================
# DASHBOARD STATS (SAAS V5)
# =========================
@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id
    ).all()

    total_invoices = len(invoices)

    paid_invoices = len(
        [i for i in invoices if i.status == "Paid"]
    )

    pending_invoices = len(
        [i for i in invoices if i.status == "Pending"]
    )

    cancelled_invoices = len(
        [i for i in invoices if i.status == "Cancelled"]
    )

    total_revenue = sum(
        i.amount for i in invoices if i.status == "Paid"
    )

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "is_premium": current_user.is_premium,
            "invoice_limit": current_user.invoice_limit,
        },
        "stats": {
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "pending_invoices": pending_invoices,
            "cancelled_invoices": cancelled_invoices,
            "total_revenue": total_revenue,
            "remaining_limit": None
            if current_user.is_premium
            else max(0, current_user.invoice_limit - total_invoices)
        }
    }