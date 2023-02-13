import random
import hashlib

from lib.database   import get_database_connection
from lib.qr         import generate_qr_label

def add_storage_location():
    conn = get_database_connection()
    c = conn.cursor()

    name = input("Enter storage location name: ")

    id = hashlib.sha224(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[0:6]

    # Check if storage location already exists
    c.execute("SELECT * FROM storage_locations WHERE name=?", (name,))
    existing_storage_location = c.fetchone()

    # If storage location exists, inform the user
    if existing_storage_location:
        print(f"Storage location '{name}' already exists.")
    # If storage location does not exist, insert a new storage location
    else:
        c.execute("INSERT INTO storage_locations (id, name, date_added) VALUES (?, ?, datetime('now', 'localtime'))", (id, name,))
        print(f"Storage location '{name}' added.")

    conn.commit()
    conn.close()

def get_storage_locations(cursor):
    cursor.execute("SELECT * FROM storage_locations")
    storage_locations = cursor.fetchall()
    if not storage_locations:
        print("There are no storage locations.")
        add_storage_location()
        cursor.execute("SELECT * FROM storage_locations")
        storage_locations = cursor.fetchall()
    return storage_locations

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

def get_printers(cursor):
    cursor.execute("SELECT * FROM printers")
    printers = cursor.fetchall()
    if not printers:
        print("There are no printers in the database.")
        add_printer()
        cursor.execute("SELECT * FROM printers")
        printers = cursor.fetchall()
    return printers

def add_file():
    conn = get_database_connection()
    c = conn.cursor()

    name = input("Enter file name: ")

    # Check if file already exists
    c.execute("SELECT * FROM files WHERE name=?", (name,))
    existing_file = c.fetchone()

    # If file exists, inform the user
    if existing_file:
        print(f"File '{name}' already exists.")
    # If file does not exist, insert a new file
    else:
        while True:
            try:
                weight = float(input("Enter file weight in grams ( max. 2500 ): "))
                if weight > 2500:
                    print("Maximum weight is 2500 grams. Please type the weight again!")
                else:
                    break
            except ValueError:
                print("Please enter a number only.")

        c.execute(
            "INSERT INTO files (name, weight, date_added) VALUES (?, ?, datetime('now', 'localtime'))", (name, weight))
        print(f"File '{name}' added.")

    conn.commit()
    conn.close()

def get_files(cursor):
    cursor.execute("SELECT * FROM files")
    files = cursor.fetchall()
    if not files:
        print("There are no files in the database.")
        add_file()
        cursor.execute("SELECT * FROM files")
        files = cursor.fetchall()
    return files

def add_filament():
    conn = get_database_connection()
    cursor = conn.cursor()

    # Get the last added filament from the database if it exists
    cursor.execute("SELECT * FROM filament ORDER BY date_added DESC LIMIT 1")
    filament_data = cursor.fetchone()
    filament_data = {
            "token": filament_data[0],
            "manufacturer": filament_data[1],
            "material": filament_data[2],
            "weight": filament_data[3],
            "color": filament_data[5]
        }

    # Ask user for filament details, use last added filament as default if it exists
    token = hashlib.sha224(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[0:6]

    if filament_data:
        manufacturer = input("Enter filament manufacturer [{}]: ".format(filament_data['manufacturer'])) or filament_data['manufacturer']
        material = input("Enter filament material [{}]: ".format(filament_data['material'])) or filament_data['material']
        while True:
            weight_input = input("Enter filament weight in grams ( max. 2500 ) [{}]: ".format(filament_data['weight']))
            if weight_input:
                try:
                    weight = float(weight_input)
                    if weight > 2500:
                        print("Maximum weight is 2500 grams. Please type the weight again!")
                    else:
                        break
                except ValueError:
                    print("Please enter a number only.")
            else:
                weight = filament_data['weight']
                break
        color = input("Enter filament color [{}]: ".format(filament_data['color'])) or filament_data['color']
    else:
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
    
    # Get all storage locations from the database     
    storage_locations = get_storage_locations(cursor)
    
    # List all storage locations and ask user to select one
    print("Storage locations:")
    for i, storage_location in enumerate(storage_locations):
        print(f"{i + 1}. Name: {storage_location[1]}")

    while True:
        try:
            selected_storage_location = int(input("Enter the number of the storage location you want to use: "))
            # if user enters a number outside list of provided input, print error message and repeat the loop
            if selected_storage_location > len(storage_location) or selected_storage_location <= 0:
                print("Invalid option. Try again.")
                continue
        except ValueError:
            print("Invalid input. Enter a number.")
            continue
        break

    selected_storage_location = storage_locations[selected_storage_location - 1]

    # Insert filament details into database
    cursor.execute("INSERT INTO filament (token, manufacturer, material, stock_weight, leftover_weight, color, state, storage_location, date_added, date_last_used) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
              (token, manufacturer, material, weight, weight, color, "new", selected_storage_location[0]))
    
    # Update storage location with new filament
    
    cursor.execute("SELECT all_filaments FROM storage_locations WHERE id=?", (selected_storage_location[0],))
    all_filaments = cursor.fetchone()[0]
    if all_filaments is None:
        all_filaments = token
    else:
        all_filaments = f"{all_filaments},{token}"

    cursor.execute("UPDATE storage_locations SET all_filaments=?, last_added_filament=?, date_added=datetime('now') WHERE id=?", (all_filaments, token, selected_storage_location[0]))

    print(f"Filament added with token: {token}, in storage location: {selected_storage_location[1]}")

    # Generate QR label
    text = f"{manufacturer} {material}\n{weight} g\nColor: {color}"
    generate_qr_label(token, text)
    print(f"QR Label code generated in folder.")
    
    conn.commit()
    conn.close()

def get_filaments(cursor):
    cursor.execute("SELECT * FROM filament WHERE state != 'archived'")
    filaments = cursor.fetchall()
    if not filaments:
        print("There are no available filament rolls.")
        add_filament()
        cursor.execute("SELECT * FROM filament")
        filaments = cursor.fetchall()
    return filaments

def use_filament():
    conn = get_database_connection()
    cursor = conn.cursor()

    # 1. Use get_filaments to check if there are any filaments in the database
    filaments = get_filaments(cursor)
    

    # 2. List filaments based on the user's choice
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
            
            try:
                selected_filament = int(input("Enter the number of the filament you want to use: "))

                # if user enters a number outside list of filaments, print error message and repeat the loop
                if selected_filament > len(filaments) or selected_filament <= 0:
                    print("Invalid option. Try again.")
                    continue
            except ValueError:
                print("Invalid input. Enter a number.")
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
            
            try:
                selected_filament = int(input("Enter the number of the filament you want to use: "))

                # if user enters a number outside list of filaments, print error message and repeat the loop
                if selected_filament > len(filaments) or selected_filament <= 0:
                    print("Invalid option. Try again.")
                    continue
            except ValueError:
                print("Invalid input. Enter a number.")
                continue

            selected_filament = filaments[selected_filament - 1]
            break
        else:
            print("Invalid option. Try again.")
    
    # 3. Use get_printers to check if there are any printers in the database
    printers = get_printers(cursor)

    # 4. List all printers and ask user to select one
    print("Printers:")
    for i, printer in enumerate(printers):
        print(f"{i + 1}. Name: {printer[1]}")
    
        try:
            selected_printer = int(input("Enter the number of the printer you want to use: "))
            # if user enters a number outside list of provided input, print error message and repeat the loop
            if selected_printer> len(printers) or selected_printer <= 0:
                print("Invalid option. Try again.")
                continue
        except ValueError:
            print("Invalid 3input. Enter a number.")
            continue

    selected_printer = printers[selected_printer - 1]

    # 5. Ask user to input filename
    filename = input("Enter file name: ") 
    # 6. Ask user for print weight
    weight = float(input("Enter filament weight used: "))
    
    # 7. Update the selected filament row in the database with the new leftover weight
    if weight >= selected_filament[4]:
        # If the weight used is greater than the leftover weight, set leftover weight to 0 and archive the filament
        cursor.execute("UPDATE filament SET leftover_weight=0, date_last_used=datetime('now'), state='archived' WHERE token=?", (selected_filament[0],))    
        cursor.execute("SELECT all_filaments FROM storage_locations")
        all_filaments = cursor.fetchone()[0]
        all_filaments.remove(selected_filament[0])
        cursor.execute("UPDATE storage_locations SET all_filaments=?", (all_filaments,))
    
    else:
        cursor.execute("UPDATE filament SET leftover_weight=leftover_weight-?, date_last_used=datetime('now'), state='used' WHERE token=?", (weight, selected_filament[0]))
    # Locate the filament token from all_filaments column in storage_locations table, remove it from the list but retain the rest of the filaments that are separated by commas
    cursor.execute("SELECT all_filaments FROM storage_locations WHERE id=?", (selected_filament[6],))
    all_filaments = cursor.fetchone()[0]
    all_filaments.remove(selected_filament[0])
    cursor.execute("UPDATE storage_locations SET all_filaments=? WHERE id=?", (all_filaments, selected_filament[6]))

    #cursor.execute("UPDATE printers SET last_used_filament=?, date_last_used=datetime('now') WHERE id=?", (selected_filament[0], selected_printer[0]))
    #cursor.execute("INSERT INTO files (name, printer, filament, weight) VALUES (?, ?, ?, ?)", (filename, selected_printer[1], selected_filament[0], weight))
    
    #Print out the weight used & filament leftover weight
    print(f"Filament use registered.\nFilament weight used: {weight} g.\nLeftover weight: {selected_filament[4] - weight} g")

    conn.commit()
    conn.close()