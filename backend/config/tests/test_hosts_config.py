"""
Tests for HostsConfig.
"""

import json

import pytest

from backend.config.hosts_config import HostsConfig
from backend.synchronization.models.sync_source import SyncSource


def create_source(
    source_id="server-test",
    name="Test Server",
    host="192.168.1.10",
):
    """Create a valid synchronization source."""
    return SyncSource(
        source_id=source_id,
        name=name,
        host=host,
        username="user",
        remote_path="/var/log/",
        local_path="data/server-test",
        enabled=True,
    )


@pytest.fixture
def config_file(tmp_path):
    """Create an isolated hosts.config file."""
    path = tmp_path / "hosts.config"

    path.write_text(
        json.dumps(
            {"servers": []},
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


@pytest.fixture
def config(config_file):
    """Create a HostsConfig instance."""
    return HostsConfig(
        config_path=config_file
    )


def test_add_server(config):
    """Verify a server can be added."""

    source = create_source()

    config.add(source)

    result = config.get(
        "server-test"
    )

    assert result is not None
    assert result.source_id == "server-test"


def test_duplicate_server_is_rejected(config):
    """Verify duplicate source IDs are rejected."""

    source = create_source()

    config.add(source)

    with pytest.raises(ValueError):
        config.add(source)


def test_update_existing_server(config):
    """Verify an existing server can be updated."""

    config.add(create_source())

    updated = create_source(
        name="Updated Server",
        host="192.168.1.20",
    )

    config.update(updated)

    result = config.get(
        "server-test"
    )

    assert result is not None
    assert result.name == "Updated Server"
    assert result.host == "192.168.1.20"


def test_update_missing_server_is_rejected(config):
    """Verify updating a missing server fails."""

    with pytest.raises(ValueError):
        config.update(
            create_source()
        )


def test_delete_existing_server(config):
    """Verify an existing server can be deleted."""

    config.add(create_source())

    config.delete(
        "server-test"
    )

    assert config.get(
        "server-test"
    ) is None


def test_delete_missing_server_is_rejected(config):
    """Verify deleting a missing server fails."""

    with pytest.raises(ValueError):
        config.delete(
            "missing-server"
        )


def test_get_all_returns_all_servers(config):
    """Verify all configured servers are returned."""

    config.add(
        create_source(
            source_id="server-1",
            name="Server 1",
            host="192.168.1.10",
        )
    )

    config.add(
        create_source(
            source_id="server-2",
            name="Server 2",
            host="192.168.1.20",
        )
    )

    servers = config.get_all()

    assert len(servers) == 2
    assert servers[0].source_id == "server-1"
    assert servers[1].source_id == "server-2"


def test_saved_configuration_is_valid_json(config_file, config):
    """Verify saved configuration remains valid JSON."""

    config.add(
        create_source()
    )

    data = json.loads(
        config_file.read_text(
            encoding="utf-8"
        )
    )

    assert "servers" in data
    assert len(data["servers"]) == 1


def test_invalid_config_structure_is_rejected(tmp_path):
    """Verify malformed top-level configuration is rejected."""

    path = tmp_path / "hosts.config"

    path.write_text(
        json.dumps(
            {"servers": {}}
        ),
        encoding="utf-8",
    )

    config = HostsConfig(
        config_path=path
    )

    with pytest.raises(ValueError):
        config.load()