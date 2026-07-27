from neo4j import GraphDatabase
import json
import os


# Neo4j connection
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Meeting@123"


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# Find project folder
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# Crime data location
json_path = os.path.join(
    BASE_DIR,
    "data",
    "crime_records.json"
)


# Load crime records
with open(json_path, "r") as file:
    crimes = json.load(file)



def create_graph(tx, crime):

    query = """

    CREATE (case:Case {
        id:$case_id,
        crime:$crime_type,
        date:$date
    })


    CREATE (person:Person {
        name:$suspect
    })


    CREATE (location:Location {
        name:$location
    })


    CREATE (evidence:Evidence {
        description:$features
    })


    CREATE
    (person)-[:INVOLVED_IN]->(case),
    (case)-[:OCCURRED_AT]->(location),
    (case)-[:HAS_EVIDENCE]->(evidence)

    """

    tx.run(
        query,
        case_id=crime["case_id"],
        crime_type=crime["crime_type"],
        date=crime["date"],
        suspect=crime["suspect"],
        location=crime["location"],
        features=crime["features"]
    )



# Insert data into Neo4j
with driver.session() as session:

    for crime in crimes:

        session.execute_write(
            create_graph,
            crime
        )


print("✅ Crime Knowledge Graph Created!")

driver.close()
