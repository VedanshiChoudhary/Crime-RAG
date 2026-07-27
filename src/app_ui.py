import streamlit as st
import tempfile
import os

from pyvis.network import Network

from ai_image_features import analyze_image

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from neo4j import GraphDatabase

import ollama


# ==========================
# PAGE CONFIGURATION
# ==========================

st.set_page_config(
    page_title="Crime-RAG Investigation System",
    page_icon="🔎",
    layout="wide"
)


st.title("🔎 Crime-RAG Investigation System")

st.write(
    """
    AI powered forensic investigation system using:

    - Computer Vision Sketch Analysis
    - FAISS Semantic Search
    - Neo4j Knowledge Graph
    - Ollama Llama 3.2
    """
)


# ==========================
# PROJECT PATH
# ==========================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)



# ==========================
# LOAD VECTOR DATABASE
# ==========================

@st.cache_resource
def load_database():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        os.path.join(BASE_DIR, "vector_database"),
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db



db = load_database()



# ==========================
# NEO4J CONNECTION
# ==========================

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "Meeting@123")
)



# ==========================
# GET CASE FROM NEO4J
# ==========================

def get_case(case_id):

    query = """

    MATCH (p:Person)-[:INVOLVED_IN]->(c:Case)
    MATCH (c)-[:OCCURRED_AT]->(l:Location)
    MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)

    WHERE c.id=$id

    RETURN

    p.name AS person,
    c.id AS case,
    c.crime AS crime,
    c.date AS date,
    l.name AS location,
    e.description AS evidence

    """


    with driver.session() as session:

        result = session.run(
            query,
            id=case_id
        )

        return result.data()



# ==========================
# CREATE GRAPH VISUALIZATION
# ==========================

def create_graph(case_data):

    net = Network(
        height="500px",
        width="100%",
        bgcolor="white",
        font_color="black"
    )


    for item in case_data:

        person = item["person"]
        case = item["case"]
        location = item["location"]
        evidence = item["evidence"]


        net.add_node(
            person,
            label=person,
            color="blue"
        )


        net.add_node(
            case,
            label=case,
            color="red"
        )


        net.add_node(
            location,
            label=location,
            color="green"
        )


        net.add_node(
            evidence,
            label=evidence,
            color="orange"
        )


        net.add_edge(
            person,
            case,
            label="INVOLVED_IN"
        )


        net.add_edge(
            case,
            location,
            label="OCCURRED_AT"
        )


        net.add_edge(
            case,
            evidence,
            label="HAS_EVIDENCE"
        )


    file_path = "crime_graph.html"

    net.save_graph(file_path)


    return file_path



# ==========================
# UPLOAD IMAGE
# ==========================

uploaded_file = st.file_uploader(
    "Upload Suspect Sketch",
    type=["jpg", "jpeg", "png"]
)



if uploaded_file:


    st.image(
        uploaded_file,
        caption="Uploaded Suspect Sketch",
        width=400
    )



    if st.button("🚀 Analyze Sketch"):


        # Save uploaded image temporarily

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        ) as file:

            file.write(
                uploaded_file.getvalue()
            )

            image_path = file.name



        # ======================
        # AI FEATURE EXTRACTION
        # ======================


        with st.spinner(
            "Analyzing sketch..."
        ):

            features = analyze_image(
                image_path
            )


        st.success(
            "Sketch analysis completed"
        )


        st.subheader(
            "🧠 AI Extracted Features"
        )


        col1, col2, col3 = st.columns(3)


        with col1:
            st.metric(
                "Hair",
                features["hair"]
            )


        with col2:
            st.metric(
                "Face Shape",
                features["face_shape"]
            )


        with col3:
            st.metric(
                "Face Detected",
                features["face_detected"]
            )



        # ======================
        # FAISS SEARCH
        # ======================


        query = f"""

        Hair:
        {features['hair']}

        Face shape:
        {features['face_shape']}

        Facial mark:
        scar facial mark

        """



        with st.spinner(
            "Searching crime database..."
        ):

            results = db.similarity_search(
                query,
                k=1
            )



        case_id = results[0].metadata["case_id"]



        # ======================
        # NEO4J DATA
        # ======================


        case_data = get_case(
            case_id
        )


        st.subheader(
            "📁 Matching Crime Case"
        )


        st.json(
            case_data
        )



        # ======================
        # GRAPH DISPLAY
        # ======================


        graph_file = create_graph(
            case_data
        )


        st.subheader(
            "🕸️ Crime Knowledge Graph"
        )


        with open(
            graph_file,
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()


        st.components.v1.html(
            html,
            height=550
        )



        # ======================
        # OLLAMA REPORT
        # ======================


        with st.spinner(
            "Generating forensic report..."
        ):


            prompt = f"""

            Create a professional forensic investigation report.

            Use only this information:

            {case_data}

            Do not invent information.

            """


            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )



        report = response["message"]["content"]



        st.subheader(
            "📄 Final Investigation Report"
        )


        st.text_area(
            "Report",
            report,
            height=400
        )



        st.download_button(
            label="⬇️ Download Report",
            data=report,
            file_name="forensic_report.txt",
            mime="text/plain"
        )
