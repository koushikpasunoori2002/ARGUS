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
embedding_model.py

Loads and manages the sentence embedding model.
"""

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Wrapper around a SentenceTransformer model.
    """

    def __init__(
        self,
        model_name="all-MiniLM-L6-v2",
    ):
        """
        Load the embedding model.
        """

        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name
        )

    def encode(
        self,
        text,
        normalize_embeddings=True,
    ):
        """
        Generate an embedding for a single text.
        """

        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=normalize_embeddings,
        )

    def encode_batch(
        self,
        texts,
        normalize_embeddings=True,
    ):
        """
        Generate embeddings for multiple texts.
        """

        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=normalize_embeddings,
        )

    def dimension(self):
        """
        Return embedding vector size.
        """

        return self.model.get_embedding_dimension()
    def model_info(self):
        """
        Return model information.
        """

        return {
            "model": self.model_name,
            "dimension": self.dimension(),
        }

    def __repr__(self):

        return (
            f"EmbeddingModel("
            f"model='{self.model_name}')"
        )
