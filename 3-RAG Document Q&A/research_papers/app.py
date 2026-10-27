import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
# =========================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")


# =========================================================
# 2. LLM - GROQ
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# =========================================================
# 3. PROMPT
# =========================================================

prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.

    Please provide the most accurate response based on the question.
    If the answer is not available in the context, say:
    "The answer is not available in the provided documents."

    <context>
    {context}
    </context>

    Question: {input}
    """
)


# =========================================================
# 4. CREATE VECTOR DATABASE
# =========================================================

def create_vector_embedding():

    if "vectors" not in st.session_state:

        # -----------------------------
        # Embedding Model
        # -----------------------------

        st.session_state.embeddings = OllamaEmbeddings(
            model="nomic-embed-text"
        )
        # -----------------------------
        # Document Loading
        # -----------------------------

        st.session_state.loader = PyPDFDirectoryLoader(".")

        st.session_state.docs = st.session_state.loader.load()

        # -----------------------------
        # Text Splitting
        # -----------------------------

        st.session_state.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        st.session_state.final_documents = (
            st.session_state.text_splitter
            .split_documents(
                st.session_state.docs[:50]
            )
        )

        # -----------------------------
        # FAISS Vector Database
        # -----------------------------

        st.session_state.vectors = FAISS.from_documents(
            st.session_state.final_documents,
            st.session_state.embeddings
        )


# =========================================================
# 5. STREAMLIT UI
# =========================================================

st.title("📚 Research Paper RAG Chatbot")

st.write(
    "Ask questions based on the research papers "
    "present inside the `research_papers` folder."
)


# =========================================================
# 6. EMBEDDING BUTTON
# =========================================================

if st.button("Document Embedding"):

    with st.spinner("Loading documents and creating vector database..."):

        create_vector_embedding()

    st.success("Vector Database is ready! ✅")


# =========================================================
# 7. USER QUERY
# =========================================================

user_prompt = st.text_area(
    "Enter your query from the research paper"
)


# =========================================================
# 8. QUESTION ANSWERING
# =========================================================

if user_prompt:

    # Check whether vector database exists
    if "vectors" not in st.session_state:

        st.warning(
            "Please click 'Document Embedding' first."
        )

    else:

        # -----------------------------
        # Document Chain
        # -----------------------------

        document_chain = create_stuff_documents_chain(
            llm,
            prompt
        )

        # -----------------------------
        # Retriever
        # -----------------------------

        retriever = st.session_state.vectors.as_retriever()

        # -----------------------------
        # Retrieval Chain
        # -----------------------------

        retrieval_chain = create_retrieval_chain(
            retriever,
            document_chain
        )

        # -----------------------------
        # Measure Response Time
        # -----------------------------

        start = time.perf_counter()

        response = retrieval_chain.invoke(
            {
                "input": user_prompt
            }
        )

        response_time = time.perf_counter() - start

        # -----------------------------
        # Display Answer
        # -----------------------------

        st.subheader("Answer")

        st.write(
            response["answer"]
        )

        # -----------------------------
        # Response Time
        # -----------------------------

        st.caption(
            f"Response time: {response_time:.2f} seconds"
        )

        # =================================================
        # 9. SHOW RETRIEVED DOCUMENTS
        # =================================================

        ## With a stremlit expainder
        with st.expander("Document similarity Search"):
            for i,doc in enumerate(response['context']):
                st.write(doc.page_content)
                st.write('------------------------')