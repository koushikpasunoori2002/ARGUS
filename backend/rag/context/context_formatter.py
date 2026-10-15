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
context_formatter.py

Formats RAGContext into concise structured text for the LLM.
"""


class ContextFormatter:
    """
    Formats retrieved RAG context for LLM analysis.
    """

    def format(self, context):
        sections = [
            self.format_query(context),
            self.format_logs(context),
            self.format_related_logs(context),
            self.format_knowledge(context),
            self.format_metadata(context),
        ]

        return "\n\n".join(sections)

    def format_query(self, context):
        return (
            "USER QUERY\n"
            "==========\n"
            f"{context.query}"
        )

    def format_logs(self, context):
        lines = [
            "RETRIEVED LOGS",
            "==============",
        ]

        if not context.log_results:
            lines.append(
                "No semantic log results were retrieved."
            )
            return "\n".join(lines)

        for index, result in enumerate(
            context.log_results,
            start=1,
        ):
            lines.extend(
                self._format_log(
                    result,
                    index,
                    "Log",
                )
            )

        return "\n".join(lines)

    def format_related_logs(self, context):
        lines = [
            "RELATED LOGS",
            "============",
        ]

        if not context.related_log_results:
            lines.append(
                "No related log results were retrieved."
            )
            return "\n".join(lines)

        for index, result in enumerate(
            context.related_log_results,
            start=1,
        ):
            lines.extend(
                self._format_log(
                    result,
                    index,
                    "Related Log",
                )
            )

        return "\n".join(lines)

    def _format_log(
        self,
        result,
        index,
        label,
    ):
        metadata = result.get(
            "metadata",
            {},
        )

        lines = [
            f"\n{label} {index}",
        ]
        self._add_field(
            lines,
            "Document",
            result.get("document"),
        )
        self._add_field(
            lines,
            "ID",
            result.get("id"),
        )

        self._add_field(
            lines,
            "Timestamp",
            metadata.get("timestamp"),
        )

        self._add_field(
            lines,
            "Source",
            metadata.get("source"),
        )

        self._add_field(
            lines,
            "Hostname",
            metadata.get("hostname"),
        )

        self._add_field(
            lines,
            "Process",
            metadata.get("process"),
        )

        self._add_field(
            lines,
            "Log Type",
            metadata.get("log_type"),
        )

        self._add_field(
            lines,
            "Severity",
            metadata.get("severity"),
        )

        self._add_field(
            lines,
            "Event",
            metadata.get("event"),
        )

        self._add_field(
            lines,
            "Event Type",
            metadata.get("event_type"),
        )

        self._add_field(
            lines,
            "User",
            metadata.get("user"),
        )

        self._add_field(
            lines,
            "IP",
            metadata.get("ip"),
        )

        self._add_field(
            lines,
            "Port",
            metadata.get("port"),
        )

        self._add_field(
            lines,
            "Message",
            metadata.get("message"),
        )

        return lines

    def _add_field(
        self,
        lines,
        name,
        value,
    ):
        if value is not None and value != "":
            lines.append(
                f"{name}: {value}"
            )

    def format_knowledge(self, context):
        lines = [
            "SECURITY KNOWLEDGE",
            "==================",
        ]

        if not context.knowledge_results:
            lines.append(
                "No security knowledge was retrieved."
            )
            return "\n".join(lines)

        for index, result in enumerate(
            context.knowledge_results,
            start=1,
        ):
            lines.append(
                f"\nKnowledge {index}"
            )

            self._add_field(
                lines,
                "ID",
                result.get("id"),
            )

            self._add_field(
                lines,
                "Document",
                result.get("document"),
            )

        return "\n".join(lines)

    def format_metadata(self, context):
        return (
            "CONTEXT METADATA\n"
            "================\n"
            f"Log count: {context.log_count()}\n"
            f"Related log count: "
            f"{context.related_log_count()}\n"
            f"Knowledge count: "
            f"{context.knowledge_count()}"
        )

    def info(self):
        return {
            "formatter": self.__class__.__name__,
            "sections": [
                "user_query",
                "retrieved_logs",
                "related_logs",
                "security_knowledge",
                "context_metadata",
            ],
        }

    def __repr__(self):
        return "ContextFormatter()"
