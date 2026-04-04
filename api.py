import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")

# ── Football ──────────────────────────────────────────────────────────────────
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"   # ← bug original corregido
}
BASE_URL = "https://v3.football.api-sports.io"
BASE_HEADERS = {"x-rapidapi-key": API_KEY}


def get_live_fixtures():
    res = requests.get(f"{BASE_URL}/fixtures?live=all", headers=HEADERS)
    return res.json().get("response", [])


def get_fixtures_by_date(date: str, league_id: int = None):
    params = {"date": date}
    if league_id:
        params["league"] = league_id
        params["season"] = 2025
    res = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS, params=params)
    return res.json().get("response", [])


def get_fixture_events(fixture_id: int):
    res = requests.get(f"{BASE_URL}/fixtures/events?fixture={fixture_id}", headers=HEADERS)
    return res.json().get("response", [])


def get_fixture_stats(fixture_id: int):
    res = requests.get(f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}", headers=HEADERS)
    return res.json().get("response", [])


def get_lineups(fixture_id: int):
    res = requests.get(f"{BASE_URL}/fixtures/lineups?fixture={fixture_id}", headers=HEADERS)
    return res.json().get("response", [])


# ── Basketball ────────────────────────────────────────────────────────────────
_BB_HOST = "v1.basketball.api-sports.io"
_BB_HEADERS = {**BASE_HEADERS, "x-rapidapi-host": _BB_HOST}


def get_live_basketball():
    try:
        r = requests.get(f"https://{_BB_HOST}/games", headers=_BB_HEADERS,
                         params={"live": "all"}, timeout=10)
        return _normalize_basketball(r.json().get("response", []))
    except:
        return []


def get_basketball_by_date(date_str, league_id=None):
    try:
        params = {"date": date_str}
        if league_id:
            params["league"] = league_id
        r = requests.get(f"https://{_BB_HOST}/games", headers=_BB_HEADERS,
                         params=params, timeout=10)
        return _normalize_basketball(r.json().get("response", []))
    except:
        return []


def _normalize_basketball(games):
    normalized = []
    for g in games:
        normalized.append({
            "fixture": {
                "id": g.get("id"),
                "status": {"long": g.get("status", {}).get("long", ""),
                           "elapsed": g.get("status", {}).get("timer")},
            },
            "league": {"id": g.get("league", {}).get("id"), "name": g.get("league", {}).get("name")},
            "teams": {
                "home": {"name": g.get("teams", {}).get("home", {}).get("name", "")},
                "away": {"name": g.get("teams", {}).get("away", {}).get("name", "")},
            },
            "goals": {
                "home": g.get("scores", {}).get("home", {}).get("total"),
                "away": g.get("scores", {}).get("away", {}).get("total"),
            },
        })
    return normalized


# ── Baseball ──────────────────────────────────────────────────────────────────
_BSB_HOST = "v1.baseball.api-sports.io"
_BSB_HEADERS = {**BASE_HEADERS, "x-rapidapi-host": _BSB_HOST}


def get_live_baseball():
    try:
        r = requests.get(f"https://{_BSB_HOST}/games", headers=_BSB_HEADERS,
                         params={"live": "all"}, timeout=10)
        return _normalize_baseball(r.json().get("response", []))
    except:
        return []


def get_baseball_by_date(date_str, league_id=None):
    try:
        params = {"date": date_str}
        if league_id:
            params["league"] = league_id
        r = requests.get(f"https://{_BSB_HOST}/games", headers=_BSB_HEADERS,
                         params=params, timeout=10)
        return _normalize_baseball(r.json().get("response", []))
    except:
        return []


def _normalize_baseball(games):
    normalized = []
    for g in games:
        normalized.append({
            "fixture": {
                "id": g.get("id"),
                "status": {"long": g.get("status", {}).get("long", ""),
                           "elapsed": g.get("status", {}).get("inning")},
            },
            "league": {"id": g.get("league", {}).get("id"), "name": g.get("league", {}).get("name")},
            "teams": {
                "home": {"name": g.get("teams", {}).get("home", {}).get("name", "")},
                "away": {"name": g.get("teams", {}).get("away", {}).get("name", "")},
            },
            "goals": {
                "home": g.get("scores", {}).get("home", {}).get("total"),
                "away": g.get("scores", {}).get("away", {}).get("total"),
            },
        })
    return normalized


def get_baseball_lineups(fixture_id: int):
    """Obtiene alineación de béisbol (pitchers + batters por equipo)."""
    try:
        r = requests.get(f"https://{_BSB_HOST}/games/lineups", headers=_BSB_HEADERS,
                         params={"game": fixture_id}, timeout=10)
        return r.json().get("response", [])
    except:
        return []


# ── American Football ─────────────────────────────────────────────────────────
_AF_HOST = "v1.american-football.api-sports.io"
_AF_HEADERS = {**BASE_HEADERS, "x-rapidapi-host": _AF_HOST}


def get_live_americanfootball():
    try:
        r = requests.get(f"https://{_AF_HOST}/games", headers=_AF_HEADERS,
                         params={"live": "all"}, timeout=10)
        return _normalize_americanfootball(r.json().get("response", []))
    except:
        return []


def get_americanfootball_by_date(date_str, league_id=None):
    try:
        params = {"date": date_str}
        if league_id:
            params["league"] = league_id
        r = requests.get(f"https://{_AF_HOST}/games", headers=_AF_HEADERS,
                         params=params, timeout=10)
        return _normalize_americanfootball(r.json().get("response", []))
    except:
        return []


def _normalize_americanfootball(games):
    normalized = []
    for g in games:
        normalized.append({
            "fixture": {
                "id": g.get("game", {}).get("id"),
                "status": {"long": g.get("game", {}).get("status", {}).get("long", ""),
                           "elapsed": g.get("game", {}).get("status", {}).get("quarter")},
            },
            "league": {"id": g.get("league", {}).get("id"), "name": g.get("league", {}).get("name")},
            "teams": {
                "home": {"name": g.get("teams", {}).get("home", {}).get("name", "")},
                "away": {"name": g.get("teams", {}).get("away", {}).get("name", "")},
            },
            "goals": {
                "home": g.get("scores", {}).get("home", {}).get("total"),
                "away": g.get("scores", {}).get("away", {}).get("total"),
            },
        })
    return normalized