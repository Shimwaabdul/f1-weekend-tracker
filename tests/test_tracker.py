"""Tests for API fetching, formatting, and the command-line interface."""

import hashlib

import pytest
import requests

from f1tracker.api import APIError, get_json
from f1tracker.cli import main
from f1tracker.formatting import format_results, format_standings
from f1tracker.next_race import format_next_race, to_kigali_time


def test_get_json_saves_response_to_cache(tmp_path, monkeypatch):
    class Response:
        def raise_for_status(self): pass
        def json(self): return {"MRData": {"ok": True}}

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: Response())
    assert get_json("current/next.json", tmp_path) == {"MRData": {"ok": True}}
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_get_json_uses_cache_when_api_fails(tmp_path, monkeypatch, capsys):
    def fail_request(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", fail_request)
    cache = tmp_path / f"{hashlib.sha256(b'current/next.json').hexdigest()}.json"
    cache.write_text('{"cached": true}', encoding="utf-8")
    assert get_json("current/next.json", tmp_path) == {"cached": True}
    assert "cached data" in capsys.readouterr().err


def test_get_json_reports_failure_without_cache(tmp_path, monkeypatch):
    def fail_request(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", fail_request)
    with pytest.raises(APIError, match="Could not fetch"):
        get_json("current/next.json", tmp_path)


def test_kigali_time_conversion():
    assert to_kigali_time("2026-11-08", "17:00:00Z") == "Sun 08 Nov 2026, 19:00"


def test_format_next_race_includes_available_sessions():
    race = {"raceName": "Grand Prix", "Circuit": {"Location": {"locality": "Kigali", "country": "Rwanda"}},
            "FirstPractice": {"date": "2026-11-06", "time": "15:30:00Z"},
            "date": "2026-11-08", "time": "17:00:00Z"}
    output = format_next_race(race)
    assert "Practice 1: Fri 06 Nov 2026, 17:30" in output
    assert "Race: Sun 08 Nov 2026, 19:00" in output
    assert "Qualifying:" not in output


def test_format_results_aligned_table():
    payload = {"MRData": {"RaceTable": {"Races": [{"raceName": "Grand Prix", "season": "2026",
        "Results": [{"position": "1", "Driver": {"givenName": "Ada", "familyName": "Driver"},
                     "Constructor": {"name": "Team"}, "points": "25", "status": "Finished"}]}]}}}
    output = format_results(payload)
    assert "Grand Prix - 2026" in output
    assert "Ada Driver" in output
    assert "Pos | Driver" in output


def test_format_standings_table():
    payload = {"MRData": {"StandingsTable": {"StandingsLists": [{"DriverStandings": [
        {"position": "1", "points": "25", "wins": "1",
         "Driver": {"givenName": "Ada", "familyName": "Driver"},
         "Constructors": [{"name": "Team"}]}]}]}}}
    output = format_standings(payload)
    assert "Pos | Driver" in output
    assert "Ada Driver" in output


def test_format_empty_standings():
    assert format_standings({"MRData": {"StandingsTable": {"StandingsLists": []}}}) == (
        "No driver standings are available yet."
    )


def test_cli_results_command(monkeypatch, capsys):
    payload = {"MRData": {"RaceTable": {"Races": []}}}
    monkeypatch.setattr("f1tracker.cli.get_json", lambda endpoint: payload)
    assert main(["results"]) == 0
    assert "No race results are available yet." in capsys.readouterr().out


def test_cli_reports_api_error(monkeypatch, capsys):
    def fail_request():
        raise APIError("offline")

    monkeypatch.setattr("f1tracker.cli.fetch_next_race", fail_request)
    assert main(["next"]) == 1
    assert "Error: offline" in capsys.readouterr().err
