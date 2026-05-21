import sqlite3

def save_faktura(klijent, cijena, datum):
    conn = sqlite3.connect("fakture.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO fakture (klijent, cijena, datum)
        VALUES (?, ?, ?)
    """, (klijent, cijena, datum))

    conn.commit()
    conn.close()