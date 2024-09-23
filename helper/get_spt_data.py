import json

# File is located in \SPT_Data\Server\database\templates\
items_file = "data/items.json"
language_file = "data/en.json"
output_file = "data/spt_data.json"

# Removed the following calibers
# 40x36 (underbarrel)
# 30x29 (underbarrel)
# 127x108 (HMG)
# 20x1 (Toy Gun)
# In line 80 is a line which will output all the available calibers which are not in the caliber_map
caliber_map = {
    "Caliber556x45NATO": "5.56x45mm",
    "Caliber12g": "12/70",
    "Caliber762x54R": "7.62x54mm R",
    "Caliber762x39": "7.62x39mm",
    "Caliber9x19PARA": "9x19mm",
    "Caliber545x39": "5.45x39mm",
    "Caliber762x25TT": "7.62x25mm TT",
    "Caliber9x18PM": "9x18mm PM",
    "Caliber9x39": "9x39mm",
    "Caliber762x51": "7.62x51mm",
    "Caliber366TKM": ".366 TKM",
    "Caliber9x21": "9x21mm",
    "Caliber20g": "20/70",
    "Caliber46x30": "4.6x30mm",
    "Caliber127x55": "12.7x55mm",
    "Caliber57x28": "5.7x28mm",
    "Caliber1143x23ACP": ".45 ACP",
    "Caliber23x75": "23x75mm",
    "Caliber762x35": ".300",
    "Caliber86x70": ".338 Lapua Magnum",
    "Caliber9x33R": ".357 Magnum",
    "Caliber26x75": "26x75mm",
    "Caliber68x51": "6.8x51mm"
}

try:
    with open(items_file, mode="r", encoding="UTF-8") as file:
        data = json.load(file)
except OSError:
    print("items.json could not be opened")
    exit()
caliber = set()
data = {key: value for key, value in data.items() if value.get("_name", "MISSING VALUE").startswith("patron_")}
for ammo in data:
    caliber.add(data[ammo]["_props"]["Caliber"])

# Move props down to make handling easier
available_data_types = ["PenetrationPower", "DurabilityBurnModificator", "Damage", "Weight", "ArmorDamage", "ProjectileCount",
                        "InitialSpeed", "BallisticCoeficient", "RicochetChance", "FragmentationChance", "BulletMassGram",
                        "HeavyBleedingDelta", "LightBleedingDelta", "MalfFeedChance", "MalfMisfireChance", "HeatFactor",
                        "AmmoAccr", "AmmoHear", "AmmoRec", "Name", "Caliber"]

try:
    with open(language_file, mode="r", encoding="UTF-8") as file:
        language = json.load(file)
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
# print(*{key for key in caliber if key not in caliber_map})


output_dict = {}
for ammo_id in data:
    if data[ammo_id]["Caliber"] not in caliber_map:
        continue
    if caliber_map[data[ammo_id]["Caliber"]] not in output_dict:
        output_dict[caliber_map[data[ammo_id]["Caliber"]]] = []
    output_dict[caliber_map[data[ammo_id]["Caliber"]]].append(data[ammo_id])
    del output_dict[caliber_map[data[ammo_id]["Caliber"]]][-1]["Caliber"]

try:
    with open(output_file, mode="w", encoding="UTF-8") as file:
        json.dump(output_dict, file, indent=4)
except OSError:
    print("Could not write the output file")
