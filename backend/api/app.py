"""
app.py

Main FastAPI application for LogLlamalyzer.
"""

from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as status_router
from backend.api.endpoints import router as analysis_router
from backend.api.server_endpoints import router as server_router
from backend.config.hosts_config import HostsConfig
from backend.synchronization.synchronization_service import (
    SynchronizationService,
)


# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------

synchronization_logger = logging.getLogger(
    "backend.synchronization.synchronization_service"
)

synchronization_logger.setLevel(logging.INFO)
synchronization_logger.propagate = False

if not synchronization_logger.handlers:

    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console_handler.setFormatter(console_formatter)

    synchronization_logger.addHandler(
        console_handler
    )


# ----------------------------------------------------------
# Synchronization Components
# ----------------------------------------------------------

synchronization_service = SynchronizationService()

hosts_config = HostsConfig()

synchronization_thread: threading.Thread | None = None


def start_synchronization_scheduler() -> None:
    """
    Start the continuous per-server synchronization scheduler.
    """

    global synchronization_thread

    if (
        synchronization_thread is not None
        and synchronization_thread.is_alive()
    ):
        return

    synchronization_thread = threading.Thread(
        target=synchronization_service.start_continuous_sync,
        kwargs={
            "sources_provider": hosts_config.get_all,
            "check_interval": 1.0,
        },
        daemon=True,
        name="LogLlamalyzer-Synchronization",
    )

    synchronization_thread.start()


def stop_synchronization_scheduler() -> None:
    """
    Stop the continuous synchronization scheduler.
    """

    synchronization_service.stop_continuous_sync()


# ----------------------------------------------------------
# FastAPI Lifecycle
# ----------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start and stop application background services.
    """

    # Make the same synchronization service available
    # to API endpoints.
    app.state.synchronization_service = (
        synchronization_service
    )

    start_synchronization_scheduler()

    yield

    stop_synchronization_scheduler()


app = FastAPI(
    title="LogLlamalyzer API",
    description="API for LLM-based security log analysis.",
    version="1.0.0",
    lifespan=lifespan,
)


# ----------------------------------------------------------
# CORS Configuration
# ----------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8001",
        "http://localhost:8001",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------
# Routers
# ----------------------------------------------------------

app.include_router(status_router)
app.include_router(analysis_router)
app.include_router(server_router)


# ----------------------------------------------------------
# Root Endpoint
# ----------------------------------------------------------

@app.get("/")
def root():
    """
    Basic API health endpoint.
    """

    return {
        "application": "LogLlamalyzer",
        "status": "running",
        "version": "1.0.0",
    }


# ----------------------------------------------------------
# Health Endpoint
# ----------------------------------------------------------

@app.get("/health")
def health():
    """
    API health check.
    """

    return {
        "status": "healthy",
    }