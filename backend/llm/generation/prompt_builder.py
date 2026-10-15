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
prompt_builder.py

Builds structured security-analysis prompts from
RAG context using configurable prompts.
"""

from backend.config.prompts_config import PromptsConfig
from backend.rag.context import ContextFormatter
from backend.rag.context import RAGContext


class PromptBuilder:
    """
    Builds prompts for local LLM security analysis.
    """

    def __init__(
        self,
        formatter=None,
        prompts_config=None,
    ):
        self.formatter = (
            formatter
            if formatter is not None
            else ContextFormatter()
        )

        self.prompts_config = (
            prompts_config
            if prompts_config is not None
            else PromptsConfig()
        )

    # ----------------------------------------------------------
    # Build Security Analysis Prompt
    # ----------------------------------------------------------

    def build(self, context):
        """
        Build a complete security-analysis prompt.
        """

        if not isinstance(
            context,
            RAGContext,
        ):
            raise TypeError(
                "context must be a RAGContext."
            )

        retrieved_context = (
            self.formatter.format(context)
        )

        configured_template = (
            self.prompts_config.get_template(
                "security_analysis"
            )
        )

        prompt = f"""
{configured_template}

Analyse the following security query:

{context.query}

Retrieved evidence:

{retrieved_context}


        IMPORTANT OUTPUT REQUIREMENTS:

        Follow the configured security-analysis template above.
        Its rules take precedence over any general formatting
        instructions in this prompt.

        Analyse the specific security activity in the user's query.
        Prioritise directly relevant retrieved log events.
        Do not let unrelated security knowledge or less relevant
        events replace the primary finding.

        Complete all six required sections:
        THREAT ASSESSMENT
        EVIDENCE
        SECURITY INTERPRETATION
        SEVERITY
        RECOMMENDED ACTIONS
        LIMITATIONS

        Follow the configured template's exact requirements for
        the number of evidence items and recommended actions.
        Use only retrieved evidence for factual claims.
        Clearly distinguish observed facts from interpretation.
        Do not invent events, users, timestamps, processes,
        attack details, or other missing information.
""".strip()

        return prompt

    # ----------------------------------------------------------
    # Build Short Analysis Prompt
    # ----------------------------------------------------------

    def build_analysis_prompt(self, context):
        """
        Build a concise security-analysis prompt.

        This is useful when context length needs to be reduced.
        """

        if not isinstance(
            context,
            RAGContext,
        ):
            raise TypeError(
                "context must be a RAGContext."
            )

        retrieved_context = (
            self.formatter.format(context)
        )

        configured_template = (
            self.prompts_config.get_template(
                "security_analysis"
            )
        )

        return (
            f"{configured_template}\n\n"
            "Analyse the following security query "
            "using only the retrieved evidence.\n\n"
            f"QUERY:\n{context.query}\n\n"
            f"EVIDENCE:\n{retrieved_context}\n\n"
            "Provide the following sections:\n\n"
            "THREAT ASSESSMENT\n"
            "EVIDENCE\n"
            "SECURITY INTERPRETATION\n"
            "SEVERITY\n"
            "RECOMMENDED ACTIONS\n"
            "LIMITATIONS\n\n"
            "Complete every section. "
            "Use only the retrieved evidence. "
            "Do not invent information."
        )

    # ----------------------------------------------------------
    # Build Evidence Summary Prompt
    # ----------------------------------------------------------

    def build_evidence_summary_prompt(
        self,
        context,
    ):
        """
        Build a prompt for summarising retrieved evidence.
        """

        if not isinstance(
            context,
            RAGContext,
        ):
            raise TypeError(
                "context must be a RAGContext."
            )

        retrieved_context = (
            self.formatter.format(context)
        )

        configured_template = (
            self.prompts_config.get_template(
                "evidence_summary"
            )
        )

        return f"""
{configured_template}

USER QUERY:

{context.query}

RETRIEVED EVIDENCE:

{retrieved_context}
""".strip()

    # ----------------------------------------------------------
    # Information
    # ----------------------------------------------------------

    def info(self):
        """
        Return information about the prompt builder.
        """

        return {
            "component": "PromptBuilder",
            "purpose": "Security log analysis",
            "formatter": (
                self.formatter.__class__.__name__
            ),
            "prompt_config": (
                self.prompts_config.info()
            ),
        }

    def __repr__(self):
        return (
            "PromptBuilder("
            f"formatter="
            f"'{self.formatter.__class__.__name__}', "
            f"prompts_config="
            f"'{self.prompts_config.__class__.__name__}')"
        )
