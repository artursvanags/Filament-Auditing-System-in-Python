import sqlite3
name = "database"

def get_database_connection():
    return sqlite3.connect(name + ".db")

def init_database():
    conn = get_database_connection()
    c = conn.cursor()

    # Add a table for filament rolls
    c.execute("""CREATE TABLE IF NOT EXISTS filament (
                token text PRIMARY KEY,
                manufacturer text,
                material text,
                stock_weight real,
                leftover_weight real,
                color text,
                state text,
                storage_location text,
                date_added datetime DEFAULT (datetime('now', 'localtime')),
                date_last_used datetime
                )""")

    # Add a table for printers 
    c.execute("""CREATE TABLE IF NOT EXISTS printers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name text,
                last_used_filament text,
                date_added datetime DEFAULT (datetime('now', 'localtime')),
                date_last_used datetime
                )""")
    
    # Add a table for storage locations
    c.execute("""CREATE TABLE IF NOT EXISTS storage_locations (
                id text PRIMARY KEY,
                name text,
                last_added_filament text,
                all_filaments text,
                date_added datetime DEFAULT (datetime('now', 'localtime'))
                )""")

    # Add a table for files
    c.execute("""CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name text,
                weight real,
                last_used_filament text,
                last_used_printer text,
                date_added datetime DEFAULT (datetime('now', 'localtime')),
                date_last_used datetime
                )""")

    print ("Database initialized.")

    conn.commit()
    conn.close()