import json
import os
from caliber_and_types import available_data_types, caliber_map, blacklisted_ammo
# In line 70 is a line which will output all the available calibers which are not in the caliber_map

# Files are located in \SPT_Data\Server\database\templates\ and \SPT_Data\Server\database\locales\global
items_file = "data/items.json"
language_file = "data/en.json"
output_file = "data/spt_data.json"
items_backport_file = "data/items_backport.json"
language_backport_file = "data/locale.json"

with_backport = os.path.isfile(items_backport_file) and os.path.isfile(language_backport_file)

data = {}

try:
    with open(items_file, mode="r", encoding="UTF-8") as file:
        data = json.load(file)
except OSError:
    print("items.json could not be opened")
    exit()

if with_backport:
    try:
        with open(items_backport_file, mode="r", encoding="UTF-8") as file:
            data.update(json.load(file))
    except OSError:
        print("items_backport.json could not be opened")
        exit()

data = {key: value for key, value in data.items() if value.get("_name", "MISSING VALUE").startswith("patron_") and value.get("_id", "MISSING VALUE") not in blacklisted_ammo}


caliber = set()
for ammo in data:
    caliber.add(data[ammo]["_props"]["Caliber"])

language = {}
try:
    with open(language_file, mode="r", encoding="UTF-8") as file:
        language = json.load(file)
except OSError:
    print("language file could not be opend")
    exit()
if with_backport:
    try:
        with open(language_backport_file, mode="r", encoding="UTF-8") as file:
            language.update(json.load(file)["en"])
    except OSError:
        print("language file could not be opend")
        exit()

# Transform the Data to the needed format
for ammo_id in data:
    for prop in data[ammo_id].get("_props", {}):
        if prop in available_data_types:
            data[ammo_id][prop] = data[ammo_id]["_props"][prop]
    del data[ammo_id]["_props"]
    del data[ammo_id]["_name"]
    del data[ammo_id]["_id"]
    del data[ammo_id]["_parent"]
    del data[ammo_id]["_type"]
    if data[ammo_id].get("_proto", False):
        del data[ammo_id]["_proto"]

    data[ammo_id]["Name"] = language[ammo_id + " Name"]

# Print every Caliber not in caliber_map (good for updating the map)
print("\nCalibers not in caliber_map (Missing/Blacklisted):", *{key for key in caliber if key not in caliber_map}, sep="\n", end="\n\n")


output_dict = {}
for ammo_id in data:
    if data[ammo_id]["Caliber"] not in caliber_map:
        continue
    if caliber_map[data[ammo_id]["Caliber"]] not in output_dict:
        output_dict[caliber_map[data[ammo_id]["Caliber"]]] = []
    data[ammo_id]["Name"] = data[ammo_id]["Name"].removeprefix(caliber_map[data[ammo_id]["Caliber"]]).strip()
    data[ammo_id]["Name"] = data[ammo_id]["Name"][0].upper() + data[ammo_id]["Name"][1:]
    data[ammo_id]["id"] = ammo_id
    output_dict[caliber_map[data[ammo_id]["Caliber"]]].append(data[ammo_id])
    del output_dict[caliber_map[data[ammo_id]["Caliber"]]][-1]["Caliber"]

try:
    with open(output_file, mode="w", encoding="UTF-8") as file:
        json.dump(output_dict, file, indent=4)
except OSError:
    print("Could not write the output file")
