# Insurance Document Analyzer

AI-powered compliance analysis for Indian motor insurance documents.  
Upload a policy (PDF or image) and get instant compliance checks against the **Motor Vehicles Act 1988** and **IRDAI regulations**.

---

## Features

- **OCR Pipeline** — Extracts text from PDFs and images (PyMuPDF + Tesseract with table-aware preprocessing)
- **RAG Retrieval** — Semantic search over Indian insurance laws using FAISS + Sentence Transformers
- **LLM Reasoning** — Groq-hosted Llama 3.1 8B assesses compliance with low hallucination (temperature 0.1, strict JSON output)
- **Hallucination Filtering** — Validates LLM-flagged clauses against the original document
- **Structured Output** — Confidence score, severity-ranked flagged clauses, pricing/legal/coverage assessments

## Tech Stack

| Component        | Technology                                |
|------------------|-------------------------------------------|
| Backend API      | FastAPI + Uvicorn                         |
| OCR              | PyMuPDF + Tesseract + OpenCV              |
| Embeddings       | Sentence Transformers (all-MiniLM-L6-v2)  |
| Vector Store     | FAISS (cosine similarity)                 |
| LLM              | Groq API (Llama 3.1 8B Instant)           |
| Frontend         | HTML5 + Tailwind CSS v3 + Vanilla JS      |

## Project Structure

```
Insurance-Document-Analyzer/
├── backend/
│   ├── main.py            # FastAPI app + endpoint
│   ├── ocr.py             # Text extraction (PDF + image)
│   ├── chunker.py         # Section-based document chunking
│   ├── embeddings.py      # Sentence Transformer embeddings
│   ├── vector_store.py    # FAISS vector store
│   ├── retriever.py       # RAG retrieval module
│   ├── llm_engine.py      # Groq LLM integration
│   ├── compliance.py      # Compliance assessment engine
│   ├── load_laws.py       # Law document indexing
│   ├── data/laws/         # Indian insurance legal texts
│   └── requirements.txt
├── frontend/
│   ├── index.html         # Single-page application
│   ├── styles.css         # Custom styles + animations
│   └── app.js             # API integration + rendering
└── README.md
```

## Setup

### Prerequisites
- Python 3.9+
- Tesseract OCR installed ([install guide](https://github.com/tesseract-ocr/tesseract))
- Groq API key ([get one free](https://console.groq.com))

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### Frontend

Simply open `frontend/index.html` in your browser.  
Make sure the backend server is running on `localhost:8000`.

## API

### `POST /analyze-document/`

Upload a file (PDF/PNG/JPG/TIFF) as multipart form data.

**Response:**
```json
{
  "confidence_score": 72,
  "final_compliance_status": "Compliant",
  "compliance_ratio": 0.80,
  "summary": {
    "pricing": "Premium structure aligns with IRDAI guidelines.",
    "legal": "Policy adheres to Motor Vehicles Act requirements.",
    "coverage": "Third party liability coverage meets minimum requirements."
  },
  "flagged_clauses": [
    {
      "clause_text": "No refund of premium will be provided if cancellation is initiated by the insured.",
      "issue": "Blanket no-refund clause may violate IRDAI policyholder protection regulations.",
      "severity": "medium"
    }
  ],
  "total_sections": 14,
  "analyzed_sections_count": 5,
  "analyzed_sections": [...]
}
```

## License

This project is for academic/demonstration purposes.