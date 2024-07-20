import json
import os
from scripts.gui import create_gui

CONFIG_FILE = 'data/config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        raise FileNotFoundError("Config file not found. Please ensure 'config.json' exists.")
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

if __name__ == "__main__":
    config = load_config()
    create_gui(config, save_config)
