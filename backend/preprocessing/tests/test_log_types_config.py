"""
Tests for configurable log-type and parser definitions.
"""

from backend.config.log_types_config import LogTypesConfig
from backend.preprocessing.parsers import ParserFactory


def test_log_types_configuration():
    """
    Verify that all configured log types are loaded.
    """

    config = LogTypesConfig()

    expected_log_types = {
        "auth",
        "syslog",
        "kern",
        "dpkg",
        "dmesg",
    }

    assert set(
        config.supported_log_types()
    ) == expected_log_types


def test_configured_parser_names():
    """
    Verify that each log type has the expected parser definition.
    """

    config = LogTypesConfig()

    expected_parsers = {
        "auth": "AuthParser",
        "syslog": "SyslogParser",
        "kern": "KernParser",
        "dpkg": "DpkgParser",
        "dmesg": "DmesgParser",
    }

    for log_type, parser_name in expected_parsers.items():
        assert (
            config.get_parser_name(log_type)
            == parser_name
        )


def test_parser_factory_uses_configuration():
    """
    Verify that ParserFactory creates the parser configured
    in system.config.
    """

    config = LogTypesConfig()

    for log_type in config.supported_log_types():

        parser_name = config.get_parser_name(
            log_type
        )

        parser = ParserFactory.create(
            log_type
        )

        assert (
            type(parser).__name__
            == parser_name
        )


def test_unknown_log_type_is_rejected():
    """
    Verify that an unconfigured log type is rejected.
    """

    try:
        ParserFactory.create(
            "unknown"
        )
    except ValueError as exc:
        assert (
            "No parser configured for log type"
            in str(exc)
        )
        return

    raise AssertionError(
        "ParserFactory accepted an unknown log type."
    )


def test_empty_log_type_is_rejected():
    """
    Verify that an empty log type is rejected.
    """

    try:
        ParserFactory.create("")
    except ValueError as exc:
        assert (
            "log_type cannot be empty"
            in str(exc)
        )
        return

    raise AssertionError(
        "ParserFactory accepted an empty log type."
    )