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

Complete every section of the security assessment.

THREAT ASSESSMENT
Provide a detailed assessment of whether the retrieved
evidence indicates a potential security threat. Explain
the conclusion and the level of confidence supported by
the evidence.

EVIDENCE
List the important observations from the retrieved logs.
Include relevant timestamps, users, source identifiers,
event types, processes, authentication activity, or other
details when they are present in the retrieved evidence.
Do not invent missing details.

SECURITY INTERPRETATION
Provide a detailed explanation of what the observed events
may indicate. Connect the evidence to the security query.
Clearly distinguish observed facts from security
interpretation.

SEVERITY
Provide one of:
LOW, MEDIUM, HIGH, or CRITICAL.

Explain why the selected severity is appropriate based only
on the retrieved evidence.

RECOMMENDED ACTIONS
Provide several practical actions that could help
investigate, contain, monitor, or mitigate the potential
threat. Actions should be relevant to the observed evidence.

LIMITATIONS
Clearly explain what the retrieved evidence does not prove.
If the evidence is insufficient to confirm the suspected
activity, state this explicitly and identify what additional
evidence would be useful.

IMPORTANT:
- Complete all six sections.
- Do not omit any section.
- Do not provide only a short summary.
- Use the retrieved evidence as the basis for every claim.
- Do not invent IP addresses, usernames, timestamps,
  processes, events, attack details, or other facts.
- Clearly distinguish evidence from interpretation.
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