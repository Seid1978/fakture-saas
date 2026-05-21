import sqlite3

DB_NAME = "faktura.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fakture (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            content TEXT,
            datum TEXT,
            cijena TEXT,
            klijent TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_invoice(filename, content, datum=None, cijena=None, klijent=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO fakture (filename, content, datum, cijena, klijent)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, content, datum, cijena, klijent))

    conn.commit()
    conn.close()