import os

from image_features import extract_features

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# ==========================
# Load Embedding Model
# ==========================

print("Loading embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ==========================
# Load Vector Database
# ==========================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

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


# ==========================
# User Input
# ==========================

image_path = input("\nEnter sketch image path: ")

features = extract_features(image_path)

if features is None:
    print("❌ Image not found!")
    exit()


# ==========================
# Create Search Query
# ==========================

query = f"""
{features['hair']}
{features['face_shape']}
{features['facial_mark']}
"""

print("\nGenerated Search Query:")
print(query)


# ==========================
# Search FAISS
# ==========================

results = db.similarity_search(
    query,
    k=3
)


print("\n===== Matching Crime Records =====\n")

for doc in results:

    print(doc.page_content)

    print("-----------------------------------------")
