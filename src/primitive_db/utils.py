import json


def load_metadata(filepath):
    """Load table metadata from JSON, returning an empty dict if missing."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    """Save table metadata to a JSON file using UTF-8 encoding."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)