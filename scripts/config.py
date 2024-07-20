import json
import os

CONFIG_FILE = '../data/config.json'
DEFAULT_BASE_DIR = r'C:\StableDiffusion\sd.webui\webui\outputs\txt2img-images'
DEFAULT_OUTPUT_DIR = r'C:\outputs'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'base_dir': DEFAULT_BASE_DIR,
            'output_dir': DEFAULT_OUTPUT_DIR
        }
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
