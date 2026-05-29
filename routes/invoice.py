from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.invoice import Invoice

router = APIRouter()

@router.post("/invoices")
def create_invoice(client: str, amount: float, db: Session = Depends(get_db)):
    new_invoice = Invoice(client=client, amount=amount)
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice

@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()