import configparser
from pathlib import Path

def load_config(config_path: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

config_path = Path(__file__).parent / 'config.ini'
config = load_config(config_path)