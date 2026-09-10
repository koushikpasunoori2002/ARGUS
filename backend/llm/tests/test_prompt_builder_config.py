"""
Tests for configurable prompt integration.
"""

from backend.llm.generation.prompt_builder import PromptBuilder
from backend.rag.context import RAGContext


def _create_context():
    """
    Create a test RAG context.
    """

    context = RAGContext(
        query="failed SSH authentication",
    )

    context.add_log_result({
        "id": "log_001",
        "document": (
            "Failed password for root "
            "from 192.168.1.20"
        ),
        "metadata": {
            "severity": "HIGH",
            "source": "auth.log",
        },
        "distance": 0.8,
    })

    context.add_knowledge_result({
        "id": "KB_001",
        "document": (
            "Repeated failed SSH authentication "
            "attempts may indicate a brute-force attack."
        ),
        "metadata": {
            "category": "authentication",
        },
        "distance": 0.3,
    })

    return context


def test_prompt_builder_loads_configured_prompts():
    """
    Verify that PromptBuilder loads the configured prompts.
    """

    builder = PromptBuilder()

    info = builder.info()

    assert info["prompt_config"]["prompt_count"] == 2
    assert (
        "security_analysis"
        in info["prompt_config"]["prompts"]
    )
    assert (
        "evidence_summary"
        in info["prompt_config"]["prompts"]
    )


def test_security_analysis_template_is_used():
    """
    Verify that the configured security-analysis
    template is included in the generated prompt.
    """

    builder = PromptBuilder()

    configured_template = (
        builder.prompts_config.get_template(
            "security_analysis"
        )
    )

    prompt = builder.build_analysis_prompt(
        _create_context()
    )

    assert configured_template in prompt


def test_evidence_summary_template_is_used():
    """
    Verify that the configured evidence-summary
    template is included in the generated prompt.
    """

    builder = PromptBuilder()

    configured_template = (
        builder.prompts_config.get_template(
            "evidence_summary"
        )
    )

    prompt = (
        builder.build_evidence_summary_prompt(
            _create_context()
        )
    )

    assert configured_template in prompt


def test_evidence_summary_prompt_contains_query():
    """
    Verify that the evidence-summary prompt
    contains the user query.
    """

    builder = PromptBuilder()
    context = _create_context()

    prompt = (
        builder.build_evidence_summary_prompt(
            context
        )
    )

    assert context.query in prompt


def test_evidence_summary_prompt_contains_evidence():
    """
    Verify that the evidence-summary prompt
    contains retrieved log and knowledge evidence.
    """

    builder = PromptBuilder()

    prompt = (
        builder.build_evidence_summary_prompt(
            _create_context()
        )
    )

    assert "Failed password for root" in prompt
    assert "192.168.1.20" in prompt
    assert "Repeated failed SSH authentication" in prompt
    assert "brute-force attack" in prompt


def test_prompt_builder_rejects_invalid_context():
    """
    Verify that PromptBuilder rejects invalid context objects.
    """

    builder = PromptBuilder()

    try:
        builder.build("invalid context")
    except TypeError:
        return

    raise AssertionError(
        "PromptBuilder accepted an invalid context."
    )