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


with open("live_data.json", "w", encoding="UTF-8") as file:
    json.dump(run_query(ammo_query), file, indent=4)
