import sqlite3

def add_printer():
    global database_name
    conn = sqlite3.connect(database_name + ".db")
    c = conn.cursor()

    name = input("Enter printer name: ")

    # Check if printer already exists
    c.execute("SELECT * FROM printers WHERE name=?", (name,))
    existing_printer = c.fetchone()

    # If printer exists, inform the user
    if existing_printer:
        print(f"Printer '{name}' already exists.")
    # If printer does not exist, insert a new printer
    else:
        c.execute(
            "INSERT INTO printers (name, date_added) VALUES (?, datetime('now', 'localtime'))", (name,))
        print(f"Printer '{name}' added.")

    conn.commit()
    conn.close()