"""Formatting helpers for race results and championship standings."""

from typing import Any

from f1tracker.api import APIError


def _records(payload: dict[str, Any], table: str, key: str) -> list[dict[str, Any]]:
    """Return a list of records from a Jolpica response table."""
    mr_data = payload.get("MRData")
    data_table = mr_data.get(table) if isinstance(mr_data, dict) else None
    records = data_table.get(key) if isinstance(data_table, dict) else None
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise APIError(f"Unexpected API response: {table}.{key} is missing or invalid.")
    return records


def _table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a plain-text table with columns aligned to their contents."""
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    render = lambda row: " | ".join(value.ljust(widths[i]) for i, value in enumerate(row))
    divider = "-+-".join("-" * width for width in widths)
    return "\n".join([render(headers), divider, *(render(row) for row in rows)])


def format_results(payload: dict[str, Any]) -> str:
    """Format the latest race results as an aligned text table."""
    races = _records(payload, "RaceTable", "Races")
    if not races:
        return "No race results are available yet."
    race = races[0]
    results = race.get("Results", [])
    if not isinstance(results, list):
        raise APIError("Unexpected API response: race Results is invalid.")
    try:
        rows = []
        for result in results:
            driver = result["Driver"]
            rows.append([result["position"], f"{driver['givenName']} {driver['familyName']}",
                         result["Constructor"]["name"], result["points"], result["status"]])
        title = f"{race['raceName']} - {race['season']}"
    except (KeyError, TypeError) as error:
        raise APIError("Unexpected API response: race result data is incomplete.") from error
    return f"{title}\n{_table(['Pos', 'Driver', 'Team', 'Points', 'Status'], rows)}"


def format_standings(payload: dict[str, Any]) -> str:
    """Format the current driver standings as an aligned text table."""
    mr_data = payload.get("MRData")
    tables = mr_data.get("StandingsTable", {}) if isinstance(mr_data, dict) else {}
    lists = tables.get("StandingsLists", []) if isinstance(tables, dict) else []
    if not isinstance(lists, list) or not lists or not isinstance(lists[0], dict):
        return "No driver standings are available yet."
    standings = lists[0].get("DriverStandings", [])
    if not isinstance(standings, list):
        raise APIError("Unexpected API response: DriverStandings is invalid.")
    try:
        rows = []
        for entry in standings:
            driver = entry["Driver"]
            team = entry["Constructors"][0]["name"]
            rows.append([entry["position"], f"{driver['givenName']} {driver['familyName']}",
                         team, entry["points"], entry["wins"]])
    except (KeyError, IndexError, TypeError) as error:
        raise APIError("Unexpected API response: driver standing data is incomplete.") from error
    return _table(["Pos", "Driver", "Team", "Points", "Wins"], rows)
