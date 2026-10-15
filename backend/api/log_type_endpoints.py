# ARGUS: An LLM-RAG Guided Unified Reasoning System for Security Operational Centres
# Copyright 2026 Koushik Pasunoori and Dr Jose Maria Alcaraz Calero
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
