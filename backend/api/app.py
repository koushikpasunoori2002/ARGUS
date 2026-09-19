"""
app.py

Main FastAPI application for ARGUS.
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
from backend.config.system_config import SystemConfig
from backend.synchronization.synchronization_service import (
    SynchronizationService,
)

from backend.api.log_type_endpoints import (
    router as log_type_router,
)


# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------

synchronization_logger = logging.getLogger(
    "backend.synchronization.synchronization_service"
)

synchronization_logger.setLevel(
    logging.INFO
)

synchronization_logger.propagate = False

if not synchronization_logger.handlers:

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        logging.INFO
    )

    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console_handler.setFormatter(
        console_formatter
    )

    synchronization_logger.addHandler(
        console_handler
    )


# ----------------------------------------------------------
# Configuration
# ----------------------------------------------------------

hosts_config = HostsConfig()

system_config = SystemConfig()


# ----------------------------------------------------------
# Synchronization Components
# ----------------------------------------------------------

synchronization_service = SynchronizationService()

synchronization_thread: threading.Thread | None = None

synchronization_enabled_by_user = False


def start_synchronization_scheduler() -> None:
    """
    Start the continuous synchronization scheduler using
    settings from system.config.
    """

    global synchronization_thread
    global synchronization_enabled_by_user

    if (
        synchronization_thread is not None
        and synchronization_thread.is_alive()
    ):
        synchronization_enabled_by_user = True

        synchronization_logger.info(
            "Synchronization is already running."
        )

        return

    synchronization_enabled = (
        system_config.is_enabled()
    )

    if not synchronization_enabled:

        synchronization_logger.info(
            "Synchronization is globally disabled "
            "in system.config."
        )

        synchronization_enabled_by_user = False

        return

    scheduler_check_interval = (
        system_config.get_scheduler_check_interval()
    )

    default_interval = (
        system_config.get_default_interval()
    )

    synchronization_logger.info(
        "System synchronization configuration loaded: "
        "enabled=%s, default_interval=%ss, "
        "scheduler_check_interval=%ss",
        synchronization_enabled,
        default_interval,
        scheduler_check_interval,
    )

    synchronization_thread = threading.Thread(
        target=synchronization_service.start_continuous_sync,
        kwargs={
            "sources_provider": hosts_config.get_all,
            "check_interval": float(
                scheduler_check_interval
            ),
        },
        daemon=True,
        name="LogLlamalyzer-Synchronization",
    )

    synchronization_thread.start()

    synchronization_enabled_by_user = True

    synchronization_logger.info(
        "Synchronization started by user."
    )


def stop_synchronization_scheduler() -> None:
    """
    Stop the continuous synchronization scheduler.
    """

    global synchronization_enabled_by_user

    synchronization_service.stop_continuous_sync()

    synchronization_enabled_by_user = False

    synchronization_logger.info(
        "Synchronization stopped by user."
    )


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

    # Make configuration managers available to the
    # application if other components need them.
    app.state.hosts_config = hosts_config
    app.state.system_config = system_config

    # Synchronization is intentionally NOT started
    # automatically. It is controlled from the frontend.
    synchronization_logger.info(
        "Application started with synchronization OFF."
    )

    yield

    # Always stop synchronization when the application
    # shuts down.
    stop_synchronization_scheduler()


app = FastAPI(
    title="ARGUS API",
    description="API for LLM-based security log analysis.",
    version="1.0.0",
    lifespan=lifespan,
)


# ----------------------------------------------------------
# Synchronization Control Endpoints
# ----------------------------------------------------------

@app.post("/sync/start")
def start_sync():
    """
    Start continuous log synchronization.
    """

    start_synchronization_scheduler()

    return {
        "enabled": synchronization_enabled_by_user,
        "status": "running"
        if synchronization_enabled_by_user
        else "stopped",
    }


@app.post("/sync/stop")
def stop_sync():
    """
    Stop continuous log synchronization.
    """

    stop_synchronization_scheduler()

    return {
        "enabled": False,
        "status": "stopped",
    }


@app.get("/sync/status")
def sync_status():
    """
    Return the current synchronization status.
    """

    running = (
        synchronization_thread is not None
        and synchronization_thread.is_alive()
    )

    return {
        "enabled": running,
        "status": "running"
        if running
        else "stopped",
    }


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
app.include_router(log_type_router)


# ----------------------------------------------------------
# Root Endpoint
# ----------------------------------------------------------

@app.get("/")
def root():
    """
    Basic API health endpoint.
    """

    return {
        "application": "ARGUS",
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