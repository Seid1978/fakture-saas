from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.invoice import Invoice

router = APIRouter(prefix="/invoices", tags=["Invoices"])


# GET ALL INVOICES
@router.get("/")
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()


# GET SINGLE INVOICE
@router.get("/{id}")
def get_invoice(id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice


# CREATE INVOICE
@router.post("/")
def create_invoice(data: dict, db: Session = Depends(get_db)):
    new_invoice = Invoice(
        client=data.get("client"),
        amount=data.get("amount"),
        status=data.get("status", "Pending"),
        date=data.get("date")
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


# DELETE INVOICE
@router.delete("/{id}")
def delete_invoice(id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()

    return {"message": "Invoice deleted"}


# UPDATE INVOICE (EDIT)
@router.put("/{id}")
def update_invoice(id: int, data: dict, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.client = data.get("client", invoice.client)
    invoice.amount = data.get("amount", invoice.amount)
    invoice.status = data.get("status", invoice.status)
    invoice.date = data.get("date", invoice.date)

    db.commit()
    db.refresh(invoice)

    return invoice