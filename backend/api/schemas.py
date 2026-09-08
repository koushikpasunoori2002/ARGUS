"""
schemas.py

Pydantic request and response models for the LogLlamalyzer API.
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """
    Request model for security analysis.
    """

    query: str


class AnalyzeResponse(BaseModel):
    """
    Response model returned by the analysis endpoint.
    """

    query: str
    answer: str


class ServerSchema(BaseModel):
    """
    Server configuration model.
    """

    source_id: str = Field(
        min_length=1,
        description="Unique identifier for the server.",
    )

    name: str = Field(
        min_length=1,
        description="Display name of the server.",
    )

    host: str = Field(
        min_length=1,
        description="Hostname or IP address.",
    )

    username: str = Field(
        min_length=1,
        description="SSH username.",
    )

    remote_path: str = Field(
        min_length=1,
        description="Remote log directory.",
    )

    local_path: str = Field(
        min_length=1,
        description="Local synchronization directory.",
    )

    enabled: bool = True