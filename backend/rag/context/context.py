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
context.py

Defines the structured context passed from the RAG
retrieval layer to the LLM layer.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RAGContext:
    """
    Structured context containing retrieved evidence and
    related log records for security analysis.
    """

    query: str

    log_results: List[Dict[str, Any]] = field(
        default_factory=list
    )

    related_log_results: List[Dict[str, Any]] = field(
        default_factory=list
    )

    knowledge_results: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_log_result(
        self,
        result: Dict[str, Any],
    ) -> None:
        """Add a semantic log retrieval result."""

        self.log_results.append(result)

    def add_related_log_result(
        self,
        result: Dict[str, Any],
    ) -> None:
        """Add a related log retrieval result."""

        self.related_log_results.append(result)

    def add_knowledge_result(
        self,
        result: Dict[str, Any],
    ) -> None:
        """Add a security knowledge retrieval result."""

        self.knowledge_results.append(result)

    def log_count(self) -> int:
        """Return the number of semantic log results."""

        return len(self.log_results)

    def related_log_count(self) -> int:
        """Return the number of related log results."""

        return len(self.related_log_results)

    def knowledge_count(self) -> int:
        """Return the number of security knowledge results."""

        return len(self.knowledge_results)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the context into a dictionary."""

        return {
            "query": self.query,
            "log_results": self.log_results,
            "related_log_results": self.related_log_results,
            "knowledge_results": self.knowledge_results,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return (
            "RAGContext\n"
            f"Query              : {self.query}\n"
            f"Log Results        : {self.log_count()}\n"
            f"Related Log Results: {self.related_log_count()}\n"
            f"Knowledge Results  : {self.knowledge_count()}\n"
            f"Metadata           : {self.metadata}"
        )

    def __repr__(self) -> str:
        return (
            f"RAGContext("
            f"query='{self.query}', "
            f"logs={self.log_count()}, "
            f"related_logs={self.related_log_count()}, "
            f"knowledge={self.knowledge_count()}"
            f")"
        )
