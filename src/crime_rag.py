import os
import ollama

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# Project path
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Vector database location
db_path = os.path.join(
    BASE_DIR,
    "vector_database"
)


print("Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


print("Loading crime database...")

db = FAISS.load_local(
    db_path,
    embedding_model,
    allow_dangerous_deserialization=True
)


print("\n🚔 Crime RAG System Ready!")


while True:

    question = input(
        "\nAsk investigation question (type exit): "
    )

    if question.lower() == "exit":
        break


    # Retrieve similar cases
    results = db.similarity_search(
        question,
        k=3
    )


    context = ""

    for result in results:
        context += result.page_content
        context += "\n\n"


    prompt = f"""
You are an AI crime investigation assistant.

Use only the following crime records.

Crime Records:
{context}


Investigator Question:
{question}


Create a short investigation report.
Mention relevant case IDs, locations, and evidence.
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


    print("\n===== Investigation Report =====\n")

    print(
        response["message"]["content"]
    )
