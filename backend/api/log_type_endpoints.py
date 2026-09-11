"""
log_type_endpoints.py

API endpoints for configured log types and parser definitions.
"""

from fastapi import APIRouter

from backend.config.log_types_config import LogTypesConfig


router = APIRouter(
    prefix="/log-types",
    tags=["Log Types"],
)


@router.get("")
def get_log_types():
    """
    Return all configured log types and their parser definitions.
    """

    config = LogTypesConfig()

    log_types = config.get_all()

    return {
        "log_types": [
            {
                "log_type": log_type,
                "parser": definition["parser"],
            }
            for log_type, definition in log_types.items()
        ],
        "count": len(log_types),
    }