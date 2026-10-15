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
embedding_manager.py

Manages embedding generation for text and Chunk objects.
"""

import numpy as np

from .embedding_model import EmbeddingModel


class EmbeddingManager:
    """
    High-level interface for embedding generation.
    """

    def __init__(
        self,
        model_name="all-MiniLM-L6-v2",
    ):

        self.model = EmbeddingModel(model_name)

    def embed_text(self, text):
        """
        Generate an embedding for a single text.
        """

        return self.model.encode(text)

    def embed_texts(self, texts):
        """
        Generate embeddings for multiple texts.
        """

        return self.model.encode_batch(texts)

    def embed_chunk(self, chunk):
        """
        Generate an embedding for a Chunk object.
        """

        return self.model.encode(chunk.text)

    def embed_chunks(self, chunks):
        """
        Generate embeddings for multiple Chunk objects.
        """

        texts = [
            chunk.text
            for chunk in chunks
        ]

        return self.model.encode_batch(texts)

    def cosine_similarity(
        self,
        embedding1,
        embedding2,
    ):
        """
        Compute cosine similarity between two embeddings.
        """

        embedding1 = np.asarray(embedding1)
        embedding2 = np.asarray(embedding2)

        return float(
            np.dot(embedding1, embedding2)
            /
            (
                np.linalg.norm(embedding1)
                *
                np.linalg.norm(embedding2)
            )
        )

    def embedding_dimension(self):
        """
        Return the embedding vector dimension.
        """

        return self.model.dimension()

    def model_information(self):
        """
        Return information about the loaded model.
        """

        return self.model.model_info()

    def __repr__(self):

        return (
            f"EmbeddingManager("
            f"model={self.model.model_name})"
        )
