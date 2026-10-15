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
knowledge_document.py

Defines a security knowledge document used by
the ARGUS knowledge base.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class KnowledgeDocument:
    """
    Represents a single security knowledge document.
    """

    document_id: str
    text: str
    source: str
    category: str
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):
        """
        Convert the knowledge document to a dictionary.
        """

        return {
            "document_id": self.document_id,
            "text": self.text,
            "source": self.source,
            "category": self.category,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a KnowledgeDocument from a dictionary.
        """

        return cls(
            document_id=data.get(
                "document_id",
                "",
            ),
            text=data.get(
                "text",
                "",
            ),
            source=data.get(
                "source",
                "",
            ),
            category=data.get(
                "category",
                "",
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    def __len__(self):
        """
        Return the length of the document text.
        """

        return len(self.text)

    def __str__(self):

        return (
            f"Knowledge Document\n"
            f"ID       : {self.document_id}\n"
            f"Source   : {self.source}\n"
            f"Category : {self.category}\n"
            f"Length   : {len(self.text)} characters\n"
            f"Metadata : {self.metadata}\n"
            f"Text     : {self.text}"
        )

    def __repr__(self):

        return (
            f"KnowledgeDocument("
            f"document_id='{self.document_id}', "
            f"source='{self.source}', "
            f"category='{self.category}', "
            f"length={len(self.text)})"
        )
