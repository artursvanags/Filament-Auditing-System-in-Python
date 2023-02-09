import sqlite3
name = "database"
def init_database_connection():
    conn = sqlite3.connect(name + ".db")
    c = conn.cursor()
    return c, conn

def init_database():
    c, conn = init_database_connection()

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