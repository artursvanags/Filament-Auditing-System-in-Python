import sqlite3
from config import database_name

def get_database_connection():
    return sqlite3.connect(database_name + ".db")

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
                serial_number PRIMARY KEY,
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
                filename text,
                weight real,
                last_used_filament text,
                last_used_printer text,
                date_added datetime DEFAULT (datetime('now', 'localtime')),
                date_last_used datetime
                )""")

    # Add a table for print history
    c.execute("""CREATE TABLE IF NOT EXISTS print_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename text,
                printer text,
                filament text,
                weight real,
                date_added datetime DEFAULT (datetime('now', 'localtime'))
                )""")
    
    conn.commit()
    conn.close()