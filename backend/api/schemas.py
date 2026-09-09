"""
Pydantic schemas used by the FastAPI backend.
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request schema for security analysis queries."""

    query: str = Field(
        ...,
        min_length=1,
        description="Security-related query to analyse.",
    )


class AnalyzeResponse(BaseModel):
    """Response schema returned by the analysis endpoint."""

    answer: str


class ServerSchema(BaseModel):
    """Schema representing a synchronisation server."""

    source_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the server.",
    )

    name: str = Field(
        ...,
        min_length=1,
        description="Display name of the server.",
    )

    host: str = Field(
        ...,
        min_length=1,
        description="Server hostname or IP address.",
    )

    username: str = Field(
        ...,
        min_length=1,
        description="SSH username used for synchronisation.",
    )

    remote_path: str = Field(
        ...,
        min_length=1,
        description="Remote log directory.",
    )

    local_path: str = Field(
        ...,
        min_length=1,
        description="Local directory used for synchronised logs.",
    )

    enabled: bool = Field(
        default=True,
        description="Whether synchronisation is enabled.",
    )

    sync_interval: int = Field(
        default=60,
        gt=0,
        description="Synchronisation interval in seconds.",
    )