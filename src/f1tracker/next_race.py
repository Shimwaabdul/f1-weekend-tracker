"""Fetch and display the next Formula 1 race."""

from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from f1tracker.api import APIError, get_json

try:
    LOCAL_TIMEZONE = ZoneInfo("Africa/Kigali")
except ZoneInfoNotFoundError:
    LOCAL_TIMEZONE = timezone(timedelta(hours=2), name="Africa/Kigali")


def fetch_next_race() -> dict[str, Any]:
    """Return the next race details from the Jolpica API."""
    data = get_json("current/next.json")
    mr_data = data.get("MRData")
    race_table = mr_data.get("RaceTable") if isinstance(mr_data, dict) else None
    races = race_table.get("Races") if isinstance(race_table, dict) else None
    if not isinstance(races, list) or not races or not isinstance(races[0], dict):
        raise APIError("The API did not return a next race.")
    return races[0]


def to_kigali_time(date: str, time: str) -> str:
    """Convert a UTC date and time to a readable Kigali time."""
    try:
        utc_time = datetime.fromisoformat(f"{date}T{time.replace('Z', '+00:00')}")
    except ValueError as error:
        raise APIError(f"Invalid session date or time: {date} {time}") from error
    local_time = utc_time.astimezone(LOCAL_TIMEZONE)
    return local_time.strftime("%a %d %b %Y, %H:%M")


def format_next_race(race: dict[str, Any]) -> str:
    """Format the next race and all sessions provided by the API."""
    try:
        location = race["Circuit"]["Location"]
        lines = [f"Next race: {race['raceName']}",
                 f"Location: {location['locality']}, {location['country']}"]
        sessions = [
            ("FirstPractice", "Practice 1"), ("SecondPractice", "Practice 2"),
            ("ThirdPractice", "Practice 3"), ("Sprint", "Sprint"),
            ("Qualifying", "Qualifying"),
        ]
        for key, label in sessions:
            session = race.get(key)
            if isinstance(session, dict):
                lines.append(f"{label}: {to_kigali_time(session['date'], session['time'])}")
        lines.append(f"Race: {to_kigali_time(race['date'], race['time'])}")
    except (KeyError, TypeError) as error:
        raise APIError("Unexpected API response: next race data is incomplete.") from error
    return "\n".join(lines)
