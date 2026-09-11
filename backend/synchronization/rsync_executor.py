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

    Relative local paths are resolved against the project root
    before being converted to WSL paths.
    """

    def __init__(
        self,
        timeout: int = 30,
    ) -> None:
        """
        Initialise the rsync executor.
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

        self.project_root = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

    def _to_wsl_path(
        self,
        path: str | Path,
    ) -> str:
        """
        Convert a Windows or project-relative path to
        a WSL-compatible path while preserving a trailing slash.
        """

        path_string = str(path)

        # Preserve whether the caller explicitly supplied a
        # trailing slash. Rsync uses this to distinguish between
        # copying a directory and copying its contents.
        has_trailing_slash = path_string.endswith(
            ("/", "\\")
        )

        # Already a Linux/WSL absolute path.
        if path_string.startswith("/"):
            return path_string

        # Windows absolute path.
        if (
            len(path_string) >= 2
            and path_string[1] == ":"
        ):
            windows_path = Path(
                path_string
            ).resolve()

        else:
            # Resolve project-relative paths against the
            # LogLlamalyzer project root.
            windows_path = (
                self.project_root / path_string
            ).resolve()

        windows_string = str(
            windows_path
        ).replace("\\", "/")

        # Convert C:/Users/... to /mnt/c/Users/...
        if (
            len(windows_string) >= 2
            and windows_string[1] == ":"
        ):
            drive = windows_string[0].lower()
            remainder = windows_string[2:]

            if not remainder.startswith("/"):
                remainder = "/" + remainder

            wsl_path = (
                f"/mnt/{drive}"
                f"{remainder}"
            )

        else:
            wsl_path = windows_string

        if has_trailing_slash:
            wsl_path += "/"

        return wsl_path

    def sync(
        self,
        source: str,
        destination: str | Path,
        options: Sequence[str] | None = None,
    ) -> RsyncResult:
        """
        Execute one rsync operation.
        """

        if (
            not isinstance(source, str)
            or not source.strip()
        ):
            raise ValueError(
                "source must be a non-empty string."
            )

        destination_path = Path(
            destination
        )

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

        # Use supplied options or the standard default.
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
                if isinstance(
                    exc.stdout,
                    str,
                )
                else ""
            )

            stderr = (
                exc.stderr
                if isinstance(
                    exc.stderr,
                    str,
                )
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