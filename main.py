from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# ---------------------------
# CORS (React access)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# INIT DATABASE (IMPORTANT FOR RENDER)
# ---------------------------
def init_db():
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no INTEGER,
            client TEXT,
            total REAL
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------------------
# CREATE INVOICE
# ---------------------------
@app.post("/invoice")
def create_invoice(data: dict):
    client = data["client"]
    items = data["items"]

    total = 0
    for item in items:
        total += item["quantity"] * item["price"]

    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO invoices (client, total) VALUES (?, ?)",
        (client, total)
    )

    invoice_no = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "status": "created",
        "invoice_no": invoice_no,
        "client": client,
        "total": total
    }

# ---------------------------
# GET ALL INVOICES (DASHBOARD)
# ---------------------------
@app.get("/invoices")
def get_invoices():
    try:
        conn = sqlite3.connect("faktura.db")
        cursor = conn.cursor()

        cursor.execute("SELECT invoice_no, client, total FROM invoices")
        rows = cursor.fetchall()

        conn.close()

        return {
            "count": len(rows),
            "invoices": [
                {
                    "invoice_no": r[0],
                    "client": r[1],
                    "total": r[2]
                }
                for r in rows
            ]
        }

    except Exception as e:
        return {"error": str(e)}

# ---------------------------
# SIMPLE PDF (HTML OUTPUT)
# ---------------------------
@app.get("/invoice/pdf/{invoice_id}")
def get_invoice_pdf(invoice_id: int):
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT invoice_no, client, total FROM invoices WHERE invoice_no=?",
        (invoice_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "Invoice not found"}

    return f"""
    <html>
        <body style="font-family:Arial;">
            <h1>FAKTURA</h1>
            <p><b>Invoice No:</b> {row[0]}</p>
            <p><b>Client:</b> {row[1]}</p>
            <p><b>Total:</b> {row[2]}</p>
        </body>
    </html>
    """