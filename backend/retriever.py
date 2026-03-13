from typing import List, Tuple
import numpy as np
from embeddings import EmbeddingGenerator
from vector_store import VectorStore


class Retriever:
    """
    Docstring for Retriever

    Retrieval module for rag
    when you give a query, it retrieves top-k relevant clauses from the vector_store
    """

    def __init__(
            self,
            embedding_generator: EmbeddingGenerator,
            vector_store: VectorStore,
            top_k: int=5
    ):
        """
        Docstring for __init__
        
        :param self: Description
        :param embedding_generator: Description
        :type embedding_generator: EmbeddingGenerator
        :param vector_store: Description
        :type vector_store: VectorStore
        :param top_k: Description
        :type top_k: int
        """

        self.embedding_generator=embedding_generator
        self.vector_store=vector_store
        self.top_k=top_k

    def retrieve(self, query_text: str) -> List[Tuple[str, float]]:
        """
        Docstring for retrieve
        
        :param self: Description
        :param query_text: Description
        :type query_text: str
        :return: Description
        :rtype: List[Tuple[str, float]]
        """

        # step 1 : In this first we will generate the embedding for the query

        query_embedding=self.embedding_generator.embed_single_text(query_text)

        #step 2: search faiss index for top-k similar clauses

        results=self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k
        )

        return results