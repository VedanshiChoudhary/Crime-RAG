import json
import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load crime records
json_path = os.path.join(BASE_DIR, "data", "crime_records.json")

with open(json_path, "r") as file:
    crime_data = json.load(file)

documents = []

for crime in crime_data:
    text = f"""
    Case ID: {crime['case_id']}
    Crime Type: {crime['crime_type']}
    Location: {crime['location']}
    Date: {crime['date']}
    Suspect: {crime['suspect']}
    Features: {crime['features']}
    """

    documents.append(
        Document(
            page_content=text,
            metadata={"case_id": crime["case_id"]}
        )
    )

print("Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Creating vector database...")

db = FAISS.from_documents(documents, embedding_model)

save_path = os.path.join(BASE_DIR, "vector_database")

db.save_local(save_path)

print("\n✅ Vector database created successfully!")
print(f"Saved to: {save_path}")
