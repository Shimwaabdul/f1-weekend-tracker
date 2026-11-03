"""Fetch and display the next Formula 1 race."""

from datetime import datetime
from zoneinfo import ZoneInfo

import requests

API_URL = "https://api.jolpi.ca/ergast/f1/current/next.json"
LOCAL_TIMEZONE = ZoneInfo("Africa/Kigali")


def fetch_next_race() -> dict[str, object]:
    """Return the next race details from the Jolpica API."""
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["MRData"]["RaceTable"]["Races"][0]


def to_kigali_time(date: str, time: str) -> str:
    """Convert a UTC date and time to a readable Kigali time."""
    utc_time = datetime.fromisoformat(f"{date}T{time.replace('Z', '+00:00')}")
    local_time = utc_time.astimezone(LOCAL_TIMEZONE)
    return local_time.strftime("%a %d %b %Y, %H:%M")


def main() -> None:
    """Print the next race and its scheduled sessions."""
    race = fetch_next_race()
    location = race["Circuit"]["Location"]
    print(f"Next race: {race['raceName']}")
    print(f"Location: {location['locality']}, {location['country']}")
    print(f"Date: {race['date']}")
    sessions = {
        "FirstPractice": "Practice 1", "SecondPractice": "Practice 2",
        "ThirdPractice": "Practice 3", "Sprint": "Sprint",
        "Qualifying": "Qualifying", "Race": "Race",
    }
    for key, label in sessions.items():
        session = race.get(key)
        if isinstance(session, dict):
            print(f"{label}: {to_kigali_time(session['date'], session['time'])}")


if __name__ == "__main__":
    main()
