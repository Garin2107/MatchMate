import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

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