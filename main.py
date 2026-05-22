from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pydantic import BaseModel, Field
from typing import List

import sqlite3
import json

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# -----------------------
# APP SETUP
# -----------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# DATABASE
# -----------------------
conn = sqlite3.connect("fakture.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no INTEGER,
    client TEXT,
    total REAL,
    items TEXT
)
""")

conn.commit()

# -----------------------
# MODELS
# -----------------------
class Item(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class Invoice(BaseModel):
    client: str = Field(..., min_length=1)
    items: List[Item]

# -----------------------
# ROOT
# -----------------------
@app.get("/")
def root():
    return {"message": "Fakture API radi 🚀"}

# -----------------------
# CREATE INVOICE
# -----------------------
@app.post("/invoice")
def create_invoice(invoice: Invoice):
    total = sum(i.quantity * i.price for i in invoice.items)
    items_json = json.dumps([i.dict() for i in invoice.items])

    cursor.execute("SELECT MAX(invoice_no) FROM invoices")
    last = cursor.fetchone()[0]
    next_no = 1 if last is None else last + 1

    cursor.execute("""
        INSERT INTO invoices (invoice_no, client, total, items)
        VALUES (?, ?, ?, ?)
    """, (next_no, invoice.client, total, items_json))

    conn.commit()

    return {
        "status": "created",
        "invoice_no": next_no,
        "client": invoice.client,
        "total": total
    }

# -----------------------
# READ INVOICES
# -----------------------
@app.get("/invoices")
def get_invoices():
    cursor.execute("SELECT * FROM invoices")
    rows = cursor.fetchall()

    return {
        "count": len(rows),
        "invoices": [
            {
                "id": r[0],
                "invoice_no": r[1],
                "client": r[2],
                "total": r[3]
            }
            for r in rows
        ]
    }

# -----------------------
# UPDATE INVOICE
# -----------------------
@app.put("/invoice/{invoice_id}")
def update_invoice(invoice_id: int, invoice: Invoice):
    total = sum(i.quantity * i.price for i in invoice.items)
    items_json = json.dumps([i.dict() for i in invoice.items])

    cursor.execute("""
        UPDATE invoices
        SET client = ?, total = ?, items = ?
        WHERE id = ?
    """, (invoice.client, total, items_json, invoice_id))

    conn.commit()

    return {
        "status": "updated",
        "id": invoice_id,
        "client": invoice.client,
        "total": total
    }

# -----------------------
# DELETE INVOICE
# -----------------------
@app.delete("/invoice/{invoice_id}")
def delete_invoice(invoice_id: int):
    cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    conn.commit()

    return {"status": "deleted", "id": invoice_id}

# -----------------------
# PDF GENERATOR
# -----------------------
@app.get("/invoice/pdf/{invoice_id}")
def generate_pdf(invoice_id: int = Path(...)):
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()

    if not row:
        return {"error": "Invoice not found"}

    invoice_no = row[1]
    client = row[2]
    total = row[3]
    items = json.loads(row[4])

    file_name = f"invoice_{invoice_id}.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)

    c.drawString(100, 750, "FAKTURA")
    c.drawString(100, 730, f"Invoice No: {invoice_no}")
    c.drawString(100, 710, f"Client: {client}")

    y = 670
    c.drawString(100, y, "Items:")
    y -= 20

    for item in items:
        line = f"{item['name']} x{item['quantity']} = {item['price'] * item['quantity']}"
        c.drawString(100, y, line)
        y -= 20

    c.drawString(100, y - 20, f"TOTAL: {total}")

    c.save()

    return FileResponse(file_name, media_type="application/pdf")