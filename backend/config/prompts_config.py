"""
prompts_config.py

Loads and provides access to configurable prompts
stored in config/prompts.config.
"""

from __future__ import annotations

import json
from pathlib import Path


class PromptsConfig:
    """
    Loads prompt definitions from config/prompts.config.
    """

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = (
                Path(__file__).resolve().parents[2]
                / "config"
                / "prompts.config"
            )

        self.config_path = Path(config_path)
        self._config = self._load()

    def _load(self):
        """
        Load and validate the prompts configuration.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Prompts configuration file not found: "
                f"{self.config_path}"
            )

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            config = json.load(file)

        if not isinstance(config, dict):
            raise ValueError(
                "prompts.config must contain a JSON object."
            )

        prompts = config.get("prompts")

        if not isinstance(prompts, dict):
            raise ValueError(
                "prompts.config must contain a 'prompts' object."
            )

        for prompt_id, prompt_data in prompts.items():
            if not isinstance(prompt_data, dict):
                raise ValueError(
                    f"Prompt '{prompt_id}' must be an object."
                )

            if "name" not in prompt_data:
                raise ValueError(
                    f"Prompt '{prompt_id}' is missing 'name'."
                )

            if "template" not in prompt_data:
                raise ValueError(
                    f"Prompt '{prompt_id}' is missing 'template'."
                )

            if not isinstance(
                prompt_data["name"],
                str,
            ):
                raise ValueError(
                    f"Prompt '{prompt_id}' name must be a string."
                )

            if not isinstance(
                prompt_data["template"],
                str,
            ):
                raise ValueError(
                    f"Prompt '{prompt_id}' template must be a string."
                )

        return config

    def get_prompt(self, prompt_id):
        """
        Return one configured prompt.
        """
        prompts = self._config["prompts"]

        if prompt_id not in prompts:
            raise KeyError(
                f"Prompt '{prompt_id}' is not configured."
            )

        return prompts[prompt_id]

    def get_template(self, prompt_id):
        """
        Return only the template text for a prompt.
        """
        return self.get_prompt(prompt_id)["template"]

    def get_name(self, prompt_id):
        """
        Return the display name of a prompt.
        """
        return self.get_prompt(prompt_id)["name"]

    def get_all(self):
        """
        Return all configured prompts.
        """
        return self._config["prompts"]

    def info(self):
        """
        Return configuration metadata.
        """
        return {
            "component": "PromptsConfig",
            "config_path": str(self.config_path),
            "prompt_count": len(
                self._config["prompts"]
            ),
            "prompts": list(
                self._config["prompts"].keys()
            ),
        }

    def __repr__(self):
        return (
            "PromptsConfig("
            f"prompts={list(self._config['prompts'].keys())}"
            ")"
        )