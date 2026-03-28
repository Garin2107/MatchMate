import streamlit as st
import pandas as pd
from datetime import date
from api import get_live_fixtures, get_fixtures_by_date, get_fixture_events, get_fixture_stats, get_lineups
from supabase import create_client
import time


# ── Función de limpieza global ────────────────────────────────────────────────
def clean(val):
    """Convierte cualquier valor a string seguro para pandas."""
    if val is None:
        return "-"
    try:
        return str(val)
    except:
        return "-"


st.set_page_config(page_title="⚽ MatchMate", page_icon="⚽", layout="wide")
st.title("⚽ MatchMate — Segunda Pantalla")
st.caption("Datos en tiempo real mientras ves el partido en TV")


# ── Conexión Supabase (st.secrets, compatible con Streamlit Cloud) ────────────
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()


st.sidebar.header("🔍 Buscar partido")
mode = st.sidebar.radio("Modo", ["🔴 En vivo ahora", "📅 Por fecha"])


LIGAS_CHILE = {
    "Primera División Chile": 265,
    "Segunda División Chile": 266,
    "Todas las ligas": None
}
selected_liga = st.sidebar.selectbox("Liga", list(LIGAS_CHILE.keys()))
league_id = LIGAS_CHILE[selected_liga]


if mode == "🔴 En vivo ahora":
    fixtures = get_live_fixtures()
    st.sidebar.success(f"{len(fixtures)} partido(s) en vivo")
else:
    selected_date = st.sidebar.date_input("Fecha", value=date.today())
    fixtures = get_fixtures_by_date(str(selected_date), league_id)


if league_id and mode == "🔴 En vivo ahora":
    fixtures = [f for f in fixtures if f["league"]["id"] == league_id]


if not fixtures:
    st.warning("No hay partidos disponibles.")
    st.stop()


partido_labels = []
for f in fixtures:
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    score_h = f["goals"]["home"] if f["goals"]["home"] is not None else "-"
    score_a = f["goals"]["away"] if f["goals"]["away"] is not None else "-"
    minuto = f["fixture"]["status"]["elapsed"]
    min_str = f" ({minuto}')" if minuto else ""
    partido_labels.append(f"{home} {score_h} - {score_a} {away}{min_str}")


selected_idx = st.sidebar.selectbox("Partido", range(len(partido_labels)), format_func=lambda i: partido_labels[i])
fixture = fixtures[selected_idx]
fixture_id = fixture["fixture"]["id"]


home = fixture["teams"]["home"]["name"]
away = fixture["teams"]["away"]["name"]
score_h = fixture["goals"]["home"] if fixture["goals"]["home"] is not None else 0
score_a = fixture["goals"]["away"] if fixture["goals"]["away"] is not None else 0
status = fixture["fixture"]["status"]["long"]
minuto = fixture["fixture"]["status"]["elapsed"]


col1, col2, col3 = st.columns([3, 1, 3])
with col1:
    st.markdown(f"### 🏠 {home}")
with col2:
    st.markdown(f"## {score_h} — {score_a}")
    if minuto:
        st.markdown(f"**{minuto}'** ⏱️")
    st.caption(status)
with col3:
    st.markdown(f"### ✈️ {away}")


st.divider()


tab1, tab2, tab3, tab4 = st.tabs(["📋 Eventos", "📊 Estadísticas", "👥 Alineaciones", "🎯 Predictor"])


# ── Tab 1: Eventos ────────────────────────────────────────────────────────────
with tab1:
    events = get_fixture_events(fixture_id)
    if events:
        data = {
            "Min":     [clean(e.get("time", {}).get("elapsed")) + "'" for e in events],
            "Tipo":    [clean(e.get("type")) for e in events],
            "Detalle": [clean(e.get("detail")) for e in events],
            "Jugador": [clean(e.get("player", {}).get("name")) for e in events],
            "Equipo":  [clean(e.get("team", {}).get("name")) for e in events],
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Sin eventos registrados aún.")


# ── Tab 2: Estadísticas ───────────────────────────────────────────────────────
with tab2:
    stats = get_fixture_stats(fixture_id)
    if len(stats) >= 2:
        home_stats = {s["type"]: s["value"] for s in stats[0]["statistics"]}
        away_stats = {s["type"]: s["value"] for s in stats[1]["statistics"]}
        keys = list(home_stats.keys())
        data = {
            "Estadística": [clean(k) for k in keys],
            home:          [clean(home_stats.get(k)) for k in keys],
            away:          [clean(away_stats.get(k)) for k in keys],
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Estadísticas no disponibles aún.")


# ── Tab 3: Alineaciones ───────────────────────────────────────────────────────
with tab3:
    lineups = get_lineups(fixture_id)
    if lineups:
        col_h, col_a = st.columns(2)
        for i, team_lineup in enumerate(lineups[:2]):
            col = col_h if i == 0 else col_a
            with col:
                st.subheader(team_lineup["team"]["name"])
                st.caption(f"Formación: {team_lineup['formation']}")
                data = {
                    "#":       [clean(p["player"]["number"]) for p in team_lineup["startXI"]],
                    "Jugador": [clean(p["player"]["name"]) for p in team_lineup["startXI"]],
                    "Pos":     [clean(p["player"]["pos"]) for p in team_lineup["startXI"]],
                }
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Alineaciones no disponibles.")


# ── Tab 4: Predictor multijugador ─────────────────────────────────────────────
with tab4:
    st.subheader("🎯 Predictor multijugador")

    usuario = st.text_input("Tu nombre o apodo", placeholder="Ej: Antonio")

    with st.form("prediccion"):
        pred_gol = st.radio("Próximo en marcar:", [home, away, "Nadie"])
        pred_resultado = st.selectbox("Resultado final:", [f"Gana {home}", f"Gana {away}", "Empate"])
        pred_goles = st.slider("Total de goles:", 0, 10, 2)
        submitted = st.form_submit_button("✅ Enviar predicción")

    if submitted and usuario:
        supabase.table("predicciones").insert({
            "usuario": usuario,
            "fixture_id": fixture_id,
            "resultado": pred_resultado,
            "proximo_gol": pred_gol,
            "total_goles": pred_goles
        }).execute()
        st.success(f"¡Predicción guardada, {usuario}!")
        st.balloons()
    elif submitted and not usuario:
        st.warning("Ingresa tu nombre antes de enviar.")

    st.subheader("📊 Predicciones del grupo")
    response = supabase.table("predicciones").select("*").eq("fixture_id", fixture_id).execute()
    if response.data:
        df_pred = pd.DataFrame(response.data)[["usuario", "resultado", "proximo_gol", "total_goles"]]
        df_pred.columns = ["Usuario", "Resultado", "Próx. gol", "Total goles"]
        st.dataframe(df_pred.astype(str), use_container_width=True, hide_index=True)
    else:
        st.info("Nadie ha predicho aún. ¡Sé el primero!")


# Auto-refresh cada 30 segundos solo si hay partido en vivo
if mode == "🔴 En vivo ahora":
    st.sidebar.caption("🔄 Actualizando cada 30 segundos...")
    time.sleep(30)
    st.rerun()


# Detectar goles nuevos y alertar
if "ultimo_marcador" not in st.session_state:
    st.session_state.ultimo_marcador = (score_h, score_a)

marcador_actual = (score_h, score_a)
if marcador_actual != st.session_state.ultimo_marcador:
    st.toast(f"⚽ ¡GOL! Nuevo marcador: {home} {score_h} - {score_a} {away}", icon="⚽")
    st.session_state.ultimo_marcador = marcador_actual