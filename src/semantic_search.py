import os

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Location of vector database
db_path = os.path.join(BASE_DIR, "vector_database")


print("Loading AI model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


print("Loading vector database...")

db = FAISS.load_local(
    db_path,
    embedding_model,
    allow_dangerous_deserialization=True
)


print("\n✅ AI Crime Search Ready!")

while True:

    query = input("\nAsk about a crime (type 'exit' to stop): ")

    if query.lower() == "exit":
        break

    results = db.similarity_search(
        query,
        k=3
    )

    print("\n🔍 Related Crime Records:\n")

    for result in results:
        print("-" * 50)
        print(result.page_content)
