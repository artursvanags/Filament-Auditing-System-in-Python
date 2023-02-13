import threading

from lib.database   import init_database, get_database_connection
from lib.scanner    import scan_qr_code
from lib.modules   import add_filament, use_filament

def menu():

    while True:
        print("Filament Management System")
        print("1. Add filament roll")
        print("2. Use filament roll")
        print("3. Exit")
        choice = int(input("Scan the QR code or Enter your choice (1-3): "))
        if choice == 1:
            add_filament()
        elif choice == 2:
            use_filament()
        elif choice == 3:
            break
        else:
            print("Invalid choice.")

def filament_data(token):
    conn = get_database_connection()
    c = conn.cursor()
    # Fetch data for the given token
    c.execute("SELECT * FROM filament WHERE token=?", (token,))
    filament_data = c.fetchone()

    # Print information about the filament
    if token in filament_data:
        print(f"State: {filament_data[6]}")
        print(f"Data Added: {filament_data[8]} | Last Used: {filament_data[9]}")
        print(f"Token: {filament_data[0]} | Manufacturer: {filament_data[1]} | Material: {filament_data[2]} | Stock Weight: {filament_data[3]}g | Leftover Weight: {filament_data[4]}g | Color: {filament_data[5]}")
    else:
        print("Invalid QR code token")

    # Close the database connection
    conn.close()


if __name__ == '__main__':
    # Create the database
    init_database()

    #Start the scanner in a separate thread
    # scanner_thread = threading.Thread(target=scan_qr_code, args=(filament_data,))
    # scanner_thread.start()

    # Run the menu
    menu()