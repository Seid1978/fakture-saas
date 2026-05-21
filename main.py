from fastapi import FastAPI, File, UploadFile
import os
import sqlite3

from pdf_parser import extract_text_from_pdf
from database import init_db, save_invoice
from ai_parser import extract_data

app = FastAPI()

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# INIT DB
init_db()


# -------------------------
# ROOT
# -------------------------
@app.get("/")
def root():
    return {"message": "API radi 🚀"}


# -------------------------
# UPLOAD + AI PARSING
# -------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)
    data = extract_data(text)

    save_invoice(
        file.filename,
        text,
        data.get("datum"),
        data.get("cijena"),
        data.get("klijent")
    )

    return {
        "filename": file.filename,
        "status": "saved",
        "data": data
    }


# -------------------------
# SVE FAKTURE
# -------------------------
@app.get("/fakture")
def get_fakture():
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, content, datum, cijena, klijent
        FROM fakture
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return {
        "total": len(rows),
        "fakture": [
            {
                "id": r[0],
                "filename": r[1],
                "datum": r[3],
                "cijena": r[4],
                "klijent": r[5],
                "preview": r[2][:120] if r[2] else ""
            }
            for r in rows
        ]
    }


# -------------------------
# SEARCH
# -------------------------
@app.get("/fakture/search")
def search_fakture(query: str):
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, content, datum, cijena, klijent
        FROM fakture
        WHERE content LIKE ?
        ORDER BY id DESC
    """, (f"%{query}%",))

    rows = cursor.fetchall()
    conn.close()

    return {
        "query": query,
        "results": [
            {
                "id": r[0],
                "filename": r[1],
                "datum": r[3],
                "cijena": r[4],
                "klijent": r[5]
            }
            for r in rows
        ]
    }


# -------------------------
# FILTER PO KLIJENTU
# -------------------------
@app.get("/fakture/filter")
def filter_fakture(klijent: str):
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, content, datum, cijena, klijent
        FROM fakture
        WHERE klijent LIKE ?
        ORDER BY id DESC
    """, (f"%{klijent}%",))

    rows = cursor.fetchall()
    conn.close()

    return {
        "klijent": klijent,
        "total": len(rows),
        "fakture": [
            {
                "id": r[0],
                "filename": r[1],
                "datum": r[3],
                "cijena": r[4],
                "klijent": r[5]
            }
            for r in rows
        ]
    }


# -------------------------
# TOTAL ZARADA
# -------------------------
@app.get("/fakture/total")
def total_zarada():
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("SELECT cijena FROM fakture")
    rows = cursor.fetchall()
    conn.close()

    total = 0.0

    for r in rows:
        try:
            if r[0]:
                total += float(r[0])
        except:
            pass

    return {
        "total_zarada": total,
        "broj_faktura": len(rows)
    }


# -------------------------
# DETAIL FAKTURE
# -------------------------
@app.get("/fakture/{faktura_id}")
def get_faktura(faktura_id: int):
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, content, datum, cijena, klijent
        FROM fakture
        WHERE id = ?
    """, (faktura_id,))

    r = cursor.fetchone()
    conn.close()

    if not r:
        return {"error": "Not found"}

    return {
        "id": r[0],
        "filename": r[1],
        "datum": r[3],
        "cijena": r[4],
        "klijent": r[5],
        "content": r[2]
    }


# -------------------------
# KLIJENT ANALYTICS (TOTAL + COUNT)
# -------------------------
@app.get("/fakture/klijenti/analytics")
def klijent_analytics():
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT klijent,
               SUM(CAST(cijena AS REAL)),
               COUNT(*)
        FROM fakture
        GROUP BY klijent
    """)

    rows = cursor.fetchall()
    conn.close()

    return {
        "data": [
            {
                "klijent": r[0],
                "total": r[1] if r[1] else 0,
                "broj_faktura": r[2]
            }
            for r in rows
        ]
    }


# -------------------------
# MONTHLY ANALYTICS
# -------------------------
@app.get("/fakture/analytics/monthly")
def monthly_analytics():
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT substr(datum, 1, 7) as mjesec,
               SUM(CAST(cijena AS REAL))
        FROM fakture
        GROUP BY mjesec
        ORDER BY mjesec
    """)

    rows = cursor.fetchall()
    conn.close()

    return {
        "data": [
            {
                "mjesec": r[0],
                "total": r[1] if r[1] else 0
            }
            for r in rows
        ]
    }


# -------------------------
# TOP CLIENTS (RANKING)
# -------------------------
@app.get("/fakture/analytics/top-clients")
def top_clients():
    conn = sqlite3.connect("faktura.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT klijent,
               SUM(CAST(cijena AS REAL)) as total
        FROM fakture
        GROUP BY klijent
        ORDER BY total DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return {
        "data": [
            {
                "klijent": r[0],
                "total": r[1]
            }
            for r in rows
        ]
    }