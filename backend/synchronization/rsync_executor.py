"""
rsync_executor.py

Provides a reusable wrapper for executing rsync through WSL
on Windows.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class RsyncResult:
    """Result of one rsync operation."""

    success: bool
    return_code: int
    stdout: str
    stderr: str


class RsyncExecutor:
    """
    Executes rsync through WSL.

    The executor accepts rsync options from the configured
    synchronization source, allowing each server to define
    its own rsync behaviour.
    """

    def __init__(
        self,
        timeout: int = 30,
    ) -> None:
        """
        Initialise the rsync executor.

        timeout:
            Maximum number of seconds allowed for one rsync
            operation.
        """

        if (
            not isinstance(timeout, int)
            or isinstance(timeout, bool)
            or timeout <= 0
        ):
            raise ValueError(
                "timeout must be an integer greater than 0."
            )

        self.command = ["wsl", "rsync"]
        self.timeout = timeout

    def _to_wsl_path(
        self,
        path: str | Path,
    ) -> str:
        """
        Convert a Windows path to a WSL path.

        Linux/WSL paths are returned unchanged.
        """

        path_string = str(path)

        # Already a WSL/Linux path.
        if path_string.startswith("/"):
            return path_string

        # Windows drive path, e.g. C:\Users\...
        if (
            len(path_string) >= 2
            and path_string[1] == ":"
        ):
            drive = path_string[0].lower()

            remainder = (
                path_string[2:]
                .replace("\\", "/")
            )

            return f"/mnt/{drive}{remainder}"

        return path_string

    def sync(
        self,
        source: str,
        destination: str | Path,
        options: Sequence[str] | None = None,
    ) -> RsyncResult:
        """
        Execute one rsync operation.

        The caller can provide custom rsync options.
        """

        if (
            not isinstance(source, str)
            or not source.strip()
        ):
            raise ValueError(
                "source must be a non-empty string."
            )

        destination_path = Path(destination)

        destination_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        wsl_source = self._to_wsl_path(
            source
        )

        wsl_destination = self._to_wsl_path(
            destination_path
        )

        # Use configured options when supplied.
        # Fall back to the standard archive, verbose,
        # and compression flags.
        rsync_options = (
            list(options)
            if options
            else ["-avz"]
        )

        command = [
            *self.command,
            *rsync_options,
            wsl_source,
            wsl_destination,
        ]

        try:

            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout,
            )

        except subprocess.TimeoutExpired as exc:

            stdout = (
                exc.stdout
                if isinstance(exc.stdout, str)
                else ""
            )

            stderr = (
                exc.stderr
                if isinstance(exc.stderr, str)
                else ""
            )

            timeout_message = (
                f"rsync operation timed out after "
                f"{self.timeout} seconds."
            )

            if stderr.strip():

                timeout_message = (
                    f"{timeout_message} "
                    f"{stderr.strip()}"
                )

            return RsyncResult(
                success=False,
                return_code=-3,
                stdout=stdout.strip(),
                stderr=timeout_message,
            )

        except (
            FileNotFoundError,
            OSError,
        ) as exc:

            return RsyncResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=str(exc),
            )

        return RsyncResult(
            success=completed.returncode == 0,
            return_code=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )

    def is_available(self) -> bool:
        """
        Return True when WSL rsync is available.
        """

        try:

            completed = subprocess.run(
                [
                    *self.command,
                    "--version",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout,
            )

        except (
            FileNotFoundError,
            OSError,
            subprocess.TimeoutExpired,
        ):
            return False

        return completed.returncode == 0