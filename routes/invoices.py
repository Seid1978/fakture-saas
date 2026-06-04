from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.invoice import Invoice
from models.user import User
from auth.auth import get_current_user

router = APIRouter(prefix="/invoices", tags=["Invoices"])


# =========================
# GET ALL (USER ONLY)
# =========================
@router.get("/")
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Invoice).filter(
        Invoice.user_id == current_user.id
    ).all()


# =========================
# CREATE INVOICE (LIMIT + SAFE)
# =========================
@router.post("/")
def create_invoice(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    client = data.get("client")
    amount = data.get("amount")
    description = data.get("description", "")
    status = data.get("status", "Pending")

    # =========================
    # VALIDATION
    # =========================
    if not client:
        raise HTTPException(status_code=400, detail="Client is required")

    if amount is None or amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")

    # =========================
    # FREE PLAN LIMIT
    # =========================
    if not current_user.is_premium:
        invoice_count = db.query(Invoice).filter(
            Invoice.user_id == current_user.id
        ).count()

        if invoice_count >= current_user.invoice_limit:
            raise HTTPException(
                status_code=403,
                detail="Free plan limit reached (5 invoices). Upgrade to premium."
            )

    # =========================
    # CREATE
    # =========================
    new_invoice = Invoice(
        client=client,
        amount=amount,
        status=status,
        user_id=current_user.id
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


# =========================
# GET ONE (SECURE)
# =========================
@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice


# =========================
# UPDATE (SAFE)
# =========================
@router.put("/{invoice_id}")
def update_invoice(
    invoice_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if "client" in data:
        invoice.client = data["client"]

    if "amount" in data:
        if data["amount"] <= 0:
            raise HTTPException(status_code=400, detail="Amount must be > 0")
        invoice.amount = data["amount"]

    if "status" in data:
        invoice.status = data["status"]

    db.commit()
    db.refresh(invoice)

    return invoice


# =========================
# DELETE (SECURE)
# =========================
@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()

    return {"message": "Invoice deleted"}