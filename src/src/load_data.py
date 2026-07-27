import json
import os

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the JSON file
file_path = os.path.join(BASE_DIR, "data", "crime_records.json")

# Read the JSON file
with open(file_path, "r") as file:
    crime_data = json.load(file)

print("\n Crime Records Loaded Successfully!\n")

for crime in crime_data:
    print(f"Case ID     : {crime['case_id']}")
    print(f"Crime Type  : {crime['crime_type']}")
    print(f"Location    : {crime['location']}")
    print(f"Date        : {crime['date']}")
    print(f"Suspect     : {crime['suspect']}")
    print(f"Features    : {crime['features']}")
    print("-" * 50)
