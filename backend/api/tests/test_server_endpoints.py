"""
End-to-end tests for server management API endpoints.
"""

import json

from fastapi.testclient import TestClient

from backend.api.app import app
from backend.config.hosts_config import HostsConfig
import backend.api.server_endpoints as server_endpoints


SERVER_DATA = {
    "source_id": "server-test",
    "name": "Test Server",
    "host": "192.168.1.10",
    "username": "user",
    "remote_path": "/var/log/",
    "local_path": "data/server-test",
    "enabled": True,
}


def create_test_config(tmp_path):
    """Create an isolated configuration file."""

    config_path = tmp_path / "hosts.config"

    config_path.write_text(
        json.dumps(
            {"servers": []},
            indent=2,
        ),
        encoding="utf-8",
    )

    return HostsConfig(
        config_path=config_path
    )


def test_server_crud_api(tmp_path, monkeypatch):
    """
    Verify the complete server CRUD lifecycle.
    """

    test_config = create_test_config(
        tmp_path
    )

    monkeypatch.setattr(
        server_endpoints,
        "config",
        test_config,
    )

    client = TestClient(app)

    # ------------------------------------------------------
    # Create
    # ------------------------------------------------------

    response = client.post(
        "/servers",
        json=SERVER_DATA,
    )

    assert response.status_code == 200

    created = response.json()

    assert created["source_id"] == "server-test"
    assert created["name"] == "Test Server"

    # ------------------------------------------------------
    # Read all
    # ------------------------------------------------------

    response = client.get(
        "/servers"
    )

    assert response.status_code == 200

    servers = response.json()

    assert len(servers) == 1
    assert servers[0]["source_id"] == "server-test"

    # ------------------------------------------------------
    # Read one
    # ------------------------------------------------------

    response = client.get(
        "/servers/server-test"
    )

    assert response.status_code == 200

    server = response.json()

    assert server["source_id"] == "server-test"
    assert server["host"] == "192.168.1.10"

    # ------------------------------------------------------
    # Update
    # ------------------------------------------------------

    updated_data = {
        **SERVER_DATA,
        "name": "Updated Server",
        "host": "192.168.1.20",
        "remote_path": "/var/log/security/",
    }

    response = client.put(
        "/servers/server-test",
        json=updated_data,
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["name"] == "Updated Server"
    assert updated["host"] == "192.168.1.20"
    assert updated["remote_path"] == (
        "/var/log/security/"
    )

    # ------------------------------------------------------
    # Verify update persisted
    # ------------------------------------------------------

    response = client.get(
        "/servers/server-test"
    )

    assert response.status_code == 200

    persisted = response.json()

    assert persisted["name"] == "Updated Server"
    assert persisted["host"] == "192.168.1.20"

    # ------------------------------------------------------
    # Delete
    # ------------------------------------------------------

    response = client.delete(
        "/servers/server-test"
    )

    assert response.status_code == 200

    deleted = response.json()

    assert deleted["source_id"] == "server-test"

    # ------------------------------------------------------
    # Verify deletion
    # ------------------------------------------------------

    response = client.get(
        "/servers/server-test"
    )

    assert response.status_code == 404


def test_duplicate_server_returns_bad_request(
    tmp_path,
    monkeypatch,
):
    """Verify duplicate server IDs are rejected."""

    test_config = create_test_config(
        tmp_path
    )

    monkeypatch.setattr(
        server_endpoints,
        "config",
        test_config,
    )

    client = TestClient(app)

    first = client.post(
        "/servers",
        json=SERVER_DATA,
    )

    second = client.post(
        "/servers",
        json=SERVER_DATA,
    )

    assert first.status_code == 200
    assert second.status_code == 400


def test_missing_server_returns_not_found(
    tmp_path,
    monkeypatch,
):
    """Verify missing servers return 404."""

    test_config = create_test_config(
        tmp_path
    )

    monkeypatch.setattr(
        server_endpoints,
        "config",
        test_config,
    )

    client = TestClient(app)

    response = client.get(
        "/servers/missing-server"
    )

    assert response.status_code == 404


def test_invalid_server_data_returns_validation_error():
    """Verify Pydantic validation rejects invalid input."""

    client = TestClient(app)

    invalid_data = {
        "source_id": "",
        "name": "Invalid Server",
        "host": "192.168.1.10",
        "username": "user",
        "remote_path": "/var/log/",
        "local_path": "data/server-test",
        "enabled": True,
    }

    response = client.post(
        "/servers",
        json=invalid_data,
    )

    assert response.status_code == 422