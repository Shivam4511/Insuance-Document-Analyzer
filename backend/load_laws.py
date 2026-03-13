from pathlib import Path
from typing import List

from chunker import chunk_document
from embeddings import EmbeddingGenerator
from vector_store import VectorStore


def load_and_index_laws(
    laws_dir: str,
    vector_store: VectorStore,
    embedder: EmbeddingGenerator
) -> None:
    """
    Docstring for load_and_index_laws

    Loads legal documents, chunks them, embeds them,
    and stores them in the FAISS vector store.

    This function should be called ONCE during app startup.
    """

    laws_path = Path(laws_dir)
    if not laws_path.exists():
        raise FileNotFoundError(f"Laws directory not found: {laws_dir}")

    all_law_chunks: List[str] = []

    # Read all law text files
    for law_file in laws_path.glob("*.txt"):
        with open(law_file, "r", encoding="utf-8") as f:
            law_text = f.read()

        # Chunk law text into semantically meaningful pieces
        chunks = chunk_document(law_text)
        all_law_chunks.extend(chunks)

    if not all_law_chunks:
        raise ValueError("No law text found to index.")

    # Generate embeddings for law chunks
    embeddings = embedder.embed_texts(all_law_chunks)

    # Store embeddings in FAISS
    vector_store.add_embeddings(embeddings, all_law_chunks)

    print(f"[INFO] Indexed {len(all_law_chunks)} legal clauses into FAISS.")
