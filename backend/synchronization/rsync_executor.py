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

    This class is responsible only for executing one rsync operation.
    Server management, scheduling, configuration and frontend control
    will be implemented in later phases.
    """

    def __init__(self) -> None:
        self.command = ["wsl", "rsync"]

    def _to_wsl_path(self, path: str | Path) -> str:
        """
        Convert a Windows path to a WSL path.

        Linux/WSL paths are returned unchanged.
        """

        path_string = str(path)

        # Already a WSL/Linux path
        if path_string.startswith("/"):
            return path_string

        # Windows drive path, e.g. C:\Users\...
        if len(path_string) >= 2 and path_string[1] == ":":
            drive = path_string[0].lower()
            remainder = path_string[2:].replace("\\", "/")

            return f"/mnt/{drive}{remainder}"

        return path_string


    def sync(
        self,
        source: str,
        destination: str | Path,
        options: Sequence[str] | None = None,
) ->     RsyncResult:
        """
        Execute one rsync operation.
        """

        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be a non-empty string.")

        destination_path = Path(destination)

        destination_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        wsl_source = self._to_wsl_path(source)
        wsl_destination = self._to_wsl_path(destination_path)

        command = [
            *self.command,
            "-avz",
        ]

        if options:
            command.extend(options)

        command.extend(
            [
                wsl_source,
                wsl_destination,
            ]
        )

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )

        except (FileNotFoundError, OSError) as exc:
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
        """Return True when WSL rsync is available."""

        try:
            completed = subprocess.run(
                [
                    *self.command,
                    "--version",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except (FileNotFoundError, OSError):
            return False

        return completed.returncode == 0