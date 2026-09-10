"""
prompt_builder.py

Builds structured security-analysis prompts from
RAG context using configurable prompts.
"""

from backend.rag.context import RAGContext
from backend.rag.context import ContextFormatter
from backend.config.prompts_config import PromptsConfig


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
""".strip()

        return prompt

    # ----------------------------------------------------------
    # Short Prompt
    # ----------------------------------------------------------

    def build_analysis_prompt(self, context):
        """
        Build a concise analysis prompt.

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
            "Identify the potential threat, supporting "
            "evidence, severity, and recommended actions. "
            "Do not invent information."
        )

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