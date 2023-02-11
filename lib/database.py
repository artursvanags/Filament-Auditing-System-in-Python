import sqlite3
name = "database"

def get_database_connection():
    return sqlite3.connect(name + ".db")

def init_database():
    conn = get_database_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS filament (
                token text PRIMARY KEY,
                manufacturer text,
                material text,
                stock_weight real,
                leftover_weight real,
                color text,
                state text,
                date_added datetime DEFAULT (datetime('now', 'localtime')),
                date_last_used datetime
                )""")
    

    c.execute("""CREATE TABLE IF NOT EXISTS printers (
                id integer PRIMARY KEY,
                name text,
                last_used_filament text,
                date_added datetime DEFAULT (datetime('now', 'localtime'))
                )""")

    conn.commit()
    conn.close()