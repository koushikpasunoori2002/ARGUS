"""
Server management API endpoints.
"""

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ServerSchema
from backend.config.hosts_config import HostsConfig
from backend.synchronization.models.sync_source import SyncSource


router = APIRouter(
    prefix="/servers",
    tags=["Servers"],
)

config = HostsConfig()


@router.get("")
def get_servers() -> list[dict]:
    """
    Return all configured servers.
    """

    return [
        server.to_dict()
        for server in config.get_all()
    ]


@router.get("/{source_id}")
def get_server(
    source_id: str,
) -> dict:
    """
    Return one configured server.
    """

    server = config.get(source_id)

    if server is None:
        raise HTTPException(
            status_code=404,
            detail="Server not found.",
        )

    return server.to_dict()


@router.post("")
def add_server(
    server_data: ServerSchema,
) -> dict:
    """
    Add a new server.
    """

    try:
        server = SyncSource(
            **server_data.model_dump()
        )

        config.add(server)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return server.to_dict()


@router.put("/{source_id}")
def update_server(
    source_id: str,
    server_data: ServerSchema,
) -> dict:
    """
    Update an existing server.
    """

    if source_id != server_data.source_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "source_id in the URL and request "
                "body must match."
            ),
        )

    try:
        server = SyncSource(
            **server_data.model_dump()
        )

        config.update(server)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return server.to_dict()


@router.delete("/{source_id}")
def delete_server(
    source_id: str,
) -> dict:
    """
    Delete an existing server.
    """

    try:
        config.delete(source_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "message": "Server deleted successfully.",
        "source_id": source_id,
    }