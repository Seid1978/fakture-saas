from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from auth.security import get_current_user
from models.invoice import Invoice

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    invoices = db.query(Invoice)\
        .filter(Invoice.user_id == current_user.id)\
        .all()

    total_invoices = len(invoices)
    total_revenue = sum(i.amount for i in invoices)
    paid_invoices = len([i for i in invoices if i.status == "Paid"])

    return {
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "paid_invoices": paid_invoices,
        "pending_invoices": len([i for i in invoices if i.status == "Pending"])
    }