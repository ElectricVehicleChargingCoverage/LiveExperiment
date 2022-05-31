import json
import math

filename = input("Filename in output Folder (without .json ending):")

def distance(dataEntry, apiEntry):
    return distanceBetween(dataEntry["latitude"], dataEntry["longitude"], apiEntry["latitude"], apiEntry["longitude"])


def distanceBetween(lat1, lon1, lat2, lon2):
    lat = (lat1 + lat2) / 2 * 0.01745
    dx = 111.3 * math.cos(lat) * (lon1 - lon2)
    dy = 111.3 * (lat1 - lat2)
    distance = math.sqrt(dx * dx + dy * dy)
    return distance

with open(f"output/{filename}.json", encoding='ascii') as input_file:
    data = json.load(input_file)
    print("Dataset has", len(data), "entries.")

    with open(f"APIResponse/{filename}.json", encoding='ascii') as api_file:
        api = json.load(api_file)
        points = api['points']
        print("Api response has", len(points), "entries.")

        lastEntryIndex = 0

        for apiEntry in points:
            # Find closest data point in real dataset:
            index = lastEntryIndex
            best = distance(data[index], apiEntry)
            for i in range(max(0, lastEntryIndex - 4), min(lastEntryIndex + 50, len(data))):
                if distance(data[i], apiEntry) < best:
                    best = distance(data[i], apiEntry)
                    index = i
            # Found closest real world data point at index.
            lastEntryIndex = index

            soc_diff = apiEntry["soc_percent"] * 100 - data[index]["SoCInput"]
            apiEntry["SoC_measured"] = data[index]["SoCInput"]
            apiEntry["soc_diff"] = soc_diff
            apiEntry["floored_soc_diff"] = math.floor(soc_diff)
            apiEntry["abs_soc_diff"] = abs(soc_diff)


        with open(f'output/{filename}_comparison.csv', 'w') as csvFile:
            csvFile.write("latitude,longitude,soc_difference,floored_soc_difference,absolute_difference,remaining_kWh,SoC,SoC_measured\n")
            first = True
            for p in points:
                if first: # Skip first point
                    first = False
                    continue
                csvFile.write(f"{p['latitude']},{p['longitude']},{p['soc_diff']},{p['floored_soc_diff']},{p['abs_soc_diff']},{p['soc']},{p['soc_percent']*100},{p['SoC_measured']}\n")

print("Done")