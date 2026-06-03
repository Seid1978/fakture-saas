from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth.auth import get_current_user
from models.user import User
from models.invoice import Invoice

router = APIRouter()


# =========================
# GET CURRENT USER
# =========================
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "invoice_count": current_user.invoice_count
    }


# =========================
# DASHBOARD DATA
# =========================
@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoices = db.query(Invoice).filter(
        Invoice.owner_id == current_user.id
    ).all()

    total = len(invoices)
    paid = len([i for i in invoices if i.is_paid])
    unpaid = total - paid

    return {
        "user": {
            "email": current_user.email,
            "is_premium": current_user.is_premium,
            "invoice_count": current_user.invoice_count
        },
        "stats": {
            "total_invoices": total,
            "paid_invoices": paid,
            "unpaid_invoices": unpaid,
            "limit": None if current_user.is_premium else 5
        }
    }