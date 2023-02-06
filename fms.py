import random
import sqlite3
import hashlib

database_name = "database"


def init_database():
    global database_name
    conn = sqlite3.connect(database_name + ".db")
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

def add_filament():
    global database_name
    conn = sqlite3.connect(database_name + ".db")
    c = conn.cursor()

    manufacturer = input("Enter filament manufacturer: ")
    material = input("Enter filament material: ")
    weight = float(input("Enter filament weight: "))
    color = input("Enter filament color: ")
    token = hashlib.sha224(
        str(random.getrandbits(256)).encode('utf-8')).hexdigest()[0:6]

    c.execute("INSERT INTO filament (token, manufacturer, material, stock_weight, leftover_weight, color, state, date_added, date_last_used) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
              (token, manufacturer, material, weight, weight, color, "new"))
    conn.commit()
    print(f"Filament added with token: {token}")

def use_filament():
    global database_name
    conn = sqlite3.connect(database_name + ".db")
    c = conn.cursor()

    c.execute("SELECT * FROM filament WHERE state != 'archived'")
    filaments = c.fetchall()
    if not filaments:
        print("There are no available filament rolls.")
        add_filament()
        c.execute("SELECT * FROM filament")
        filaments = c.fetchall()

    while True:
        print("Filament Options:")
        print("(L)ast 5 added filaments")
        print("(S)earch by token")
        option = input("Enter your choice: ").upper()
        if option == "L":
            c.execute("SELECT * FROM filament WHERE state != 'archived' ORDER BY date_added DESC LIMIT 5")
            filaments = c.fetchall()
            for i, filament in enumerate(filaments):
                print(f"{i + 1}. Token: {filament[0]} | Manufacturer: {filament[1]} | Material: {filament[2]} | Stock Weight: {filament[3]} | Leftover Weight: {filament[4]} | Color: {filament[5]}")
            selected_filament = int(input("Enter the number of the filament you want to use: "))
            selected_filament = filaments[selected_filament - 1]
            break
        elif option == "S":
            token = input("Enter filament token (or part of it) to search: ")
            c.execute("SELECT * FROM filament WHERE token LIKE ? AND state != 'archived' ORDER BY date_added DESC", (f"%{token}%",))
            filaments = c.fetchall()
            if not filaments:
                print("No filaments found.")
                continue
            for i, filament in enumerate(filaments):
                print(f"{i + 1}. Token: {filament[0]} | Manufacturer: {filament[1]} | Material: {filament[2]} | Stock Weight: {filament[3]} | Leftover Weight: {filament[4]} | Color: {filament[5]}")
            selected_filament = int(input("Enter the number of the filament you want to use: "))
            selected_filament = filaments[selected_filament - 1]
            break
        else:
            print("Invalid option. Try again.")

    c.execute("SELECT * FROM printers")
    printers = c.fetchall()
    if not printers:
        print("There are no available printers.")
        add_printer()
        c.execute("SELECT * FROM printers")
        printers = c.fetchall()

    print("Printers:")
    for i, printer in enumerate(printers):
        print(f"{i + 1}. Name: {printer[1]}")
    selected_printer = int(input("Enter the number of the printer you want to use: "))
    selected_printer = printers[selected_printer - 1]

    filename = input("Enter file name: ")
    weight = float(input("Enter filament weight used: "))
    if weight > selected_filament[4]:
        c.execute("UPDATE filament SET leftover_weight=0, state='archived' WHERE token=?", (selected_filament[0],))
    else:
        c.execute("UPDATE filament SET leftover_weight=leftover_weight-?, date_last_used=datetime('now'), state='used' WHERE token=?", (weight, filament[0]))
    c.execute("UPDATE printers SET last_used_filament=? WHERE id=?", (selected_filament[0], selected_printer[0]))
    
    conn.commit()
    conn.close()

def menu():
    while True:
        print("Filament Management System")
        print("1. Add filament roll")
        print("2. Use filament roll")
        print("3. Exit")
        choice = int(input("Enter your choice (1-3): "))

        if choice == 1:
            add_filament()
        elif choice == 2:
            use_filament()
        elif choice == 3:
            break
        else:
            print("Invalid choice.")

init_database()
if init_database:
    menu()
else:
    print("Tables could not be created.")