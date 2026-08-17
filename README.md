# 📄 PDF Q&A Chatbot (RAG)

A production-ready Retrieval-Augmented Generation (RAG) chatbot that answers questions from PDF documents using FastAPI, LangChain, ChromaDB, Hugging Face Embeddings, and Ollama.

## Features

- Ask questions from PDF documents
- Semantic search using vector embeddings
- Retrieval-Augmented Generation (RAG)
- FastAPI REST API
- Swagger UI documentation
- Source page citations
- Production-ready logging
- Exception handling
- Health monitoring endpoint

## Tech Stack

- Python
- FastAPI
- LangChain
- ChromaDB
- Hugging Face
- Ollama
- Pydantic

## Run the project

```bash
uvicorn src.api.main:app --reload
```

Open

```
http://127.0.0.1:8000/docs
```

to access the Swagger UI.

## Project Structure

```
src/
api/
core/
services/
documents/
vectordb/
```

## License

MIT