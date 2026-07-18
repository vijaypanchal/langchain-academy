"""Utility module to load environment variables from the root .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    """
    Load environment variables from the local .env file.

    This function looks for a .env file in the project root, the current
    working directory, and the parent directories of the repository.
    """
    current_dir = Path(__file__).resolve().parent.parent
    candidates = [Path.cwd() / ".env", current_dir / ".env"]

    for parent in [current_dir, *current_dir.parents]:
        candidates.append(parent / ".env")

    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path, override=False)
            return

    load_dotenv(override=False)


# Load environment variables when this module is imported
load_env()