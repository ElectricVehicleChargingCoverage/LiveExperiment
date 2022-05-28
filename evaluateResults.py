import json
import math

filename = input("Filename in data Folder (without .json ending):")

SoCMap = {}

batteryCapacity = 79000.0 # max battery capacity in Wh


def distanceBetween(lat1, lon1, lat2, lon2):
    lat = (lat1 + lat2) / 2 * 0.01745
    dx = 111.3 * math.cos(lat) * (lon1 - lon2)
    dy = 111.3 * (lat1 - lat2)
    distance = math.sqrt(dx * dx + dy * dy)
    return distance

def updateSoCMap(lastEntry, entry):
    SoC = lastEntry["SoCInput"]
    SoCMap[SoC] = {}
    SoCMap[SoC]["distance"] = entry["totalDistance"] - lastEntry["totalDistance"]
    SoCMap[SoC]["time"] = entry["tripTime"] - lastEntry["tripTime"]

with open(f"data/{filename}.json", encoding='ascii') as input_file:
    data = json.load(input_file)
    print("Dataset has", len(data), "entries.")

    lastEntry = None
    lastEntryWithSoC = None

    for entry in data:
        if (lastEntry == None): # set defaults for first entry
            entry["totalDistance"] = 0
            entry["distanceSinceLastPoint"] = 0
            lastEntry = entry
            lastEntryWithSoC = entry
            continue
        
        entry["distanceSinceLastPoint"] = distanceBetween(entry["latitude"], entry["longitude"], lastEntry["latitude"], lastEntry["longitude"])
        entry["totalDistance"] = entry["distanceSinceLastPoint"] + lastEntry["totalDistance"]

        timeSinceLastPoint = entry["tripTime"] - lastEntry["tripTime"]
        entry["speedApprox"] = round(entry["distanceSinceLastPoint"] * 3600 / timeSinceLastPoint, 2)

        if (lastEntryWithSoC["SoCInput"] != entry["SoCInput"]):
            updateSoCMap(lastEntryWithSoC, entry)
            lastEntryWithSoC = entry

        # Update last entry
        lastEntry = entry
    
    updateSoCMap(lastEntryWithSoC, data[-1])

    # 2nd loop to calculate consumption
    for entry in data:
        SoC = entry["SoCInput"]
        proportion = entry["distanceSinceLastPoint"] / SoCMap[SoC]["distance"]
        entry["proportion"] = proportion
        entry["Wh"] = (batteryCapacity / 100) * proportion # /100 because this is the amount of Wh for 1% battery capacity
        if (entry["distanceSinceLastPoint"] > 0):
            entry["consumptionPerKm"] = entry["Wh"] / entry["distanceSinceLastPoint"]
        else:
            entry["consumptionPerKm"] = 0



with open(f'output/{filename}.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)

print("Done")
