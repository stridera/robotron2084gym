""" Configuration file for Robotron. """
from os import path
from typing import Any, Optional
import yaml


class Config:
    """ Load and manage the configuration file. """

    # Required configuration keys that must be present
    REQUIRED_KEYS = [
        'screen_size',
        'play_area',
        'waves',
        'resource_path',
        'extra_life_score'
    ]

    def __init__(self, config_path: Optional[str] = None):
        """
        Load and validate the configuration file.

        Args:
            config_path: Path to the config YAML file. Defaults to config.yaml in this directory.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If required keys are missing from config
            yaml.YAMLError: If config file is not valid YAML
        """
        if config_path is None:
            config_path = path.join(path.dirname(__file__), "config.yaml")

        if not path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)  # Use safe_load instead of FullLoader
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing configuration file: {e}") from e

        self._validate()

    def _validate(self):
        """
        Validate that all required configuration keys are present.

        Raises:
            ValueError: If required keys are missing
        """
        if self.config is None:
            raise ValueError("Configuration file is empty")

        missing_keys = [key for key in self.REQUIRED_KEYS if key not in self.config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key: The configuration key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)
