# Retrieval Augmented Generation System for Researchers

## Description

This RAG system is designed to assist researchers in efficiently writing literature reviews and answering research-specific questions.

The system uses **FastAPI** as the backend for handling API requests, **Streamlit** for the frontend interface, and integrates several libraries for embeddings, vector storage and model calling.

## Tech Stack

- **Python 3.12**
- **FastAPI** - Backend API for handling user queries and returning AI-generated responses.
- **Streamlit** - Web-based frontend for interacting with the RAG system.
- **ChromaDB** - Vector database for document embeddings.
- **Groq API** - For accessing pre-trained text generation language models.
- **llama-index** - For document indexing and querying.
- **HuggingFace** - For embeddings via the HuggingFace embedding model.

## How to run locally

### Prerequisites

- Install **Python 3.12**.
- Install dependencies using `pip install -r requirements.txt`.
- Set up your **Groq API key** as an environment variable.

### 1. Fastapi

cd to Folder

run uvicorn app:app --host 127.0.0.1 --port 8000 --reload

### 2. Streamlit

- FastAPI must be running locally for Streamlit to function.
- Run the Streamlit app
  `streamlit run main.py`