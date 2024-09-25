import requests
import json
from caliber_and_types import available_data_types, caliber_map, blacklisted_ammo

# File paths
output_file = "data/live_data.json"  # Output file to store the processed data

# Function to request data from tarkov.dev API


def run_query(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Query failed to run by returning code of {response.status_code}. {query}"
        )


# GraphQL query to fetch ammunition data
ammo_query = """
query Ammo_query {
  items(lang: en, type: ammo) {
    id
    name
    weight
    properties {
      ... on ItemPropertiesAmmo {
        caliber
        penetrationPower
        damage
        armorDamage
        projectileCount
        initialSpeed
        ballisticCoeficient
        ricochetChance
        fragmentationChance
        bulletMassGrams
        heavyBleedModifier
        lightBleedModifier
        failureToFeedChance
        misfireChance
        heatFactor
        durabilityBurnFactor
      }
    }
  }
}
"""

# Fetch data from the API
data = run_query(ammo_query)

# Initialize the output dictionary
output_dict = {}
missing_calibers = set()

# Process each ammunition item
for entry in data["data"]["items"]:
    # Skip grenades and items without properties
    if 'grenade' in entry["name"].lower() or not entry.get("properties") or entry.get("id", "A") in blacklisted_ammo:
        continue
    properties = entry["properties"]
    # Get the caliber code
    caliber = properties.get("caliber")
    if caliber not in caliber_map:
        missing_calibers.add(caliber)  # Collect calibers not in the map
        continue
    cal_name = caliber_map[caliber]
    # Initialize the list for this caliber if not already done
    if cal_name not in output_dict:
        output_dict[cal_name] = []
    # Prepare the ammunition entry
    ammo_entry = {}
    ammo_entry["id"] = entry["id"]
    # Remove the caliber prefix from the name
    name = entry["name"]
    cal_prefix = cal_name
    # Adjust for special cases (e.g., .300 Blackout)
    if cal_name == ".300":
        cal_prefix += " Blackout"
    if cal_name == "6.8x51mm":
        cal_prefix += " (.277 SIG Fury)"
    if name.startswith(cal_prefix):
        name = name[len(cal_prefix):].strip()
    # Capitalize the first letter
    if name:
        name = name[0].upper() + name[1:]
    ammo_entry["Name"] = name

    # Map property names to match available_data_types
    property_mappings = {
        "penetrationPower": "PenetrationPower",
        "durabilityBurnFactor": "DurabilityBurnModificator",
        "damage": "Damage",
        "armorDamage": "ArmorDamage",
        "projectileCount": "ProjectileCount",
        "initialSpeed": "InitialSpeed",
        "ballisticCoeficient": "BallisticCoeficient",
        "ricochetChance": "RicochetChance",
        "fragmentationChance": "FragmentationChance",
        "bulletMassGrams": "BulletMassGram",
        "heavyBleedModifier": "HeavyBleedingDelta",
        "lightBleedModifier": "LightBleedingDelta",
        "failureToFeedChance": "MalfFeedChance",
        "misfireChance": "MalfMisfireChance",
        "heatFactor": "HeatFactor",
        "id": "id"
    }

    # Copy and rename the properties
    for prop_key, prop_value in properties.items():
        mapped_key = property_mappings.get(prop_key)
        if mapped_key:
            ammo_entry[mapped_key] = prop_value

    # Add the weight from the main entry
    ammo_entry["Weight"] = entry["weight"]

    # Include only the properties in available_data_types
    ammo_entry = {k: v for k, v in ammo_entry.items() if k in available_data_types}

    # Add the ammo entry to the output dictionary
    output_dict[cal_name].append(ammo_entry)

# Print missing calibers, if any (useful for updating caliber_map)
if missing_calibers:
    print("Calibers not in caliber_map (Missing/Blacklisted):")
    print(*missing_calibers, sep="\n")

# Write the output dictionary to the output file
with open(output_file, "w", encoding="UTF-8") as file:
    json.dump(output_dict, file, indent=4)
