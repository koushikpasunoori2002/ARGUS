"""
rag_analyzer.py

Performs security analysis using retrieved RAG context
and the configured local LLM.
"""

from backend.llm.generation.llm_client import LLMClient
from backend.llm.generation.prompt_builder import PromptBuilder
from backend.llm.generation.response import LLMResponse


class RAGAnalyzer:
    """
    Generates security analysis responses from RAG context.
    """

    def __init__(
        self,
        llm_client=None,
        prompt_builder=None,
    ):
        self.llm_client = (
            llm_client
            if llm_client is not None
            else LLMClient()
        )

        self.prompt_builder = (
            prompt_builder
            if prompt_builder is not None
            else PromptBuilder()
        )

    def analyze(self, context):
        """
        Generate an analysis response from the supplied RAG context.
        """

        if context is None:
            raise ValueError("context cannot be None.")

        prompt = self.prompt_builder.build(context)

        result = self.llm_client.generate(prompt)

        if isinstance(result, LLMResponse):
            response = result
        else:
            response = LLMResponse(
                query=context.query,
                answer=str(result),
                model=getattr(
                    self.llm_client,
                    "model",
                    "unknown",
                ),
            )

        response.query = context.query

        response.metadata.update(
            {
                "rag": True,
                "log_results": context.log_count(),
                "related_log_results": (
                    context.related_log_count()
                ),
                "knowledge_results": (
                    context.knowledge_count()
                ),
            }
        )

        return response

    def analyze_structured(self, context):
        """
        Generate and parse a structured security analysis.
        """

        response = self.analyze(context)

        from backend.llm.analysis.analysis_parser import (
            AnalysisParser,
        )

        parser = AnalysisParser()

        analysis = parser.parse(
            response.answer
        )

        analysis.metadata.update(
            {
                "query": context.query,
                "log_results": context.log_count(),
                "related_log_results": (
                    context.related_log_count()
                ),
                "knowledge_results": (
                    context.knowledge_count()
                ),
                "model": response.model,
            }
        )

        return analysis

    def info(self):
        """
        Return analyzer configuration information.
        """

        return {
            "analyzer": self.__class__.__name__,
            "llm_client": self.llm_client.__class__.__name__,
            "prompt_builder": (
                self.prompt_builder.__class__.__name__
            ),
        }

    def __repr__(self):
        return (
            f"RAGAnalyzer("
            f"llm_client={self.llm_client.__class__.__name__}, "
            f"prompt_builder={self.prompt_builder.__class__.__name__})"
        )