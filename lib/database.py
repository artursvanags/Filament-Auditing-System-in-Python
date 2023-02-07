import sqlite3

def init_database_connection(name):
    conn = sqlite3.connect(name + ".db")
    c = conn.cursor()
    return c, conn

def init_database(name):

    conn = sqlite3.connect(name + ".db")
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