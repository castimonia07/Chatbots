# 💬 Project 4: Conversational RAG with Multi-PDF Upload & Chat History

An advanced, multi-turn Conversational Retrieval-Augmented Generation (RAG) assistant that allows users to dynamically upload multiple PDF documents, maintains chat history across distinct user sessions, and intelligently reformulates follow-up queries using a **History-Aware Retriever**.

---

## 🏗️ Architecture Diagram

```mermaid
flowchart TD
    User([👤 User]) -->|Uploads PDFs & Enters Session ID| UI[Streamlit UI]
    
    subgraph Document_Processing [Dynamic PDF Ingestion Pipeline]
        Upload[st.file_uploader: Multiple PDFs] --> TempFiles[Tempfile Handler]
        TempFiles --> PDFLoader[PyPDFLoader]
        PDFLoader --> Splitter[RecursiveCharacterTextSplitter\nchunk_size=5000, overlap=500]
        Splitter --> Embeddings[OllamaEmbeddings\nmodel: nomic-embed-text]
        Embeddings --> ChromaDB[(Chroma Vector Database\nIn-Memory Store)]
    end

    subgraph Conversational_RAG [Two-Stage Conversational Retrieval Pipeline]
        UserQuery[User Question] --> SessionStore[(Session History Store\nst.session_state.store[session_id])]
        
        SessionStore --> HistoryAwareRetriever[History-Aware Retriever\nRephrases follow-up questions to standalone query]
        UserQuery --> HistoryAwareRetriever
        ChromaDB -.->|Indexed Chunks| HistoryAwareRetriever
        
        HistoryAwareRetriever --> Context[Retrieved Document Context]
        Context --> StuffChain[create_stuff_documents_chain\nSystem Prompt + Context + Chat History]
        
        StuffChain --> GroqLLM[ChatGroq\nmodel: openai/gpt-oss-20b]
        GroqLLM --> Answer[Synthesized Grounded Answer]
    end

    subgraph State_Management [RunnableWithMessageHistory]
        Runnable[RunnableWithMessageHistory Wrapper]
        Runnable -->|Appends Q&A to Session History| SessionStore
    end

    Answer --> UI
    SessionStore -.->|Renders Full History| UI
```

---

## 📌 Detailed Features & Concepts Discussed

### 1. Dynamic Multi-File PDF Ingestion
- Users can upload multiple PDF documents simultaneously using `st.file_uploader(..., accept_multiple_files=True)`.
- Files are saved safely to system temporary paths using Python's `tempfile.NamedTemporaryFile` and loaded on the fly via `PyPDFLoader`.

### 2. Chunking & Chroma Vector Database
- Split using `RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)` for larger context windows.
- Ingested directly into `Chroma.from_documents` using `OllamaEmbeddings(model="nomic-embed-text")`.

### 3. History-Aware Retrieval (Query Reformulation)
In multi-turn conversations, follow-up questions like *"Can you summarize its main findings?"* fail in standard vector retrieval because *"its"* lacks semantic context.
- `create_history_aware_retriever`: Uses an LLM to inspect the prior chat turns (`MessagesPlaceholder("chat_history")`) and reformulates ambiguous follow-ups into standalone semantic search queries before hitting ChromaDB.

### 4. Grounded Question Answering Chain
- Integrates `create_stuff_documents_chain` with a prompt template that injects retrieved context, chat history, and the new query.
- Strict instructions restrict the assistant from fabricating information outside the uploaded PDF documents.

### 5. Multi-Session History Management
- Uses `RunnableWithMessageHistory` to manage conversation histories keyed by dynamic `session_id` strings.
- Allows isolated chat threads for different topics, users, or documents:
  ```python
  def get_session_history(session: str) -> BaseChatMessageHistory:
      if session not in st.session_state.store:
          st.session_state.store[session] = ChatMessageHistory()
      return st.session_state.store[session]
  ```

---

## 📁 File Structure

```
4-RAG Q&A-2/
├── app.py          # Conversational RAG application with history & PDF loader
├── temp.pdf        # Sample document for verification & testing
└── README.md       # Project documentation & architecture
```

---

## 🚀 Setup & Execution Guide

### Prerequisites
1. **Groq API Key**: Obtain a key from [Groq Console](https://console.groq.com/).
2. **Ollama**: Ensure Ollama is running with `nomic-embed-text`:
   ```bash
   ollama pull nomic-embed-text
   ```

### Running the Application
From the repository root:
```bash
streamlit run "4-RAG Q&A-2/app.py"
```
Or from within the project directory:
```bash
cd "4-RAG Q&A-2"
streamlit run app.py
```

### Usage Steps
1. Enter your **Groq API Key** in the input field.
2. Specify or keep the default **Session ID** (e.g. `session_1`).
3. Upload one or more PDF files via the file uploader widget.
4. Once processed, type your first question in the text input.
5. Ask follow-up questions referencing earlier answers (e.g., *"Can you elaborate on the second point you mentioned?"*).
6. Observe how the assistant maintains conversational context and prints the session history.
