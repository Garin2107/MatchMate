import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
BASE_URL = "https://v3.football.api-sports.io"

BASE_HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v1.basketball.api-sports.io"
}

# Alias para compatibilidad con funciones existentes
HEADERS = BASE_HEADERS

def get_live_fixtures():
    """Retorna todos los partidos en vivo en este momento."""
    res = requests.get(f"{BASE_URL}/fixtures?live=all", headers=HEADERS)
    return res.json().get("response", [])

def get_fixtures_by_date(date: str, league_id: int = None):
    """
    Retorna partidos de una fecha específica.
    date: formato 'YYYY-MM-DD'
    league_id: opcional, ej. 265 = Primera División Chile
    """
    params = {"date": date}
    if league_id:
        params["league"] = league_id
        params["season"] = 2025
    res = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS, params=params)
    return res.json().get("response", [])

def get_fixture_events(fixture_id: int):
    """Retorna los eventos de un partido (goles, tarjetas, sustituciones)."""
    res = requests.get(f"{BASE_URL}/fixtures/events?fixture={fixture_id}", headers=HEADERS)
    return res.json().get("response", [])

def get_fixture_stats(fixture_id: int):
    """Retorna estadísticas de un partido (posesión, tiros, etc.)."""
    res = requests.get(f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}", headers=HEADERS)
    return res.json().get("response", [])

def get_lineups(fixture_id: int):
    """Retorna alineaciones de ambos equipos."""
    res = requests.get(f"{BASE_URL}/fixtures/lineups?fixture={fixture_id}", headers=HEADERS)
    return res.json().get("response", [])

import requests

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
BASE_HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v1.basketball.api-sports.io"}


# ── Basketball (api-sports.io) ────────────────────────────────────────────────
def get_live_basketball():
    try:
        r = requests.get(
            "https://v1.basketball.api-sports.io/games",
            headers={**BASE_HEADERS, "x-rapidapi-host": "v1.basketball.api-sports.io"},
            params={"live": "all"}, timeout=10
        )
        return _normalize_basketball(r.json().get("response", []))
    except:
        return []

def get_basketball_by_date(date_str, league_id=None):
    try:
        params = {"date": date_str}
        if league_id:
            params["league"] = league_id
        r = requests.get(
            "https://v1.basketball.api-sports.io/games",
            headers={**BASE_HEADERS, "x-rapidapi-host": "v1.basketball.api-sports.io"},
            params=params, timeout=10
        )
        return _normalize_basketball(r.json().get("response", []))
    except:
        return []

def _normalize_basketball(games):
    """Normaliza respuesta de basketball al mismo formato que football."""
    normalized = []
    for g in games:
        normalized.append({
            "fixture": {
                "id": g.get("id"),
                "status": {
                    "long": g.get("status", {}).get("long", ""),
                    "elapsed": g.get("status", {}).get("timer"),
                }
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


# ── Baseball (api-sports.io) ──────────────────────────────────────────────────
def get_live_baseball():
    try:
        r = requests.get(
            "https://v1.baseball.api-sports.io/games",
            headers={**BASE_HEADERS, "x-rapidapi-host": "v1.baseball.api-sports.io"},
            params={"live": "all"}, timeout=10
        )
        return _normalize_baseball(r.json().get("response", []))
    except:
        return []

def get_baseball_by_date(date_str, league_id=None):
    try:
        params = {"date": date_str}
        if league_id:
            params["league"] = league_id
        r = requests.get(
            "https://v1.baseball.api-sports.io/games",
            headers={**BASE_HEADERS, "x-rapidapi-host": "v1.baseball.api-sports.io"},
            params=params, timeout=10
        )
        return _normalize_baseball(r.json().get("response", []))
    except:
        return []

def _normalize_baseball(games):
    normalized = []
    for g in games:
        normalized.append({
            "fixture": {
                "id": g.get("id"),
                "status": {
                    "long": g.get("status", {}).get("long", ""),
                    "elapsed": g.get("status", {}).get("inning"),
                }
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


# ── American Football (api-sports.io) ────────────────────────────────────────
def get_live_americanfootball():
    try:
        r = requests.get(
            "https://v1.american-football.api-sports.io/games",
            headers={**BASE_HEADERS, "x-rapidapi-host": "v1.american-football.api-sports.io"},
            params={"live": "all"}, timeout=10
        )
        return _normalize_americanfootball(r.json().get("response", []))
    except:
        return []

def get_americanfootball_by_date(date_str, league_id=None):
    try:
        params = {"date": date_str}
        if league_id:
            params["league"] = league_id
        r = requests.get(
            "https://v1.american-football.api-sports.io/games",
            headers={**BASE_HEADERS, "x-rapidapi-host": "v1.american-football.api-sports.io"},
            params=params, timeout=10
        )
        return _normalize_americanfootball(r.json().get("response", []))
    except:
        return []

def _normalize_americanfootball(games):
    normalized = []
    for g in games:
        normalized.append({
            "fixture": {
                "id": g.get("game", {}).get("id"),
                "status": {
                    "long": g.get("game", {}).get("status", {}).get("long", ""),
                    "elapsed": g.get("game", {}).get("status", {}).get("quarter"),
                }
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
