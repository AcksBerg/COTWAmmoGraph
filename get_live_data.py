import requests
import json


def run_query(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))


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
        bulletMassGrams
        durabilityBurnFactor
      }
    }
  }
}
"""

data = run_query(ammo_query)

with open("live_data.json", "w", encoding="UTF-8") as file:
    json.dump(data, file, indent=4)

caliber_data = {}

for entry in data["data"]["items"]:
    if entry["name"].lower().find("grenade") != -1 or not entry.get("properties"):
        continue
    if entry["properties"]["caliber"] not in caliber_data:
        caliber_data[entry["properties"]["caliber"]] = [entry["name"]]
        continue
    caliber_data[entry["properties"]["caliber"]].append(entry["name"])

with open("caliber_data.json", "w", encoding="UTF-8") as file:
    json.dump(caliber_data, file, indent=4)