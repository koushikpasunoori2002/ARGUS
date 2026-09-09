"""
Server management API endpoints.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from backend.api.schemas import ServerSchema
from backend.config.hosts_config import HostsConfig
from backend.synchronization.models.sync_source import SyncSource


router = APIRouter(
    prefix="/servers",
    tags=["Servers"],
)

config = HostsConfig()


def get_project_root() -> Path:
    """
    Return the project root directory.
    """

    return Path(__file__).resolve().parents[2]


def create_server_local_directory(
    local_path: str,
) -> None:
    """
    Create the local directory configured for a server.
    """

    project_root = get_project_root()

    path = Path(local_path)

    if not path.is_absolute():
        path = project_root / path

    path.mkdir(
        parents=True,
        exist_ok=True,
    )


@router.get("")
def get_servers() -> list[dict]:
    """
    Return all configured servers.
    """

    return [
        server.to_dict()
        for server in config.get_all()
    ]


# ----------------------------------------------------------
# Synchronization Status
# ----------------------------------------------------------

@router.get("/sync-status")
def get_sync_status(
    request: Request,
) -> list[dict]:
    """
    Return live synchronization status for every configured
    server, including its configured interval and approximate
    time until the next synchronization.
    """

    synchronization_service = getattr(
        request.app.state,
        "synchronization_service",
        None,
    )

    if synchronization_service is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Synchronization service is not "
                "available."
            ),
        )

    statuses = (
        synchronization_service.get_all_statuses()
    )

    servers = config.get_all()

    response = []

    for server in servers:

        status = statuses.get(
            server.source_id
        )

        next_sync_in = (
            synchronization_service.get_next_sync_in(
                server
            )
        )

        server_status = (
            status
            if status is not None
            else {
                "source_id": server.source_id,
                "status": "pending",
            }
        )

        response.append(
            {
                "source_id": server.source_id,
                "name": server.name,
                "enabled": server.enabled,
                "sync_interval": server.sync_interval,
                "next_sync_in": next_sync_in,
                "status": server_status,
            }
        )

    return response


# ----------------------------------------------------------
# Individual Server
# ----------------------------------------------------------

@router.get("/{source_id}")
def get_server(
    source_id: str,
) -> dict:
    """
    Return one configured server.
    """

    server = config.get(
        source_id
    )

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
    Add a new server and create its local directory.
    """

    try:

        server = SyncSource(
            **server_data.model_dump()
        )

        create_server_local_directory(
            server.local_path
        )

        config.add(
            server
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except OSError as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to create the server local "
                f"directory: {exc}"
            ),
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

        create_server_local_directory(
            server.local_path
        )

        config.update(
            server
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except OSError as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to create the server local "
                f"directory: {exc}"
            ),
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

        config.delete(
            source_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "message": "Server deleted successfully.",
        "source_id": source_id,
    }