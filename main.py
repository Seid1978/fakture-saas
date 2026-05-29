from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
from database import engine, Base, get_db

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

from pydantic import BaseModel

# --------------------
# APP
# --------------------
app = FastAPI()

# --------------------
# CORS (frontend access)
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # u production stavi frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# DB INIT
# --------------------
Base.metadata.create_all(bind=engine)

# --------------------
# ROOT ROUTE
# --------------------
@app.get("/")
def root():
    return {"message": "Fakture SaaS API is running 🚀"}

# --------------------
# SCHEMAS
# --------------------
class RegisterSchema(BaseModel):
    email: str
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str

class TokenSchema(BaseModel):
    access_token: str

class InvoiceCreate(BaseModel):
    client: str
    amount: int
    status: str = "pending"

class InvoiceOut(BaseModel):
    id: int
    client: str
    amount: int
    status: str

    class Config:
        from_attributes = True

# --------------------
# REGISTER
# --------------------
@app.post("/register")
def register(user: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = models.User(
        email=user.email,
        password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}

# --------------------
# LOGIN
# --------------------
@app.post("/login", response_model=TokenSchema)
def login(user: LoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})

    return {"access_token": token}

# --------------------
# GET INVOICES
# --------------------
@app.get("/invoices", response_model=List[InvoiceOut])
def get_invoices(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(models.Invoice).filter(
        models.Invoice.owner_id == user.id
    ).all()

# --------------------
# CREATE INVOICE
# --------------------
@app.post("/invoices", response_model=InvoiceOut)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    new_invoice = models.Invoice(
        client=invoice.client,
        amount=invoice.amount,
        status=invoice.status,
        owner_id=user.id
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice

# --------------------
# UPDATE INVOICE
# --------------------
@app.put("/invoices/{invoice_id}", response_model=InvoiceOut)
def update_invoice(
    invoice_id: int,
    updated: InvoiceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    invoice = db.query(models.Invoice).filter(
        models.Invoice.id == invoice_id,
        models.Invoice.owner_id == user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.client = updated.client
    invoice.amount = updated.amount
    invoice.status = updated.status

    db.commit()
    db.refresh(invoice)

    return invoice

# --------------------
# DELETE INVOICE
# --------------------
@app.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    invoice = db.query(models.Invoice).filter(
        models.Invoice.id == invoice_id,
        models.Invoice.owner_id == user.id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()

    return {"message": "Deleted successfully"}