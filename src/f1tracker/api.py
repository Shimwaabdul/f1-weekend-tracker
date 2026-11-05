"""HTTP access and simple on-disk caching for the Jolpica API."""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
CACHE_DIR = Path.home() / ".f1tracker-cache"


class APIError(Exception):
    """Raised when API data cannot be fetched or read."""


def get_json(endpoint: str, cache_dir: Path = CACHE_DIR) -> dict[str, Any]:
    """Fetch a JSON endpoint, falling back to its cached response on failure."""
    cache_file = cache_dir / f"{hashlib.sha256(endpoint.encode()).hexdigest()}.json"
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", timeout=10)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("The API response was not a JSON object.")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(payload), encoding="utf-8")
        return payload
    except (requests.RequestException, ValueError) as api_error:
        if cache_file.exists():
            try:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                if not isinstance(cached, dict):
                    raise ValueError("Cached data is not a JSON object.")
            except (OSError, ValueError) as cache_error:
                raise APIError(f"API failed ({api_error}); cache is unreadable ({cache_error}).") from cache_error
            print("Warning: API unavailable; showing cached data.", file=sys.stderr)
            return cached
        raise APIError(f"Could not fetch {endpoint}: {api_error}") from api_error
    except OSError as error:
        raise APIError(f"Could not save API cache: {error}") from error
