import json

def find_ammo_position(data, id):
    return next(
        ([caliber, index] for caliber, ammos in data.items() 
         for index, ammo in enumerate(ammos) if ammo['id'] == id),
        None
    )

live_data: list = []

try:
    with open("live_data.json", "r", encoding="UTF-8") as file:
        live_data = json.load(file)["data"]["items"]
except OSError:
    print("Live data could not be read.")
    exit()

processed_data = {}

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
    "Caliber68x51": "6.8x51mm",
    "Caliber20x1mm": "20x1mm"
}

# Remove grenades and data missing properties from live data and move the properties to the main data to make the handling easier
for entry in live_data:
    if entry["name"].lower().find("grenade") != -1 or not entry.get("properties"):
        continue
    # Remove the Caliber from the name and the Blackout from the .300 Blackout (Because of the Wipser round)
    entry["Name"] = entry["name"][len(caliber_map[entry["properties"]["caliber"]])+1:].removeprefix("Blackout ")
    entry["Weight"] = entry["weight"]
    for name, value in entry["properties"].items():
        # Rename keynames to match RM names
        match name:
            case "bulletMassGrams":
                entry["BulletMassGram"] = value
            case "heavyBleedModifier":
                entry["HeavyBleedingDelta"] = value
            case "lightBleedModifier":
                entry["LightBleedingDelta"] = value
            case "durabilityBurnFactor":
                entry["DurabilityBurnModificator"] = value
            case "failureToFeedChance":
                entry["MalfFeedChance"] = value
            case "misfireChance":
                entry["MalfMisfireChance"] = value
            case _:
                entry[name[0].upper() + name[1:]] = value
    del entry["name"]
    del entry["weight"]
    del entry["properties"]
    cal = caliber_map[entry["Caliber"]]
    if entry["ProjectileCount"] > 2:
        cal += " Shot"
    del entry["Caliber"]
    # Calculate the damage
    entry["Damage"] = entry["Damage"] * entry["ProjectileCount"]
    if cal not in processed_data:
        processed_data[cal] = [entry]
        continue
    processed_data[cal].append(entry)

available_data_types = ["PenetrationPower", "DurabilityBurnModificator", "Damage", "Weight", "ArmorDamage", "ProjectileCount",
                        "InitialSpeed", "BallisticCoeficient", "RicochetChance", "FragmentationChance", "BulletMassGram",
                        "HeavyBleedingDelta", "LightBleedingDelta", "MalfFeedChance", "MalfMisfireChance", "HeatFactor",
                        "AmmoAccr", "AmmoHear", "AmmoRec"]

try:
    with open("ammo.js", "r", encoding="UTF-8") as file:
        current_id = None
        current_ammo_pos = None
        for line in file:
            line = line.strip()
            if "serverItem" in line and (line.startswith("if") and "._id" in line or line.startswith("serverItem")):
                if line.startswith("if"):
                    current_id = line.split('"')[1]
                    current_ammo_pos = find_ammo_position(processed_data, current_id)
                    continue
                line = line.removeprefix("serverItem._props.")
                name, *dummy, value = line.split()
                value = value.rstrip(';')
                if name in available_data_types and value[0].isnumeric() and current_ammo_pos:
                    processed_data[current_ammo_pos[0]][current_ammo_pos[1]][name] = value
                    pass

except OSError:
    print("Ammo.js could not be read")
    exit()


with open("data.js", "w", encoding="UTF-8") as file:
    file.write("const data = ")
    json.dump(processed_data, file, indent=4)
    file.write(";")
