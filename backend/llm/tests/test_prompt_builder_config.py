"""
Tests for configurable prompt integration.
"""

from backend.llm.generation.prompt_builder import PromptBuilder


def test_prompt_builder_loads_configured_prompts():
    builder = PromptBuilder()

    info = builder.info()

    assert info["prompt_config"]["prompt_count"] == 2
    assert "security_analysis" in info["prompt_config"]["prompts"]
    assert "evidence_summary" in info["prompt_config"]["prompts"]


def test_security_analysis_template_is_used():
    builder = PromptBuilder()

    configured_template = (
        builder.prompts_config.get_template(
            "security_analysis"
        )
    )

    assert configured_template in (
        builder.build_analysis_prompt(
            _create_context()
        )
    )


def _create_context():
    from backend.rag.context import RAGContext

    return RAGContext(
        query="failed SSH authentication",
        log_results=[],
        knowledge_results=[],
    )