import json

# Path to the JSON file
file_path = "data/crime_records.json"

# Read JSON data
with open(file_path, "r") as file:
    crime_data = json.load(file)

print("Crime Records Loaded Successfully!\n")

for crime in crime_data:
    print(f"Case ID     : {crime['case_id']}")
    print(f"Crime Type  : {crime['crime_type']}")
    print(f"Location    : {crime['location']}")
    print(f"Date        : {crime['date']}")
    print(f"Suspect     : {crime['suspect']}")
    print(f"Features    : {crime['features']}")
    print("-" * 40)
