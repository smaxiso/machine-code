import json
import os
from typing import Any

class ConfigLoader:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self, config_path="config.json"):
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    self._config = json.load(f)
                    print(f"[Config] Loaded configuration from {config_path}")
                except json.JSONDecodeError:
                    print(f"[Config] Error decoding {config_path}. Using defaults/empty.")
        else:
            print(f"[Config] Warning: {config_path} not found.")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
