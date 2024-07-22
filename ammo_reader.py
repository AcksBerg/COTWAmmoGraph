import json

input_file = "ammo.js"
output_file = "output.json"

def extract_data(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except OSError:
        print("File could not be read")
        return []

    data_list = []
    current_caliber = None
    current_type = None
    types = []
    slug_types = []
    shot_types = []
    shot_sum_types = []

    for line in lines:
        line = line.strip()

        if line.startswith("////"):
            if current_caliber:
                if current_type:
                    if "ProjectileCount" in current_type and int(current_type["ProjectileCount"]) > 2:
                        shot_types.append(current_type)
                        shot_sum_type = current_type.copy()
                        shot_sum_type["Damage"] = str(int(current_type["Damage"]) * int(current_type["ProjectileCount"]))
                        shot_sum_types.append(shot_sum_type)
                    else:
                        slug_types.append(current_type)
                    current_type = None

                if shot_types and slug_types:
                    data_list.append({"caliber": current_caliber + " shot", "types": shot_types})
                    data_list.append({"caliber": current_caliber + " shot sum", "types": shot_sum_types})
                    data_list.append({"caliber": current_caliber + " slug", "types": slug_types})
                else:
                    data_list.append({"caliber": current_caliber, "types": shot_types + slug_types})

            current_caliber = line.replace("////", "").strip()
            if current_caliber == "AMMO":
                current_caliber = ""
                continue
            types = []
            slug_types = []
            shot_types = []
            shot_sum_types = []

        elif line.startswith("///"):
            break

        elif line.startswith("//"):
            if current_type:
                if "ProjectileCount" in current_type and int(current_type["ProjectileCount"]) > 2:
                    shot_types.append(current_type)
                    shot_sum_type = current_type.copy()
                    shot_sum_type["Damage"] = str(int(current_type["Damage"]) * int(current_type["ProjectileCount"]))
                    shot_sum_types.append(shot_sum_type)
                else:
                    slug_types.append(current_type)
            current_type = {"name": line.replace("//", "").strip()}

        elif "serverItem._props." in line:
            key, value = line.replace("serverItem._props.", "").split(" = ")
            current_type[key.strip()] = value.strip().strip(";")

    if current_type:
        if "ProjectileCount" in current_type and int(current_type["ProjectileCount"]) > 1:
            shot_types.append(current_type)
            shot_sum_type = current_type.copy()
            shot_sum_type["Damage"] = str(int(current_type["Damage"]) * int(current_type["ProjectileCount"]))
            shot_sum_types.append(shot_sum_type)
        else:
            slug_types.append(current_type)
    if current_caliber:
        if shot_types and slug_types:
            data_list.append({"caliber": current_caliber + " shot", "types": shot_types})
            data_list.append({"caliber": current_caliber + " shot sum", "types": shot_sum_types})
            data_list.append({"caliber": current_caliber + " slug", "types": slug_types})
        else:
            data_list.append({"caliber": current_caliber, "types": shot_types + slug_types})

    return data_list

def set_default_values(data):
    keys = ["ProjectileCount", "Damage", "PenetrationPower", "InitialSpeed", "RicochetChance", "FragmentationChance", 
            "BulletMassGram", "HeavyBleedingDelta", "LightBleedingDelta", "ammoAccr", "ammoHear", "ammoRec", 
            "malf_changes", "MalfMisfireChance", "MisfireChance", "MalfFeedChance", "DurabilityBurnModificator", 
            "HeatFactor"]

    for caliber in data:
        for ammo_type in caliber["types"]:
            for key in keys:
                if key not in ammo_type:
                    ammo_type[key] = 0

data = extract_data(input_file)
set_default_values(data)

with open(output_file, "w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Data has been saved to {output_file}.")
