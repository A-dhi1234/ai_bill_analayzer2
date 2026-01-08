import yaml
from groq import Groq
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
config_path = BASE_DIR / "config" / "config.yaml"

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

client = Groq(api_key=config["api_keys"]["groq"])
