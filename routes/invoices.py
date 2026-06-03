from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.invoice import Invoice
from auth.auth import get_current_user
from models.user import User

router = APIRouter()


# =========================
# GET INVOICES (ONLY USER)
# =========================
@router.get("/")
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Invoice).filter(
        Invoice.owner_id == current_user.id
    ).all()


# =========================
# CREATE INVOICE (WITH LIMIT)
# =========================
@router.post("/")
def create_invoice(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 🔒 FREE PLAN LIMIT
    if not current_user.is_premium and current_user.invoice_count >= 5:
        raise HTTPException(
            status_code=403,
            detail="Free plan limit reached (5 invoices). Upgrade to premium."
        )

    new_invoice = Invoice(
        title=data.get("title"),
        description=data.get("description"),
        amount=data.get("amount"),
        currency=data.get("currency", "EUR"),
        owner_id=current_user.id
    )

    db.add(new_invoice)

    # update usage counter
    current_user.invoice_count += 1

    db.commit()
    db.refresh(new_invoice)

    return new_invoice


# =========================
# GET SINGLE INVOICE (SECURE)
# =========================
@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.owner_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice


# =========================
# DELETE INVOICE (SECURE)
# =========================
@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.owner_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)

    # decrease counter
    current_user.invoice_count -= 1

    db.commit()

    return {"message": "Invoice deleted"}


# =========================
# UPDATE INVOICE (SECURE)
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
        Invoice.owner_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.title = data.get("title", invoice.title)
    invoice.description = data.get("description", invoice.description)
    invoice.amount = data.get("amount", invoice.amount)
    invoice.currency = data.get("currency", invoice.currency)

    db.commit()
    db.refresh(invoice)

    return invoice