import sqlite3

DB_NAME = "faktura.db"

def show_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("\n📌 TABLES IN DATABASE:")
    for t in tables:
        print("-", t[0])

    conn.close()


def show_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()

        print("\n👤 USERS TABLE:")
        if not users:
            print("❌ No users found in database!")
        else:
            for u in users:
                print(u)

    except Exception as e:
        print("❌ Error:", e)

    conn.close()


if __name__ == "__main__":
    show_tables()
    show_users()