#!/usr/bin/env python3
"""
Initialize configuration file with default values.
Run this script to create a fresh config.json file.
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def init_config(data_dir: Path = Path("./data")):
    """Initialize config.json with default values."""

    config_file = data_dir / "config.json"

    if config_file.exists():
        response = input(f"{config_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Default configuration
    config = {
        "bots": [],
        "global_timezone": "UTC",
        "default_upload_subfolder": "audio/",
        "theme": "light",
        "created_at": datetime.utcnow().isoformat()
    }

    # Create data directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)

    # Write config file
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Created {config_file}")
    print("\nDefault configuration:")
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = Path("./data")

    print(f"Initializing config in: {data_dir}")
    init_config(data_dir)
