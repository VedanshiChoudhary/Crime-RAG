import os

from ai_image_features import analyze_image

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from neo4j import GraphDatabase

import ollama


# ==========================
# Project Path
# ==========================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ==========================
# Load FAISS Database
# ==========================

print("\nLoading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vector_path = os.path.join(
    BASE_DIR,
    "vector_database"
)


print("Loading crime vector database...")

db = FAISS.load_local(
    vector_path,
    embedding_model,
    allow_dangerous_deserialization=True
)



# ==========================
# Neo4j Connection
# ==========================

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Meeting@123"


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)



# ==========================
# Neo4j Query
# ==========================

def get_case(tx, case_id):

    query = """

    MATCH (p:Person)-[:INVOLVED_IN]->(c:Case)
    MATCH (c)-[:OCCURRED_AT]->(l:Location)
    MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)

    WHERE c.id = $case_id

    RETURN
    p.name AS person,
    c.id AS case,
    c.crime AS crime,
    c.date AS date,
    l.name AS location,
    e.description AS evidence

    """

    return tx.run(
        query,
        case_id=case_id
    ).data()



# ==========================
# Ollama Report Generator
# ==========================

def generate_report(data):

    prompt = f"""

You are a forensic investigation assistant.

Create a professional forensic report using ONLY this information:

{data}


Include:

1. Case ID
2. Crime type
3. Date
4. Location
5. Suspect description
6. Evidence analysis
7. Investigation summary
8. Recommendations


Rules:

- Use only provided information.
- Do not guess ethnicity, nationality, age, or identity.
- Do not create fake evidence.
- Do not mention police actions unless provided.
- If information is missing write "Not available".
- Clearly separate evidence and analysis.
- Do not claim the suspect is identified.

"""


    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response["message"]["content"]



# ==========================
# MAIN PROGRAM
# ==========================

print("\n========== CRIME RAG SYSTEM ==========")


image_path = input(
    "\nEnter sketch image path: "
)


# --------------------------
# AI Sketch Analysis
# --------------------------

features = analyze_image(image_path)


if features is None:
    print("Image not found!")
    exit()


print("\n===== AI FEATURES =====")

for key, value in features.items():
    print(f"{key}: {value}")



# --------------------------
# Create Search Query
# --------------------------

facial_mark = features["facial_mark"]

if facial_mark == "unknown":
    facial_mark = "scar or facial mark"


query = f"""

Crime suspect description:

Hair: {features['hair']}

Face shape: {features['face_shape']}

Facial feature:
{facial_mark}

Find crime records with similar suspect appearance.

"""


print("\n===== SEARCH QUERY =====")
print(query)



# --------------------------
# FAISS Search
# --------------------------

print("\n===== SEARCHING CASES =====")


results = db.similarity_search(
    query,
    k=1
)



case_ids = []


for doc in results:

    print("\nMatched Record:")
    print(doc.page_content)

    case_ids.append(
        doc.metadata["case_id"]
    )



# --------------------------
# Neo4j Search
# --------------------------

graph_data = []


with driver.session() as session:

    for case_id in case_ids:

        result = session.execute_read(
            get_case,
            case_id
        )

        graph_data.extend(result)



driver.close()



print("\n===== GRAPH DATA =====")

for item in graph_data:
    print(item)



# --------------------------
# Generate Report
# --------------------------

final_report = generate_report(
    graph_data
)


print(
    "\n========== FINAL FORENSIC REPORT ==========\n"
)


print(final_report)
