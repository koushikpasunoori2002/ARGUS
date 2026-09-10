"""
Tests the preprocessing pipeline using configured parser mappings.
"""

from pathlib import Path

from backend.preprocessing.pipeline import PreprocessingPipeline


PROJECT_ROOT = Path(__file__).resolve().parents[3]


FILES = {
    "auth": (
        PROJECT_ROOT
        / "dataset"
        / "raw"
        / "auth"
        / "auth.log"
    ),
    "syslog": (
        PROJECT_ROOT
        / "dataset"
        / "raw"
        / "syslog"
        / "syslog"
    ),
    "kern": (
        PROJECT_ROOT
        / "dataset"
        / "raw"
        / "kern"
        / "kern.log"
    ),
    "dpkg": (
        PROJECT_ROOT
        / "dataset"
        / "raw"
        / "dpkg"
        / "dpkg.log"
    ),
    "dmesg": (
        PROJECT_ROOT
        / "dataset"
        / "raw"
        / "dmesg"
        / "dmesg.1.gz"
    ),
}


def test_configured_pipeline_processes_all_supported_log_types():
    """
    Verify that the preprocessing pipeline can process all
    currently configured log types.
    """

    pipeline = PreprocessingPipeline()

    for log_type, file_path in FILES.items():

        assert file_path.exists(), (
            f"Test log file does not exist: {file_path}"
        )

        records = pipeline.process(file_path)

        assert isinstance(records, list)
        assert len(records) > 0

        for record in records:
            assert record.log_type == log_type


def test_configured_pipeline_auth():
    """
    Verify auth logs are processed successfully.
    """

    pipeline = PreprocessingPipeline()

    records = pipeline.process(
        FILES["auth"]
    )

    assert len(records) == 10
    assert all(
        record.log_type == "auth"
        for record in records
    )


def test_configured_pipeline_compressed_dmesg():
    """
    Verify compressed dmesg logs are processed successfully.
    """

    pipeline = PreprocessingPipeline()

    records = pipeline.process(
        FILES["dmesg"]
    )

    assert len(records) > 0
    assert all(
        record.log_type == "dmesg"
        for record in records
    )