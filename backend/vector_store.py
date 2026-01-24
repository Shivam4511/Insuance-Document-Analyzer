import faiss
import numpy as np
from typing import List,Tuple

class VectorStore:
    """
    A simple vector store using FAISS for semantic search.
    """

    def __init__(self, embedding_dim: int):
        """
        Docstring for __init__
        
        :param self: Description
        :param embedding_dim: Description
        :type embedding_dim: int
        """
        self.embedding_dim=embedding_dim

        #cosine similarity = Inner Porduct on normalized vectors

        self.index=faiss.IndexFlatIP(embedding_dim)

        self.text_chunks: List[str]=[]
    
    def add_embeddings(self, embeddings: np.ndarray, texts: List[str]):
        """
        Docstring for add_embeddings
        """

        if embeddings.shape[1]!=self.embedding_dim:

            raise ValueError("Embedding dimension mismatch.")
        
        self.index.add(embeddings)
        self.text_chunks.extend(texts)

    def search(self, query_embedding: np.ndarray, top_k: int=5) -> List[Tuple[str, float]]:
        """
        Docstring for search

        :param query_embedding: The embedding of the query.
        :param top_k: The number of top results to return.
        :return: A list of tuples (text_chunk, similarity_score).
        """

        if query_embedding.ndim == 1:
            query_embedding=query_embedding.reshape(1, -1)

        scores, indices=self.index.search(query_embedding, top_k)

        results=[]

        for idx, score in zip(indices[0], scores[0]):

            if idx==-1:
                continue
            results.append((self.text_chunks[idx], float(score)))

        return results