import json
from caliber_and_types import available_data_types

def find_ammo_position(data, id):
    return next(
        ([caliber, index] for caliber, ammos in data.items() 
         for index, ammo in enumerate(ammos) if ammo['id'] == id),
        None
    )

live_data: list = []
ammo_file = "data/ammo.js"
data_file = "data/data.js"
input_file = "data/spt_data.json" # spt_data.json or live_data.json
processed_data = {}
try:
    with open(input_file, "r", encoding="UTF-8") as file:
        processed_data = json.load(file)
except OSError:
    print("Data file could not be read.")
    exit()

try:
    with open(ammo_file, "r", encoding="UTF-8") as file:
        current_id = None
        current_ammo_pos = None
        for line in file:
            line = line.strip()
            if "serverItem" in line and (line.startswith("if") and "._id" in line or line.startswith("serverItem")):
                if line.startswith("if"):
                    # Calculate the Damage
                    if current_ammo_pos:
                        processed_data[current_ammo_pos[0]][current_ammo_pos[1]]["Damage"] = int(processed_data[current_ammo_pos[0]][current_ammo_pos[1]]["Damage"]) * int(processed_data[current_ammo_pos[0]][current_ammo_pos[1]]["ProjectileCount"])
                    current_id = line.split('"')[1]
                    current_ammo_pos = find_ammo_position(processed_data, current_id)
                    continue
                line = line.removeprefix("serverItem._props.")
                name, *dummy, value = line.split()
                value = value.rstrip(';')
                if name in available_data_types and value[0].isnumeric() and current_ammo_pos:
                    processed_data[current_ammo_pos[0]][current_ammo_pos[1]][name] = value

except OSError:
    print("Ammo.js could not be read")
    exit()


with open(data_file, "w", encoding="UTF-8") as file:
    file.write("const data = ")
    # Sort the calibers by name. Makes the webside easier to use.
    json.dump({caliber: processed_data[caliber] for caliber in sorted(processed_data.keys())}, file, indent=4)
    file.write(";")
