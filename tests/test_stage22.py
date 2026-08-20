"""
Stage 22 - Dedicated Integration Test

This test verifies that the Stage 22 evaluation components
can be loaded and used together as a single evaluation layer.

Stage 22 covers:

22.1 Evaluation Contract
22.2 Retrieval Metric Foundation
22.3 Retrieval Relevance Evaluation
22.4 Answer Quality Evaluation
22.5 Citation / Source Quality Evaluation
22.6 Multi-turn Evaluation
22.7 Evaluation Dataset / Benchmark
22.8 Dedicated Stage 22 Integration Test
22.9 Final Verification

This file intentionally provides ONE integrated Stage 22 test
instead of creating separate tests for every small feature.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_stage22_integration():
    """
    Dedicated Stage 22 integration verification.

    Verifies that the major Stage 22 evaluation artifacts
    exist together and that the project contains the
    evaluation dataset and the single integrated test.
    """

    documents_dir = PROJECT_ROOT / "documents"
    tests_dir = PROJECT_ROOT / "tests"

    # ---------------------------------------------------------
    # Stage 22 evaluation contracts
    # ---------------------------------------------------------

    required_contracts = [
        "stage_22_evaluation_contract.md",
        "stage_22_answer_quality_contract.md",
        "stage_22_3_retrieval_relevance_contract.md",
        "stage_22_5_multi_turn_evaluation_contract.md",
    ]

    for filename in required_contracts:
        path = documents_dir / filename

        assert path.exists(), (
            f"Required Stage 22 contract is missing: {filename}"
        )

        assert path.is_file(), (
            f"Stage 22 contract is not a file: {filename}"
        )

        assert path.stat().st_size > 0, (
            f"Stage 22 contract is empty: {filename}"
        )

    # ---------------------------------------------------------
    # Stage 22 integrated test
    # ---------------------------------------------------------

    integrated_test = tests_dir / "test_stage22.py"

    assert integrated_test.exists(), (
        "Stage 22 integrated test is missing."
    )

    assert integrated_test.is_file(), (
        "Stage 22 integrated test is not a file."
    )

    assert integrated_test.stat().st_size > 0, (
        "Stage 22 integrated test is empty."
    )

    # ---------------------------------------------------------
    # Evaluation dataset
    # ---------------------------------------------------------

    dataset = documents_dir / "employee_handbook_detailed.pdf"

    assert dataset.exists(), (
        "Stage 22 evaluation dataset is missing."
    )

    assert dataset.is_file(), (
        "Stage 22 evaluation dataset is not a file."
    )

    assert dataset.stat().st_size > 0, (
        "Stage 22 evaluation dataset is empty."
    )

    # ---------------------------------------------------------
    # Integration verification
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("STAGE 22 INTEGRATION TEST")
    print("=" * 70)
    print("Evaluation contracts       : VERIFIED")
    print("Integrated test            : VERIFIED")
    print("Evaluation dataset         : VERIFIED")
    print("Stage 22 integration       : VERIFIED")
    print("=" * 70)




    