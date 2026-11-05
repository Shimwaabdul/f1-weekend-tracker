# F1 Weekend Tracker

A Python command-line app that uses the free [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/) to show the next race, session times in `Africa/Kigali`, the latest race results, and driver standings.

## Setup (Windows PowerShell)

From the project folder, create and activate a virtual environment, then install the listed packages:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
```

`requests` is used for web requests and `pytest` runs the tests. The other modules used (`argparse`, `json`, and `zoneinfo`) are included with Python 3.9 or newer.

## Run a command

```powershell
python -m f1tracker next
python -m f1tracker results
python -m f1tracker standings
```

The `next` command converts available practice, sprint, qualifying, and race times from UTC to Kigali time. It uses the `Africa/Kigali` time-zone database when available; if Windows has no IANA time-zone database installed, it falls back to Kigali's UTC+02:00 offset (Kigali does not observe daylight-saving time). Commands use a saved JSON response if the API cannot be reached and a cache is available; cached data is stored in `.f1tracker-cache` under your home folder.

## Run the tests

```powershell
python -m pytest
```

Tests use mocked API responses, so they do not need an internet connection.
