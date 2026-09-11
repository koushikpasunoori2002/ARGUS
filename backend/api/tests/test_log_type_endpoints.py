"""
Tests for log-type and parser configuration API endpoints.
"""

from fastapi.testclient import TestClient

from backend.api.app import app


client = TestClient(app)


def test_get_log_types_returns_success():
    """
    Verify that the log-type endpoint responds successfully.
    """

    response = client.get("/log-types")

    assert response.status_code == 200


def test_get_log_types_returns_expected_structure():
    """
    Verify the response contains the expected structure.
    """

    response = client.get("/log-types")

    data = response.json()

    assert isinstance(data, dict)
    assert "log_types" in data
    assert "count" in data

    assert isinstance(
        data["log_types"],
        list,
    )

    assert isinstance(
        data["count"],
        int,
    )


def test_get_log_types_returns_configured_mappings():
    """
    Verify that configured log types and parser mappings
    are returned by the API.
    """

    response = client.get("/log-types")

    data = response.json()

    mappings = {
        item["log_type"]: item["parser"]
        for item in data["log_types"]
    }

    expected_mappings = {
        "auth": "AuthParser",
        "syslog": "SyslogParser",
        "kern": "KernParser",
        "dpkg": "DpkgParser",
        "dmesg": "DmesgParser",
    }

    assert mappings == expected_mappings
    assert data["count"] == 5


def test_get_log_types_returns_valid_entries():
    """
    Verify every returned entry contains a log type and parser.
    """

    response = client.get("/log-types")

    data = response.json()

    for item in data["log_types"]:
        assert isinstance(
            item,
            dict,
        )

        assert "log_type" in item
        assert "parser" in item

        assert isinstance(
            item["log_type"],
            str,
        )

        assert isinstance(
            item["parser"],
            str,
        )

        assert item["log_type"].strip()
        assert item["parser"].strip()