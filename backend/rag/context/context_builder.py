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
context_builder.py

Combines semantic log retrieval, related log retrieval,
and security knowledge retrieval into a single RAGContext.
"""

from .context import RAGContext
from backend.rag.retriever.related_log_retriever import RelatedLogRetriever


class ContextBuilder:
    def __init__(
        self,
        log_retriever=None,
        knowledge_retriever=None,
        related_log_retriever=None,
        top_k_logs=3,
        top_k_knowledge=3,
    ):
        self.log_retriever = log_retriever
        self.knowledge_retriever = knowledge_retriever
        self.related_log_retriever = related_log_retriever
        self.top_k_logs = top_k_logs
        self.top_k_knowledge = top_k_knowledge

    def build(
        self,
        query,
        source_id=None,
        ):
        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        query = query.strip()

        if not query:
            raise ValueError("query cannot be empty.")

        context = RAGContext(query=query)

        semantic_results = None

        if self.log_retriever is not None:
            semantic_results = self.log_retriever.retrieve(
                query=query,
                top_k=self.top_k_logs,
                source_id=source_id,
            )

            self._add_results(
                context,
                semantic_results,
                result_type="log",
            )

        if self.related_log_retriever is not None and semantic_results:
            related_results = self.related_log_retriever.retrieve(
                semantic_results
            )

            semantic_ids = {
                result.get("id")
                for result in self._convert_results(semantic_results)
                if result.get("id") is not None
            }

            for result in related_results:
                if result.get("id") in semantic_ids:
                    continue

                context.add_related_log_result(result)

        if self.knowledge_retriever is not None:
            knowledge_results = self.knowledge_retriever.retrieve(
                query=query,
                top_k=self.top_k_knowledge,
            )

            self._add_results(
                context,
                knowledge_results,
                result_type="knowledge",
            )

        context.metadata = {
            "log_count": context.log_count(),
            "related_log_count": context.related_log_count(),
            "knowledge_count": context.knowledge_count(),
            "top_k_logs": self.top_k_logs,
            "top_k_knowledge": self.top_k_knowledge,
        }

        return context

    def _add_results(self, context, results, result_type):
        if not results:
            return

        ids = results.get("ids", [[]])
        documents = results.get("documents", [[]])
        metadatas = results.get("metadatas", [[]])
        distances = results.get("distances", [[]])

        ids = ids[0] if ids else []
        documents = documents[0] if documents else []
        metadatas = metadatas[0] if metadatas else []
        distances = distances[0] if distances else []

        count = len(documents)

        for index in range(count):
            result = {
                "id": (
                    ids[index]
                    if index < len(ids)
                    else None
                ),
                "document": documents[index],
                "metadata": (
                    metadatas[index]
                    if index < len(metadatas)
                    else {}
                ),
                "distance": (
                    distances[index]
                    if index < len(distances)
                    else None
                ),
            }

            if result_type == "log":
                context.add_log_result(result)

            elif result_type == "knowledge":
                context.add_knowledge_result(result)

    def _convert_results(self, results):
        ids = results.get("ids", [])
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        distances = results.get("distances", [])

        if ids and isinstance(ids[0], list):
            ids = ids[0]

        if documents and isinstance(documents[0], list):
            documents = documents[0]

        if metadatas and isinstance(metadatas[0], list):
            metadatas = metadatas[0]

        if distances and isinstance(distances[0], list):
            distances = distances[0]

        records = []

        count = max(
            len(ids),
            len(documents),
            len(metadatas),
        )

        for index in range(count):
            records.append(
                {
                    "id": (
                        ids[index]
                        if index < len(ids)
                        else None
                    ),
                    "document": (
                        documents[index]
                        if index < len(documents)
                        else None
                    ),
                    "metadata": (
                        metadatas[index]
                        if index < len(metadatas)
                        else {}
                    ),
                    "distance": (
                        distances[index]
                        if index < len(distances)
                        else None
                    ),
                }
            )

        return records

    def info(self):
        return {
            "top_k_logs": self.top_k_logs,
            "top_k_knowledge": self.top_k_knowledge,
            "has_log_retriever": (
                self.log_retriever is not None
            ),
            "has_related_log_retriever": (
                self.related_log_retriever is not None
            ),
            "has_knowledge_retriever": (
                self.knowledge_retriever is not None
            ),
        }

    def __repr__(self):
        return (
            f"ContextBuilder("
            f"top_k_logs={self.top_k_logs}, "
            f"top_k_knowledge={self.top_k_knowledge}, "
            f"related_log_retrieval="
            f"{self.related_log_retriever is not None})"
        )
