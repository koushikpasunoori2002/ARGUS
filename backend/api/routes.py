"""
routes.py

Basic API routes for ARGUS.
"""

from fastapi import APIRouter


router = APIRouter()


@router.get("/status")
def status():
    """
    Return the current API status.
    """

    return {
        "application": "ARGUS",
        "status": "operational",
    }