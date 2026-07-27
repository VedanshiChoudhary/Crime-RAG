import os

from ai_image_features import analyze_image

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from neo4j import GraphDatabase


# ==========================
# Paths
# ==========================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ==========================
# Load FAISS
# ==========================

print("Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


db_path = os.path.join(
    BASE_DIR,
    "vector_database"
)


print("Loading vector database...")


db = FAISS.load_local(
    db_path,
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
# Input Sketch
# ==========================

image_path = input(
    "\nEnter sketch image path: "
)


features = analyze_image(image_path)


if features is None:
    print("Image not found")
    exit()



# ==========================
# Create Search Query
# ==========================

query_text = f"""
black hair
{features['face_shape']} face
{features['facial_mark']}
"""


print("\nGenerated Query:")
print(query_text)



# ==========================
# FAISS Search
# ==========================

results = db.similarity_search(
    query_text,
    k=3
)


case_ids = []


print("\n===== FAISS Results =====")


for doc in results:

    print(doc.page_content)

    case_id = doc.metadata["case_id"]

    case_ids.append(case_id)



# ==========================
# Neo4j Search
# ==========================


def get_case(tx, case_id):

    query = """

    MATCH (p:Person)-[:INVOLVED_IN]->(c:Case)
    MATCH (c)-[:OCCURRED_AT]->(l:Location)
    MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)

    WHERE c.id=$case_id

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



print("\n===== GRAPH RESULTS =====")


graph_results=[]


with driver.session() as session:

    for cid in case_ids:

        data=session.execute_read(
            get_case,
            cid
        )

        graph_results.extend(data)



for item in graph_results:

    print("\n----------------")
    print(item)



driver.close()


print("\n===== INVESTIGATION COMPLETE =====")
