# 📄 PDF Q&A Chatbot — Production RAG System

A production-oriented **Retrieval-Augmented Generation (RAG) system** for grounded question answering over PDF documents.

This project goes beyond a simple LLM chatbot. It implements an end-to-end RAG architecture with **document processing, semantic retrieval, BM25 lexical retrieval, hybrid retrieval, Cross-Encoder reranking, retrieval confidence gating, conversation-aware RAG, query understanding and rewriting, LLM generation, source citations, API integration, containerization, and cloud deployment**.

The backend is deployed on **Google Cloud Run**, with **Gemini 3.5 Flash** used for production generation and locally bundled Hugging Face models used for retrieval and reranking.

---

## 🎯 Project Objective

The goal of this project is to build a reliable question-answering system that can answer questions from enterprise-style PDF documents while reducing the risk of unsupported or hallucinated answers.

Instead of sending a user question directly to an LLM, the system follows a controlled retrieval-and-generation pipeline:

```text
User Question
      ↓
Query Understanding / Rewriting
      ↓
Hybrid Retrieval
(Vector Search + BM25)
      ↓
Cross-Encoder Reranking
      ↓
Retrieval Confidence Gate
      ↓
Context Construction
      ↓
LLM Generation
(Gemini 3.5 Flash)
      ↓
Answer + Confidence + Citations
```

---

## 🏗️ System Architecture

```text
                         ┌─────────────────────────┐
                         │      Streamlit UI        │
                         │   Conversational App     │
                         └────────────┬────────────┘
                                      │
                                      │ HTTP
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI API        │
                         │                           │
                         │  /health   /ask   /docs │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Query Understanding      │
                         │ & Query Rewriting        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────────┐
                   │          Hybrid Retrieval           │
                   │                                    │
                   │   Semantic Vector Search + BM25    │
                   └──────────────────┬─────────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────────┐
                   │        Cross-Encoder Reranker       │
                   │                                    │
                   │  Re-ranks retrieved document chunks │
                   └──────────────────┬─────────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────────┐
                   │       Retrieval Confidence Gate     │
                   │                                    │
                   │  Determines whether context is     │
                   │  sufficiently relevant for answer  │
                   └──────────────────┬─────────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────────┐
                   │          Context Builder            │
                   │                                    │
                   │ Relevant chunks + metadata +        │
                   │ conversation context                │
                   └──────────────────┬─────────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────────┐
                   │          Gemini 3.5 Flash           │
                   │          LLM Generation             │
                   └──────────────────┬─────────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Answer + Confidence     │
                         │ + Source Citations      │
                         │ + Metadata              │
                         └─────────────────────────┘
```

---

## ✨ Key Capabilities

### Retrieval-Augmented Generation

The system grounds LLM responses using retrieved document context rather than relying solely on the model's pretrained knowledge.

### Hybrid Retrieval

Combines two complementary retrieval strategies:

- **Semantic vector retrieval** for meaning-based matching
- **BM25 lexical retrieval** for keyword-based matching

This provides complementary retrieval signals for different types of questions.

### Cross-Encoder Reranking

Retrieved candidates are passed through a Cross-Encoder reranker to improve the ordering of relevant document chunks before context construction.

Production uses:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

### Retrieval Confidence Gate

The system evaluates retrieval relevance before allowing the generation stage to proceed.

This provides an additional control layer between:

```text
Retrieval → Generation
```

instead of assuming that every retrieved result is sufficiently relevant.

### Conversation-Aware RAG

The system maintains conversational context so that follow-up questions can be interpreted using previous conversation turns.

Example:

```text
User:
What are the company's working hours?

Assistant:
9:00 AM to 6:00 PM, Monday through Friday.

User:
What about the leave policy?
```

The retrieval pipeline can use conversation context when interpreting the follow-up query.

### Query Understanding & Rewriting

User questions can be analyzed and rewritten before retrieval to improve retrieval quality, particularly for conversational and ambiguous queries.

### Source Citations

Responses include source information such as:

- Document
- Page
- Retrieved source information

This helps users trace generated answers back to the underlying documents.

### Confidence & Metadata

API responses expose retrieval-related and model metadata, including:

- Confidence score
- Retrieved document count
- Retrieval distance
- LLM model
- Embedding model
- Citation information

---

## 🧠 LLM & Model Architecture

The application separates the LLM layer from the rest of the RAG pipeline through a provider abstraction.

The provider architecture includes:

```text
LLM Provider
├── Gemini
├── Ollama
└── Bedrock interface
```

The current production deployment uses:

```text
Provider: Gemini
Model:    Gemini 3.5 Flash
```

The retrieval stack uses locally bundled Hugging Face models:

```text
Embedding:
sentence-transformers/all-MiniLM-L6-v2

Reranker:
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The embedding model produces **384-dimensional embeddings**.

---

## 📦 Offline Retrieval Model Packaging

A key production consideration is avoiding runtime downloads of retrieval models.

The embedding and reranker models are bundled into the application container:

```text
models/
├── embedding/
│   └── all-MiniLM-L6-v2/
│
└── reranker/
    └── ms-marco-MiniLM-L-6-v2/
```

Production containers load these models locally with offline Hugging Face/Transformers configuration.

This avoids making application startup dependent on downloading model artifacts from an external model hub.

---

## ☁️ Production Deployment

The FastAPI backend is containerized using Docker and deployed to **Google Cloud Run**.

Production architecture:

```text
Docker Image
     ↓
Google Artifact Registry
     ↓
Google Cloud Run
     ↓
FastAPI Application
     │
     ├── Local Embedding Model
     ├── Local Cross-Encoder
     ├── ChromaDB
     ├── BM25
     └── Gemini 3.5 Flash
              ↓
       Google Gemini API
```

Production infrastructure includes:

- Google Cloud Run
- Google Artifact Registry
- Google Secret Manager
- Google Gemini API

API credentials are supplied through Secret Manager rather than being embedded in the application image.

---

## 🖥️ Application Interfaces

The project provides two application layers.

### FastAPI Backend

The backend exposes the RAG system through REST APIs.

Available endpoints include:

```text
GET  /health
POST /ask
GET  /docs
GET  /openapi.json
```

### Streamlit Frontend

A separate Streamlit interface provides a conversational UI for interacting with the FastAPI backend.

```text
Streamlit UI
     ↓
API Client
     ↓
FastAPI Backend
     ↓
RAG Pipeline
```

The Streamlit frontend can communicate with either a local FastAPI instance or a deployed Cloud Run backend using:

```text
API_BASE_URL
```

---

## 🔌 API Usage

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "PDF Q&A Chatbot API",
  "version": "1.0.0"
}
```

### Ask a Question

```http
POST /ask
Content-Type: application/json
```

Request:

```json
{
  "question": "What are the standard working hours?"
}
```

Representative response:

```json
{
  "answer": "Standard working hours are 9:00 AM to 6:00 PM, Monday through Friday.",
  "confidence": 1.0,
  "citations": [
    {
      "file": "employee_handbook_detailed.pdf",
      "page": 2
    }
  ],
  "metadata": {
    "retrieved_documents": 3,
    "llm_model": "gemini-3.5-flash",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
  }
}
```

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| API | FastAPI |
| UI | Streamlit |
| RAG Framework | LangChain |
| Vector Database | ChromaDB |
| Lexical Retrieval | BM25 |
| Embeddings | Hugging Face Sentence Transformers |
| Reranking | Cross-Encoder |
| Production LLM | Gemini 3.5 Flash |
| Alternative LLM | Ollama |
| Validation / Settings | Pydantic |
| Containerization | Docker |
| Cloud Platform | Google Cloud |
| Compute | Cloud Run |
| Container Registry | Artifact Registry |
| Secrets | Secret Manager |
| Testing | Pytest |

---

## 📁 Project Structure

```text
pdf-qa-chatbot-clean/
│
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── README.md
│
├── documents/
│   └── PDF source documents
│
├── models/
│   ├── embedding/
│   │   └── all-MiniLM-L6-v2/
│   │
│   └── reranker/
│       └── ms-marco-MiniLM-L-6-v2/
│
├── vectordb/
│   └── ChromaDB persistence
│
├── src/
│   ├── api/
│   ├── core/
│   ├── services/
│   └── ...
│
├── tests/
│
└── ui/
    ├── app.py
    ├── api_client.py
    └── config.py
```

---

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd pdf-qa-chatbot-clean
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env` from `.env.example` and configure the required values.

Do not commit API keys or other secrets.

---

## ▶️ Run the FastAPI Backend

Start the backend with:

```bash
uvicorn app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## 🖥️ Run the Streamlit UI

Start the frontend with:

```bash
streamlit run ui/app.py
```

By default, the UI communicates with:

```text
http://127.0.0.1:8000
```

To connect the UI to a deployed backend, configure:

```text
API_BASE_URL=<your-cloud-run-backend-url>
```

---

## 🐳 Docker

The backend is containerized using Docker.

Build the image:

```bash
docker build -t pdf-qa-chatbot-backend .
```

Run locally:

```bash
docker run --env-file .env -p 8000:8000 pdf-qa-chatbot-backend
```

The container exposes:

```text
Port 8000
```

---

## ☁️ Cloud Deployment Architecture

The production backend is deployed using:

```text
Google Cloud
     │
     ├── Cloud Run
     │      └── FastAPI RAG Backend
     │
     ├── Artifact Registry
     │      └── Docker Images
     │
     ├── Secret Manager
     │      └── GOOGLE_API_KEY
     │
     └── Gemini API
            └── Gemini 3.5 Flash
```

The application container is designed to run without downloading the embedding and reranker models at startup.

---

## 🔐 Configuration & Secrets

Configuration is managed through environment variables.

Key configuration values include:

```text
EMBEDDING_MODEL
LLM_PROVIDER
LLM_MODEL
GOOGLE_API_KEY
AWS_REGION    # retained for optional AWS Bedrock provider support
OLLAMA_BASE_URL
TEMPERATURE
TOP_K
RELEVANCE_THRESHOLD
MAX_HISTORY_MESSAGES
CHUNK_SIZE
CHUNK_OVERLAP
LOG_FULL_PROMPT
COLLECTION_NAME
```

Sensitive values such as API keys should be stored outside source control.

For production deployment, secrets are supplied through Google Cloud Secret Manager.

---

## 🧪 Testing & Verification

The project includes automated tests covering core application functionality.

The system has been verified across multiple layers, including:

```text
✓ Embedding model loading
✓ Cross-Encoder model loading
✓ Document retrieval
✓ Vector retrieval
✓ BM25 retrieval
✓ Hybrid retrieval
✓ Reranking
✓ Retrieval confidence gating
✓ Query rewriting
✓ Conversation-aware RAG
✓ FastAPI API endpoints
✓ Request validation
✓ Docker image build
✓ Production container startup
✓ Cloud Run deployment
✓ Production health endpoint
✓ Production question answering
✓ Production logging
✓ Gemini generation
```

Production verification included successful requests through the deployed Cloud Run API and validation of the resulting RAG pipeline logs.

---

## 📊 Production Configuration

The deployed backend uses production-oriented Cloud Run configuration including:

```text
CPU:                2
Memory:             4 GiB
Request Timeout:    300 seconds
Concurrency:        160
Maximum Instances:  10
Startup CPU Boost:  Enabled
Traffic:            100% to latest ready revision
```

These values are deployment configuration choices and can be adjusted according to workload and cost requirements.

---

## 🔍 Example RAG Flow

For a question such as:

```text
"What are the standard working hours?"
```

the system processes the request approximately as follows:

```text
1. Receive user question
          ↓
2. Analyze / rewrite query
          ↓
3. Retrieve semantically similar chunks
          ↓
4. Retrieve lexical matches using BM25
          ↓
5. Combine retrieval results
          ↓
6. Rerank candidates using Cross-Encoder
          ↓
7. Calculate retrieval confidence
          ↓
8. Apply confidence gate
          ↓
9. Build grounded context
          ↓
10. Generate answer using Gemini
          ↓
11. Return answer + citations + metadata
```

---

## 🧩 Engineering Design Principles

The project was designed around several principles:

### Grounded Generation

The LLM should generate answers from retrieved document context rather than blindly relying on model knowledge.

### Retrieval Before Generation

Retrieval quality is treated as a first-class component of the system.

### Multiple Retrieval Signals

Semantic and lexical retrieval complement one another.

### Reranking

Initial retrieval candidates are refined using a Cross-Encoder before context construction.

### Confidence-Aware Generation

The system introduces a retrieval confidence gate instead of assuming every retrieval result is reliable enough for generation.

### Provider Abstraction

The LLM layer is separated from the rest of the application to allow provider flexibility.

### Production Reproducibility

Retrieval models are bundled into the container so production startup does not depend on downloading them dynamically.

### Separation of Concerns

The project separates:

```text
API
Core RAG Logic
Services
UI
Configuration
Tests
Infrastructure
```

---

## 📈 What This Project Demonstrates

This project demonstrates practical experience with:

- Retrieval-Augmented Generation
- LLM application architecture
- Semantic search
- Vector databases
- BM25 / lexical retrieval
- Hybrid retrieval
- Cross-Encoder reranking
- Retrieval confidence estimation
- Query rewriting
- Multi-turn conversational retrieval
- Prompt/context construction
- FastAPI API development
- Streamlit application development
- Docker containerization
- Cloud Run deployment
- Artifact Registry
- Secret management
- Production logging
- API validation
- Automated testing
- Production verification

---

## 🔮 Future Improvements

Potential future improvements include:

- Automated RAG evaluation pipelines
- Retrieval quality metrics
- Answer faithfulness evaluation
- Latency and cost dashboards
- Distributed observability
- Authentication and authorization
- Persistent production conversation storage
- Document upload and ingestion APIs
- CI/CD automation
- Automated model/version management
- Horizontal scaling optimization
- Advanced evaluation datasets

---

## 📌 Project Status

**Production RAG backend deployed and verified on Google Cloud Run.**

Current production LLM:

```text
Gemini 3.5 Flash
```

Current retrieval stack:

```text
Vector Search
+
BM25
+
Cross-Encoder Reranking
+
Retrieval Confidence Gate
```

Application interfaces:

```text
FastAPI Backend
+
Streamlit UI
```

---

## 📄 License

MIT
