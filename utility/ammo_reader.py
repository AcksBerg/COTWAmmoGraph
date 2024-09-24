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
    print("input_file could not be read: ", input_file)
    exit()


# Copy of processed_data and caliber or it will promped an error for changing size while iteration
for caliber in list(processed_data):
    for ammo in processed_data[caliber][:]:
        # Greater two to keep the Dual Sabot slug as a slug as wished by Fontaine
        if ammo["ProjectileCount"] > 2:
            if f'{caliber} shot' not in processed_data:
                processed_data[f'{caliber} shot'] = [ammo]
            else:
                processed_data[f'{caliber} shot'].append(ammo)
            processed_data[caliber].remove(ammo)


            

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
                        processed_data[current_ammo_pos[0]][current_ammo_pos[1]]["ProjectileCount"] = int(processed_data[current_ammo_pos[0]][current_ammo_pos[1]]["ProjectileCount"])
                    current_id = line.split('"')[1]
                    current_ammo_pos = find_ammo_position(processed_data, current_id)
                    continue
                line = line.removeprefix("serverItem._props.")
                name, *dummy, value = line.split()
                value = value.rstrip(';')
                if name in available_data_types and value[0].isnumeric() and current_ammo_pos:
                    processed_data[current_ammo_pos[0]][current_ammo_pos[1]][name] = value
except OSError:
    print("Ammo.js could not be read: ", ammo_file)
    exit()

# create the single shot values
for caliber in list(processed_data):
    if " shot" not in caliber:
        continue
    if f'{caliber} single' not in processed_data:
        processed_data[f'{caliber.removesuffix(" shot")} single'] = []
    for ammo in processed_data[caliber]:
        single_ammo = ammo.copy()
        single_ammo["Damage"] = single_ammo["Damage"] / single_ammo["ProjectileCount"]
        processed_data[f'{caliber.removesuffix(" shot")} single'].append(single_ammo)



try:
    with open(data_file, "w", encoding="UTF-8") as file:
        file.write("const data = ")
        # Sort the calibers by name. Makes the webside easier to use.
        json.dump({caliber: processed_data[caliber] for caliber in sorted(processed_data.keys())}, file, indent=4)
        file.write(";")
except OSError:
    print("Could not write the data.js: ", data_file)
