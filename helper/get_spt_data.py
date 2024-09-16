import json

# File is located in \SPT_Data\Server\database\templates\
items_file = "data/items.json"

try:
    with open(items_file, mode="r", encoding="UTF-8") as file:
        data  = json.load(file)
except OSError:
    print("items.json could not be open")
    exit()
caliber = set()
data = {key:value for key,value in data.items() if value["_name"].startswith("patron_")}
for ammo in data:
    caliber.add(data[ammo]["_props"]["Caliber"])
print(*caliber,sep="\n")