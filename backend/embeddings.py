from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    """
    Generates semantic embeddings for text chunks. """

    def __init__(self, model_name: str="sentence-transformers/all-MiniLM-L6v2"):
        """
        Load Embedding model once.
        """

        self.model=SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """

        convert a list of text chunks into embeddings
        
        """

        embeddings=self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings
    
    def embed_single_text(self, text:str) -> np.ndarray:
       """
       generate embedding for a single text.
       """

       embedding=self.model.encode(
           text,
           convert_to_numpy=True,
           normalize_embeddings=True
       )

       return embedding