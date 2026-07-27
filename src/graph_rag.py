import os
import ollama

from neo4j import GraphDatabase

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


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
# Load FAISS Vector Database
# ==========================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

db_path = os.path.join(
    BASE_DIR,
    "vector_database"
)


print("Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


print("Loading vector database...")

vector_db = FAISS.load_local(
    db_path,
    embedding_model,
    allow_dangerous_deserialization=True
)


print("\n🚔 Graph RAG System Ready!")


# ==========================
# Neo4j Graph Search
# ==========================

def search_graph(case_id):

    query = """

    MATCH (p:Person)-[:INVOLVED_IN]->(c:Case)
    MATCH (c)-[:OCCURRED_AT]->(l:Location)
    MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)

    WHERE c.id = $case_id

    RETURN
    p.name AS suspect,
    c.id AS case_id,
    c.crime AS crime,
    c.date AS date,
    l.name AS location,
    e.description AS evidence

    """

    with driver.session() as session:

        result = session.run(
            query,
            case_id=case_id
        )

        return [
            record.data()
            for record in result
        ]



# ==========================
# Main Graph RAG Loop
# ==========================

while True:

    question = input(
        "\nAsk forensic question (type exit): "
    )


    if question.lower() == "exit":
        break


    # ======================
    # FAISS Search
    # ======================

    documents = vector_db.similarity_search(
        question,
        k=3
    )


    text_context = ""
    graph_context = ""

    case_ids = []


    for doc in documents:

        text_context += doc.page_content
        text_context += "\n\n"

        case_ids.append(
            doc.metadata["case_id"]
        )


    # ======================
    # Neo4j Search
    # ======================

    for case_id in case_ids:

        graph_results = search_graph(case_id)

        for item in graph_results:

            graph_context += str(item)
            graph_context += "\n"



    # ======================
    # Llama Prompt
    # ======================

    prompt = f"""

You are a forensic investigation assistant.

Use ONLY the information provided below.

IMPORTANT RULES:

- Do not invent facts.
- Do not change crime types.
- Do not merge evidence from different cases.
- Keep each case's evidence separate.
- Do not call a mark a scar unless the record says scar.
- Do not call a scar a mark unless the record says mark.
- If information is missing, write "not available".


TEXT RECORDS:

{text_context}


GRAPH INFORMATION:

{graph_context}


INVESTIGATION QUESTION:

{question}


Create a professional forensic investigation report.

Include:

1. Case ID
2. Exact crime type
3. Date
4. Location
5. Suspect description
6. Evidence
7. Investigation summary
8. Recommendations


"""


    # ======================
    # Generate Report
    # ======================

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    print("\n========== FINAL INVESTIGATION REPORT ==========\n")


    print(
        response["message"]["content"]
    )


driver.close()
