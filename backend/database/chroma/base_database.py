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
base_database.py

Defines the base interface for vector databases.
"""


from abc import ABC, abstractmethod


class BaseVectorDatabase(ABC):
    """
    Abstract interface for vector database implementations.
    """

    @abstractmethod
    def add(
        self,
        ids,
        embeddings,
        documents=None,
        metadatas=None,
    ):
        """
        Add vectors and associated data.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_embedding,
        n_results=5,
    ):
        """
        Search for vectors similar to a query embedding.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, ids):
        """
        Delete vectors by ID.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self):
        """
        Return the number of stored vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        """
        Remove all vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """
        Close the database connection.
        """
        raise NotImplementedError
