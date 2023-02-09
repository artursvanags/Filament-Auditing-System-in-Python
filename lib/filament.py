import random
import hashlib


from lib.qr import generate_qr_label
from lib.database import init_database_connection
from lib.printers import add_printer

def add_filament():
    c, conn = init_database_connection()

    # Ask user for filament details
    manufacturer = input("Enter filament manufacturer: ")
    material = input("Enter filament material: ")
    while True:
        try:
            weight = float(input("Enter filament weight in grams ( max. 2500 ): "))
            if weight > 2500:
                print("Maximum weight is 2500 grams.")
            else:
                break
        except ValueError:
            print("Please enter a number.")
    color = input("Enter filament color: ")
    token = hashlib.sha224(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[0:6]

    # Insert filament details into database
    c.execute("INSERT INTO filament (token, manufacturer, material, stock_weight, leftover_weight, color, state, date_added, date_last_used) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
              (token, manufacturer, material, weight, weight, color, "new"))
    conn.commit()

    # Print filament token
    print(f"Filament added with token: {token}")

    # Generate QR label
    text = f"{manufacturer} {material}\n{weight} g\nColor: {color}"
    generate_qr_label(token, text)

    print(f"QR Label code generated in folder.")


def use_filament():
    c, conn = init_database_connection()
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
        c.execute("UPDATE filament SET leftover_weight=leftover_weight-?, date_last_used=datetime('now'), state='used' WHERE token=?", (weight, selected_filament[0]))
    c.execute("UPDATE printers SET last_used_filament=? WHERE id=?", (selected_filament[0], selected_printer[0]))
    
    # Print out the weight used & filament leftover weight
    print(f"Filament use registered.\nFilament weight used: {weight} g.\nLeftover weight: {selected_filament[4] - weight} g")

    conn.commit()
    conn.close()
