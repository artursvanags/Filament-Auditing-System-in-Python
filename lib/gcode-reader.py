import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

def file_path():
    file_path = filedialog.askopenfilename(filetypes=[("GCODE files", "*.gcode")])
    return file_path

def get_filament_data_file(file):
    with open(file, 'r') as f:
        for line in f:
            if 'total filament used [g]' in line:
                filament_weight = line.split('=')[1].strip()
                return float(filament_weight)
    return None

filament_data = get_filament_data_file(file_path())

if filament_data is not None:
    print(f'Total filament used: {filament_data} g')
else:
    print('Could not find filament usage information in file.')
