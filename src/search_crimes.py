import json
import os

# Get project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# JSON path
file_path = os.path.join(BASE_DIR, "data", "crime_records.json")

# Load data
with open(file_path, "r") as file:
    crime_data = json.load(file)

# Ask user for search
query = input("Enter search term: ").lower()

print("\nSearching...\n")

found = False

for crime in crime_data:

    searchable_text = (
        crime["crime_type"] + " " +
        crime["location"] + " " +
        crime["suspect"] + " " +
        crime["features"]
    ).lower()

    if query in searchable_text:

        found = True

        print("=" * 50)
        print(f"Case ID     : {crime['case_id']}")
        print(f"Crime Type  : {crime['crime_type']}")
        print(f"Location    : {crime['location']}")
        print(f"Date        : {crime['date']}")
        print(f"Suspect     : {crime['suspect']}")
        print(f"Features    : {crime['features']}")
        print("=" * 50)

if not found:
    print("No matching crime records found.")
