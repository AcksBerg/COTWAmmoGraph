import requests
import json


def run_query(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))


new_query = """
query Ammo_query {
  items(lang: en, type: ammo) {
    id
    name
    properties {
      ... on ItemPropertiesAmmo {
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
      }
    }
  }
}
"""
with open("live_data.json", "w") as file:
    json.dump(run_query(new_query), file, indent=4)
