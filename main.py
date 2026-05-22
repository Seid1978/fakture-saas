from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# ---------------------------
# CORS (React frontend access)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "faktura.db"

# ---------------------------
# DB CONNECTION
# ---------------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    return conn

# ---------------------------
# INIT DB (SAFE FOR RENDER)
# ---------------------------
def init_db():
    conn = get_db()
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

    total = sum(item["quantity"] * item["price"] for item in items)

    conn = get_db()
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
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT invoice_no, client, total
            FROM invoices
            ORDER BY invoice_no DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return {
            "count": len(rows),
            "invoices": [
                {
                    "invoice_no": row["invoice_no"],
                    "client": row["client"],
                    "total": row["total"]
                }
                for row in rows
            ]
        }

    except Exception as e:
        return {
            "error": str(e)
        }

# ---------------------------
# SIMPLE PDF (HTML VIEW)
# ---------------------------
@app.get("/invoice/pdf/{invoice_id}")
def get_invoice_pdf(invoice_id: int):
    conn = get_db()
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
        <body style="font-family: Arial; padding: 20px;">
            <h1>FAKTURA</h1>
            <p><b>Invoice No:</b> {row[0]}</p>
            <p><b>Client:</b> {row[1]}</p>
            <p><b>Total:</b> {row[2]}</p>
        </body>
    </html>
    """