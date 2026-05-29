import sqlite3

conn = sqlite3.connect("faktura.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO users (email, password)
VALUES ('test@test.com', '1234')
""")

conn.commit()
conn.close()

print("✅ users table created + test user added")