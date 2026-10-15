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
run_pipeline.py

Execute the preprocessing pipeline.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.preprocessing.pipeline import (
    PreprocessingPipeline,
)


def main():

    pipeline = PreprocessingPipeline()

    file_path = (
        PROJECT_ROOT
        / "dataset"
        / "raw"
        / "auth"
        / "auth.log"
    )

    info, records = (
        pipeline.process_with_metadata(file_path)
    )

    print("=" * 70)
    print("PIPELINE EXECUTION")
    print("=" * 70)

    print("Log type:", info.log_type)
    print("Records:", len(records))

    if records:
        print("\nFirst record:")
        print(records[0])


if __name__ == "__main__":
    main()
