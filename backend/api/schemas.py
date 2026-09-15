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

    source_id: str | None = Field(
        default=None,
        description="Optional server source ID used to restrict log retrieval.",
    )


class AnalyzeResponse(BaseModel):
    """Response schema returned by the analysis endpoint."""

    query: str

    answer: str

    evidence: list[dict] = Field(
        default_factory=list,
        description="Retrieved log evidence related to the query.",
    )

    related_log_results: list[dict] = Field(
        default_factory=list,
        description="Log records related to the retrieved evidence.",
    )

    knowledge: list[dict] = Field(
        default_factory=list,
        description="Retrieved security knowledge used for interpretation.",
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Analysis and retrieval metadata.",
    )


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
        description="Display name for the server.",
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
