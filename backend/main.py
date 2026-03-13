from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from ocr import extract_text
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from retriever import Retriever
from llm_engine import LLMEngine
from compliance import ComplianceEngine
from load_laws import load_and_index_laws

# Load environment variables from .env (requires python-dotenv in requirements)
from dotenv import load_dotenv
load_dotenv()

import uvicorn

# ----------------- FASTAPI INIT -----------------

app = FastAPI(title="Insurance Document Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- GLOBAL COMPONENTS -----------------

# embedding model

embedder=EmbeddingGenerator()

# vector store(faiss)
EMBEDDING_DIM=384
vector_store=VectorStore(embedding_dim=EMBEDDING_DIM)

# load & index laws once at startup
load_and_index_laws(
    laws_dir="data/laws",
    vector_store=vector_store,
    embedder=embedder

)
# retriever
retriever=Retriever(
    embedding_generator=embedder,
    vector_store=vector_store, 
    top_k=1
)

#llm engine
llm_engine=LLMEngine()

# compliance engine
compliance_engine=ComplianceEngine(
    retriever=retriever,
    llm_engine=llm_engine
)

# ----------------- API ENDPOINTS -----------------

@app.post("/analyze-document/")
async def analyze_document(file: UploadFile = File(...)):
    """
    Docstring for analyze_document
    Analyzes the uploaded insurance document for compliance with legal regulations.
    """

    try:
        file_bytes=await file.read()
        
        if not file_bytes:
            return {"error": "Empty file uploaded"}

        # step 1: extract text via OCR
        document_text=extract_text(file_bytes, file.filename)
        
        if not document_text or not document_text.strip():
            return {"error": "No text could be extracted from the document"}

        # step 2: analyze compliance
        result=compliance_engine.analyze_document(document_text)

        return result
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
