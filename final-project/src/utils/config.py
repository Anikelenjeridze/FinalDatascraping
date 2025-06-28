import yaml
from pathlib import Path

def load_config(file_name="settings.yaml"):
    """Loads a YAML configuration file from the config directory."""
    config_path = Path(__file__).parent.parent.parent / "config" / file_name
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Load configurations once
SETTINGS = load_config("settings.yaml")
SCRAPERS_CONFIG = load_config("scrapers.yaml")