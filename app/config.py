import json

# Load configuration once
def load_config(config_path="config.json"):
    """Load configuration from a JSON file."""
    with open(config_path, "r") as file:
        return json.load(file)
config = load_config()

SECRET_KEY = config.get("secret_key", "default-secret-key") 

def get_config():
    return config
