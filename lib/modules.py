import random
import hashlib

from lib.database   import get_database_connection
from lib.qr         import generate_qr_label
from lib.printers   import add_printer

# Add a new filament roll
def add_filament():
    conn = get_database_connection()
    cursor = conn.cursor()

    # Ask user for filament details
    manufacturer = input("Enter filament manufacturer: ")
    material = input("Enter filament material: ")
    while True:
        try:
            weight = float(input("Enter filament weight in grams ( max. 2500 ): "))
            if weight > 2500:
                print("Maximum weight is 2500 grams. Please type the weight again!")
            else:
                break
        except ValueError:
            print("Please enter a number only.")
    color = input("Enter filament color: ")
    token = hashlib.sha224(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[0:6]

    # Insert filament details into database
    cursor.execute("INSERT INTO filament (token, manufacturer, material, stock_weight, leftover_weight, color, state, date_added, date_last_used) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
              (token, manufacturer, material, weight, weight, color, "new"))
    print(f"Filament added with token: {token}")

    # Generate QR label
    text = f"{manufacturer} {material}\n{weight} g\nColor: {color}"
    generate_qr_label(token, text)
    print(f"QR Label code generated in folder.")
    
    conn.commit()
    conn.close()

# Add a new printer
def add_printer():
    conn = get_database_connection()
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

# Helper functions
# A check function, that gets all filaments from database, and if there are no filaments, it calls the add_filament function
def get_filaments(cursor):
    cursor.execute("SELECT * FROM filament WHERE state != 'archived'")
    filaments = cursor.fetchall()
    if not filaments:
        print("There are no available filament rolls.")
        add_filament()
        cursor.execute("SELECT * FROM filament")
        filaments = cursor.fetchall()
    return filaments

# A check function, that gets all printers from database, and if there are no printers, it calls the add_printer function
def get_printers(cursor):
    cursor.execute("SELECT * FROM printers")
    printers = cursor.fetchall()
    if not printers:
        print("There are no printers in the database.")
        add_printer()
        cursor.execute("SELECT * FROM printers")
        printers = cursor.fetchall()
    return printers


def use_filament():
    conn = get_database_connection()
    cursor = conn.cursor()

    # Use get_filaments to check if there are any filaments in the database
    filaments = get_filaments(cursor)

    while True:
        print("Filament Options:")
        print("(L)ast 5 added filaments")
        print("(S)earch by token")
        option = input("Enter your choice: ").upper()

        if option == "L":
            cursor.execute("SELECT * FROM filament WHERE state != 'archived' ORDER BY date_added DESC LIMIT 5")
            filaments = cursor.fetchall()

            for i, filament in enumerate(filaments):
                print(f"{i + 1}. Token: {filament[0]} | Manufacturer: {filament[1]} | Material: {filament[2]} | Stock Weight: {filament[3]} | Leftover Weight: {filament[4]} | Color: {filament[5]}")
            selected_filament = int(input("Enter the number of the filament you want to use: "))
            
            # if user enters a number that is not in the list, print error message and repeat the loop
            if selected_filament > len(filaments):
                print("Invalid option. Try again.")
                continue
            
            selected_filament = filaments[selected_filament - 1]
            break

        elif option == "S":
            token = input("Enter filament token (or part of it) to search: ")
            cursor.execute("SELECT * FROM filament WHERE token LIKE ? AND state != 'archived' ORDER BY date_added DESC", (f"%{token}%",))
            filaments = cursor.fetchall()
            if not filaments:
                print("No filaments found.")
                continue
            for i, filament in enumerate(filaments):
                print(f"{i + 1}. Token: {filament[0]} | Manufacturer: {filament[1]} | Material: {filament[2]} | Stock Weight: {filament[3]} | Leftover Weight: {filament[4]} | Color: {filament[5]}")
            selected_filament = int(input("Enter the number of the filament you want to use: "))
            # if user enters a number that is not in the list, print error message and repeat the loop
            if selected_filament > len(filaments):
                print("Invalid option. Try again.")
                continue
            selected_filament = filaments[selected_filament - 1]
            break
        else:
            print("Invalid option. Try again.")
    
    # Use get_printers to check if there are any printers in the database
    printers = get_printers(cursor)

    # Print all printers and ask user to select one
    print("Printers:")
    for i, printer in enumerate(printers):
        print(f"{i + 1}. Name: {printer[1]}")
    selected_printer = int(input("Enter the number of the printer you want to use: "))
    selected_printer = printers[selected_printer - 1]

    # Ask user for filename, weight
    filename = input("Enter file name: ") 
    weight = float(input("Enter filament weight used: "))

    if weight > selected_filament[4]:
        cursor.execute("UPDATE filament SET leftover_weight=0, state='archived' WHERE token=?", (selected_filament[0],))
    else:
        cursor.execute("UPDATE filament SET leftover_weight=leftover_weight-?, date_last_used=datetime('now'), state='used' WHERE token=?", (weight, selected_filament[0]))
    cursor.execute("UPDATE printers SET last_used_filament=? WHERE id=?", (selected_filament[0], selected_printer[0]))
    
    # Print out the weight used & filament leftover weight
    print(f"Filament use registered.\nFilament weight used: {weight} g.\nLeftover weight: {selected_filament[4] - weight} g")

    conn.commit()
    conn.close()