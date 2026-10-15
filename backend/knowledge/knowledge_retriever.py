# ARGUS: An LLM-RAG Guided Unified Reasoning System for Security Operational Centres
# Copyright 2026 Koushik Pasunoori and Dr Jose Maria Alcaraz Calero
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
knowledge_retriever.py

Retrieves relevant security knowledge from the
knowledge vector database.
"""

from backend.llm.embeddings import EmbeddingManager


class KnowledgeRetriever:
    """
    Retrieves security knowledge using semantic similarity.
    """

    def __init__(
        self,
        database,
        embedding_manager=None,
        top_k=3,
    ):
        """
        Initialize the knowledge retriever.

        Parameters
        ----------
        database : ChromaDatabase
            Knowledge vector database.

        embedding_manager : EmbeddingManager, optional
            Embedding model used for queries.

        top_k : int
            Number of results to retrieve.
        """

        self.database = database

        self.embedding_manager = (
            embedding_manager
            if embedding_manager is not None
            else EmbeddingManager()
        )

        self.top_k = top_k

    # ----------------------------------------------------------
    # Retrieve
    # ----------------------------------------------------------

    def retrieve(
        self,
        query,
        top_k=None,
    ):
        """
        Retrieve relevant security knowledge.

        Parameters
        ----------
        query : str
            Security question or search query.

        top_k : int, optional
            Number of results.

        Returns
        -------
        dict
            ChromaDB search results.
        """

        if not isinstance(query, str):

            raise TypeError(
                "query must be a string."
            )

        query = query.strip()

        if not query:

            raise ValueError(
                "query cannot be empty."
            )

        if top_k is None:

            top_k = self.top_k

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than zero."
            )

        query_embedding = (
            self.embedding_manager.embed_text(
                query
            )
        )

        results = self.database.search(
            query_embedding=query_embedding,
            n_results=top_k,
        )

        return results

    # ----------------------------------------------------------
    # Retrieve with scores
    # ----------------------------------------------------------

    def retrieve_with_scores(
        self,
        query,
        top_k=None,
    ):
        """
        Retrieve knowledge together with similarity
        distances.
        """

        return self.retrieve(
            query=query,
            top_k=top_k,
        )

    # ----------------------------------------------------------
    # Information
    # ----------------------------------------------------------

    def info(self):
        """
        Return retriever information.
        """

        return {
            "component": "KnowledgeRetriever",
            "top_k": self.top_k,
            "database": self.database.info(),
            "embedding_model": (
                self.embedding_manager
                .model_information()
            ),
        }

    def close(self):
        """
        Close the underlying database.
        """

        self.database.close()

    def __repr__(self):

        return (
            f"KnowledgeRetriever("
            f"top_k={self.top_k})"
        )
