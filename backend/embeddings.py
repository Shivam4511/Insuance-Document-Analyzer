from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    """
    Generates semantic embeddings for text chunks. """

    def __init__(self, model_name: str="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Load Embedding model once. If loading fails due to an invalid model id or
        authentication issue, a helpful OSError will be raised explaining how to
        fix it (check model name spelling or set HUGGINGFACE_HUB_TOKEN / run
        `huggingface-cli login`).
        """
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            # Provide a clearer, actionable error for common hub-related failures
            msg = (
                f"Failed to load model '{model_name}': {e}\n\n"
                "Possible causes:\n"
                "- Incorrect model identifier (try 'sentence-transformers/all-MiniLM-L6-v2' or 'all-MiniLM-L6-v2')\n"
                "- Private/gated model requiring authentication\n\n"
                "Fixes:\n"
                "- Set the environment variable HUGGINGFACE_HUB_TOKEN and restart (Windows):\n"
                "    set HUGGINGFACE_HUB_TOKEN=your_token\n"
                "- Or run 'huggingface-cli login' and authenticate locally.\n"
                "If you already have a token, ensure it is correct."
            )
            raise OSError(msg) from e

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