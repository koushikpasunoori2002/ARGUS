"""
Final quantitative evaluation summary for ARGUS.

This module consolidates previously executed evaluation evidence
into a reproducible machine-readable result artifact.

It does not rerun the LLM-based evaluations.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PERFORMANCE_RESULTS = (
    PROJECT_ROOT
    / "outputs"
    / "results"
    / "performance_results.json"
)

OUTPUT_RESULTS = (
    PROJECT_ROOT
    / "outputs"
    / "results"
    / "final_evaluation_results.json"
)


def load_performance_results():
    """Load the existing measured performance results."""

    if not PERFORMANCE_RESULTS.exists():
        raise FileNotFoundError(
            f"Performance results not found: {PERFORMANCE_RESULTS}"
        )

    with PERFORMANCE_RESULTS.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_evaluation_results(performance):
    """Build the final structured evaluation results."""

    return {
        "project": "ARGUS",
        "evaluation": {
            "phase": "Phase 42",
            "purpose": (
                "Final quantitative evaluation and coursework "
                "evidence consolidation."
            ),
            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "evaluations": {
            "security_query_evaluation": {
                "passed": 5,
                "total": 5,
                "rate_percent": 100.0,
                "metric": (
                    "Valid API response rate across "
                    "representative security queries"
                ),
                "interpretation": (
                    "Measures whether the /analyze endpoint "
                    "returned a valid non-empty analysis response. "
                    "It does not measure security detection accuracy."
                ),
            },
            "threat_scenario_evaluation": {
                "passed": 5,
                "total": 5,
                "rate_percent": 100.0,
                "metric": (
                    "Required security-concept coverage"
                ),
                "interpretation": (
                    "Measures whether generated answers contained "
                    "the required concepts for five predefined "
                    "security scenarios. It is not a general-world "
                    "threat detection accuracy measure."
                ),
            },
            "retrieval_quality_evaluation": {
                "passed": 5,
                "total": 5,
                "rate_percent": 100.0,
                "metric": (
                    "Top-3 scenario relevance"
                ),
                "interpretation": (
                    "Measures whether at least one expected relevant "
                    "scenario was retrieved within the top three "
                    "results for five representative queries."
                ),
            },
            "regression_validation": {
                "passed": 114,
                "total": 114,
                "rate_percent": 100.0,
                "metric": (
                    "Automated regression test pass rate"
                ),
                "interpretation": (
                    "Baseline full-suite result recorded before "
                    "Phase 42 modifications."
                ),
                "duration_seconds": 1678.43,
            },
        },
        "performance": performance,
        "limitations": [
            (
                "Evaluation scenarios are small and representative "
                "rather than a statistically large security dataset."
            ),
            (
                "Retrieval relevance is measured using predefined "
                "scenario metadata and top-3 retrieval."
            ),
            (
                "Threat scenario evaluation measures concept "
                "coverage rather than ground-truth detection accuracy."
            ),
            (
                "Security-query evaluation measures API response "
                "validity rather than correctness of the generated analysis."
            ),
            (
                "Performance measurements depend on the local "
                "hardware, Ollama configuration, embedding model, "
                "and LLM model used during testing."
            ),
        ],
    }


def main():
    """Generate the final evaluation JSON artifact."""

    performance = load_performance_results()

    results = build_evaluation_results(
        performance
    )

    OUTPUT_RESULTS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_RESULTS.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    print("=" * 60)
    print("ARGUS FINAL EVALUATION")
    print("=" * 60)

    print(
        f"\nOutput: {OUTPUT_RESULTS}"
    )

    for name, evaluation in results["evaluations"].items():
        print(
            f"\n{name}"
        )
        print(
            f"Result: "
            f"{evaluation['passed']}/"
            f"{evaluation['total']}"
        )
        print(
            f"Rate: "
            f"{evaluation['rate_percent']:.1f}%"
        )

    print("\nPerformance")
    print(
        "RAG full process: "
        f"{performance['rag_pipeline']['full_process_seconds']:.4f} s"
    )
    print(
        "Security analysis full process: "
        f"{performance['security_analysis']['full_process_seconds']:.4f} s"
    )
    print(
        "Security/RAG ratio: "
        f"{performance['comparison']['security_analysis_to_rag_ratio']:.4f}x"
    )

    print("\n" + "=" * 60)
    print("FINAL EVALUATION ARTIFACT GENERATED")
    print("=" * 60)


if __name__ == "__main__":
    main()
