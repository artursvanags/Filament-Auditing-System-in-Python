import random
import hashlib

from lib.database   import get_database_connection
from lib.qr         import generate_qr_label
from lib.log        import log_changes

from config import max_weight, leftover_weight_threshold

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
    
    # Write to log
    log_changes("INFO", "add_storage_location", "Storage location added", f"Added storage location '{name}'.")

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
    # Ask for user to input serial number, if left empty, generate a random one uppercased
    serial_number = input("Enter printer serial number (leave blank to generate a random one): ").upper()
    if not serial_number:
        serial_number = hashlib.sha224(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[0:10].upper()
        print(f"Serial number: {serial_number} generated")

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
            "INSERT INTO printers (serial_number, name, date_added) VALUES (?, ?, datetime('now', 'localtime'))", (serial_number, name,))
        print(f"Printer '{name}' with serial number '{serial_number}' added.")
    
    # Write to log
    log_changes("INFO", "add_printer", "Printer added", f"Printer '{name}' with serial number '{serial_number}' added.")

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

    # Write to log
    log_changes("INFO", "add_file", "File added", f"Added file '{name}'.")

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

    token = hashlib.sha224(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[0:6]
    
    # Get the last added filament from the database if it exists
    cursor.execute("SELECT * FROM filament ORDER BY date_added DESC LIMIT 1")
    filament_data = cursor.fetchone()

    if filament_data:

        filament_data = {
        "token": filament_data[0],
        "manufacturer": filament_data[1],
        "material": filament_data[2],
        "weight": filament_data[3],
        "color": filament_data[5]
        }
        
        manufacturer = input("Enter filament manufacturer [{}]: ".format(filament_data['manufacturer'])) or filament_data['manufacturer']
        material = input("Enter filament material [{}]: ".format(filament_data['material'])) or filament_data['material']
        
        while True:
            weight_input = input(f"Enter filament weight in grams ( max. {max_weight} ) [{filament_data['weight']}]: ")
            if weight_input:
                try:
                    weight = float(weight_input)
                    if weight > max_weight:
                        print(f"Maximum weight is {max_weight} grams. Please type the weight again!")
                    else:
                        break
                except ValueError:
                    print("Please enter a number only.")
            else:
                weight = abs(filament_data['weight'])
                break
        color = input("Enter filament color [{}]: ".format(filament_data['color'])) or filament_data['color']
    else:
        # ask user for manufacturer & material details, but if they are empty, print an error message and ask again
        while True:
            try:
                manufacturer = input("Enter filament manufacturer: ")
                if not manufacturer:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a manufacturer name.")
        while True:
            try:
                material = input("Enter filament material: ")
                if not material:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a material name.")
        while True:
            try:
                weight = abs(float(input(f"Enter filament weight in grams ( max. {max_weight} ): ")))
                if weight > max_weight:
                    print(f"Maximum weight is {max_weight} grams. Please type the weight again!")
                else:
                    break
            except ValueError:
                print("Please enter a number only.")
        while True:
            try:
                color = input("Enter filament color: ")
                if not color:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a color name.")

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
    
    # Write to log
    log_changes("INFO", "add_filament", "Filament added", {"manufacturer": manufacturer, "material": material, "weight": f"{weight}", "color": color})

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
    def select_filament():
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
        return selected_filament
    selected_filament = select_filament()

    # 3. Use get_printers to check if there are any printers in the database
    printers = get_printers(cursor)

    # 4. List all printers and ask user to select one
    print("Printers:")
    for i, printer in enumerate(printers):
        print(f"{i + 1}. Name: {printer[1]}")
    
    while True:
        try:
            selected_printer = int(input("Enter the number of the storage location you want to use: "))
            # if user enters a number outside list of provided input, print error message and repeat the loop
            if selected_printer > len(printers) or selected_printer <= 0:
                print("Invalid option. Try again.")
                continue
        except ValueError:
            print("Invalid input. Enter a number.")
            continue
        break

    selected_printer = printers[selected_printer - 1]
    # ask user to prepare the printer and insert the filament
    input(f"Please prepare the '{selected_printer[1]}' and insert the '{selected_filament[0], selected_filament[1], selected_filament[2], selected_filament[5]}'. Press Enter to continue once ready!")
    # 5. Ask user to input filename & weight used

    filename = input("Enter file name: ")
    while True:
        try:
            weight = float(input("Enter filament weight used: "))
            if weight <= 0:
                print("Weight must be greater than 0.")
                continue
        except ValueError:
            print("Invalid input. Enter a number.")
            continue
        break
    
    # 6. Update database with new values

    # Create a new entry in the files table
    cursor.execute("INSERT INTO files (id, filename, weight, last_used_filament, last_used_printer, date_added, date_last_used) VALUES (NULL, ?, ?, ?, ?, datetime('now'), datetime('now'))", (filename, weight, selected_filament[0], selected_printer[0]))
    # fetch the id of the newly created entry
    cursor.execute("SELECT id FROM files WHERE filename=?", (filename,))
    file_id = cursor.fetchone()[0]

    # If the weight used is greater than the leftover weight
    leftover_weight = selected_filament[4] - weight
    
    if weight > selected_filament[4]:
        
        leftover_weight = 0
        # Set leftover weight to 0 and archive the filament
        cursor.execute("UPDATE filament SET leftover_weight=0, date_last_used=datetime('now'), state='archived' WHERE token=?", (selected_filament[0],))    
        cursor.execute("SELECT all_filaments FROM storage_locations")

        # Remove the selected filament token in all_filaments from storage_locations table and update the date_last_used
        # If the filament is the only one in the storage location, set all_filaments to NULL
        for row in cursor.fetchall():
            if row[0] == selected_filament[0]:
                cursor.execute("UPDATE storage_locations SET all_filaments=NULL WHERE all_filaments=?", (selected_filament[0],))
            else:
                cursor.execute("UPDATE storage_locations SET all_filaments=REPLACE(all_filaments, ?, '') WHERE all_filaments LIKE ?", (selected_filament[0], f"%{selected_filament[0]}%"))  
        print(f"Filament '{selected_filament[0]}' has been archived.")
    # Else update the leftover weight only, date_last_used and state to "used"
    else: 
        cursor.execute("UPDATE filament SET leftover_weight=leftover_weight-?, date_last_used=datetime('now'), state='used' WHERE token=?", (weight, selected_filament[0]))

    # Ask user to archive the filament if the leftover weight is less than 50, else continue
    if leftover_weight < leftover_weight_threshold:
        while True:
            option = input(f"{selected_filament[4]} g remaining for the selected roll.\nFilament will be almost empty after this job. Do you want to archive it? (Type 'Y' or leave empty to ignore) ")
            if option == "Y" or option == "y":
                cursor.execute("UPDATE filament SET leftover_weight=0, date_last_used=datetime('now'), state='archived' WHERE token=?", (selected_filament[0],))
                cursor.execute("SELECT all_filaments FROM storage_locations")
                # Remove the selected filament token in all_filaments from storage_locations table and update the date_last_used
                # If the filament is the only one in the storage location, set all_filaments to NULL
                for row in cursor.fetchall():
                    if row[0] == selected_filament[0]:
                        cursor.execute("UPDATE storage_locations SET all_filaments=NULL WHERE all_filaments=?", (selected_filament[0],))
                    else:
                        cursor.execute("UPDATE storage_locations SET all_filaments=REPLACE(all_filaments, ?, '') WHERE all_filaments LIKE ?", (selected_filament[0], f"%{selected_filament[0]}%"))  
                print(f"Filament '{selected_filament[0]}' has been archived.")
                break
            elif option == "":
                break
            else:
                print("Invalid option. Try again.")
                continue

    # Update the printer's last_used_filament
    cursor.execute("UPDATE printers SET last_used_filament=?, date_last_used=datetime('now') WHERE serial_number=?", (selected_filament[0], selected_printer[0]))

    # Update the print history
    cursor.execute("INSERT INTO print_history (id, file, printer, filament, weight, date_added) VALUES (NULL, ?, ?, ?, ?, datetime('now'))", (file_id, selected_printer[0], selected_filament[0], weight ))

    # 8. Print and log changes

    #Print out the weight used & filament leftover weight
    
    print(f"Weight used {weight} g. Left: {leftover_weight} g in the roll.")
    print("Changes have been saved to the database.")
    # Write all changes to the log
    log_changes("INFO", "use_filament","Filament has been used",{"Filament Token": selected_filament[0] , "Leftover weight:": f"{leftover_weight} g"})

    conn.commit()
    conn.close()

