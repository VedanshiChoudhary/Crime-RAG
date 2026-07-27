import os

from ai_image_features import analyze_image

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# Project path
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# Load embedding model
print("Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load FAISS database

db_path = os.path.join(
    BASE_DIR,
    "vector_database"
)

print("Loading crime database...")

db = FAISS.load_local(
    db_path,
    embedding_model,
    allow_dangerous_deserialization=True
)



# Input sketch

image_path = input(
    "Enter sketch image path: "
)


features = analyze_image(image_path)


if features is None:
    print("Image not found!")
    exit()



# Create query

query = f"""
hair: {features['hair']}
face shape: {features['face_shape']}
facial mark: {features['facial_mark']}
"""


print("\n===== Generated Query =====")
print(query)



# Search FAISS

results = db.similarity_search(
    query,
    k=3
)



print("\n===== Matching Crime Records =====")


for result in results:

    print("\n-----------------------------")
    print(result.page_content)
