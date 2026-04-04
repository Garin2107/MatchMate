import streamlit as st
import pandas as pd
from datetime import date
from api import (
    get_fixtures_by_date,
    get_fixture_events, get_fixture_stats, get_lineups,
    get_basketball_by_date,
    get_baseball_by_date,
    get_americanfootball_by_date,
    get_baseball_lineups,
)
from supabase import create_client


def clean(val):
    if val is None:
        return "-"
    try:
        return str(val)
    except:
        return "-"


st.set_page_config(page_title="🏆 MatchMate", page_icon="🏆", layout="wide")
st.title("🏆 MatchMate — Segunda Pantalla")
st.caption("Datos en tiempo real mientras ves el partido en TV")


@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("🔍 Buscar partido")
st.sidebar.info("ℹ️ Modo en vivo requiere plan Pro de API-Sports.")

DEPORTES = {
    "⚽ Fútbol":            "football",
    "🏀 Basketball":        "basketball",
    "⚾ Béisbol":           "baseball",
    "🏈 Fútbol Americano":  "americanfootball",
}
selected_deporte_label = st.sidebar.selectbox("Deporte", list(DEPORTES.keys()))
deporte = DEPORTES[selected_deporte_label]

selected_date = st.sidebar.date_input("Fecha", value=date.today())

LIGAS = {
    "football": {
        "Primera División Chile": 265,
        "Segunda División Chile": 266,
        "Liga MX": 262,
        "Premier League": 39,
        "La Liga": 140,
        "Serie A": 135,
        "Bundesliga": 78,
        "Ligue 1": 61,
        "Champions League": 2,
        "Todas las ligas": None,
    },
    "basketball": {
        "NBA": 12,
        "Euroleague": 120,
        "Todas las ligas": None,
    },
    "baseball": {
        "MLB": 1,
        "Todas las ligas": None,
    },
    "americanfootball": {
        "NFL": 1,
        "NCAA": 2,
        "Todas las ligas": None,
    },
}

ligas_deporte = LIGAS.get(deporte, {"Todas las ligas": None})
selected_liga  = st.sidebar.selectbox("Liga", list(ligas_deporte.keys()))
league_id      = ligas_deporte[selected_liga]


# ── Obtener fixtures ──────────────────────────────────────────────────────────
def get_fixtures(deporte, selected_date, league_id=None):
    if deporte == "football":
        return get_fixtures_by_date(str(selected_date), league_id)
    elif deporte == "basketball":
        return get_basketball_by_date(str(selected_date), league_id)
    elif deporte == "baseball":
        return get_baseball_by_date(str(selected_date), league_id)
    elif deporte == "americanfootball":
        return get_americanfootball_by_date(str(selected_date), league_id)
    return []


fixtures = get_fixtures(deporte, selected_date, league_id)

# ── Validar ANTES de construir el selectbox de partidos ──────────────────────
if not fixtures:
    st.warning("No hay partidos disponibles para esta fecha y liga.")
    st.stop()

st.sidebar.success(f"{len(fixtures)} partido(s) encontrados")


# ── Labels de partidos ────────────────────────────────────────────────────────
partido_labels = []
for f in fixtures:
    home    = f["teams"]["home"]["name"]
    away    = f["teams"]["away"]["name"]
    score_h = f["goals"]["home"] if f["goals"]["home"] is not None else "-"
    score_a = f["goals"]["away"] if f["goals"]["away"] is not None else "-"
    minuto  = f["fixture"]["status"]["elapsed"]
    min_str = f" ({minuto}')" if minuto else ""
    partido_labels.append(f"{home} {score_h} - {score_a} {away}{min_str}")

selected_idx = st.sidebar.selectbox(
    "Partido", range(len(partido_labels)),
    format_func=lambda i: partido_labels[i]
)

fixture    = fixtures[selected_idx]
fixture_id = fixture["fixture"]["id"]

home    = fixture["teams"]["home"]["name"]
away    = fixture["teams"]["away"]["name"]
score_h = fixture["goals"]["home"] if fixture["goals"]["home"] is not None else 0
score_a = fixture["goals"]["away"] if fixture["goals"]["away"] is not None else 0
status  = fixture["fixture"]["status"]["long"]
minuto  = fixture["fixture"]["status"]["elapsed"]


# ── Header del partido ────────────────────────────────────────────────────────
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
            "Tipo":    [clean(e.get("type"))                          for e in events],
            "Detalle": [clean(e.get("detail"))                        for e in events],
            "Jugador": [clean(e.get("player", {}).get("name"))        for e in events],
            "Equipo":  [clean(e.get("team", {}).get("name"))          for e in events],
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
            "Estadística": [clean(k)                 for k in keys],
            home:          [clean(home_stats.get(k)) for k in keys],
            away:          [clean(away_stats.get(k)) for k in keys],
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Estadísticas no disponibles aún.")


# ── Tab 3: Alineaciones ───────────────────────────────────────────────────────
with tab3:

    if deporte == "football":
        lineups = get_lineups(fixture_id)
        if lineups:
            col_h, col_a = st.columns(2)
            for i, team_lineup in enumerate(lineups[:2]):
                col = col_h if i == 0 else col_a
                with col:
                    st.subheader(team_lineup["team"]["name"])
                    st.caption(f"⚙️ Formación: {team_lineup.get('formation', '-')}")

                    start_xi = team_lineup.get("startXI", [])
                    if start_xi:
                        st.markdown("**🟢 Once titular**")
                        data = {
                            "#":       [clean(p["player"].get("number")) for p in start_xi],
                            "Jugador": [clean(p["player"].get("name"))   for p in start_xi],
                            "Pos":     [clean(p["player"].get("pos"))    for p in start_xi],
                        }
                        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

                    substitutes = team_lineup.get("substitutes", [])
                    if substitutes:
                        with st.expander("🔄 Suplentes"):
                            data_s = {
                                "#":       [clean(p["player"].get("number")) for p in substitutes],
                                "Jugador": [clean(p["player"].get("name"))   for p in substitutes],
                                "Pos":     [clean(p["player"].get("pos"))    for p in substitutes],
                            }
                            st.dataframe(pd.DataFrame(data_s), use_container_width=True, hide_index=True)

                    coach = team_lineup.get("coach", {})
                    if coach.get("name"):
                        st.caption(f"🧑‍💼 DT: {coach['name']}")
        else:
            st.info("Alineaciones no disponibles para este partido.")

    elif deporte == "baseball":
        lineups = get_baseball_lineups(fixture_id)
        if lineups:
            col_h, col_a = st.columns(2)
            for i, team_data in enumerate(lineups[:2]):
                col = col_h if i == 0 else col_a
                with col:
                    team_name = team_data.get("team", {}).get("name", f"Equipo {i+1}")
                    st.subheader(team_name)

                    pitchers = team_data.get("pitchers", [])
                    if pitchers:
                        starter = pitchers[0]
                        st.markdown("**⚾ Pitcher abridor**")
                        st.markdown(f"- {clean(starter.get('name'))}  #{clean(starter.get('number'))}")

                    if len(pitchers) > 1:
                        with st.expander("🔁 Bullpen"):
                            for p in pitchers[1:]:
                                st.markdown(f"- {clean(p.get('name'))}  #{clean(p.get('number'))}")

                    batters = team_data.get("batters", [])
                    if batters:
                        st.markdown("**🏏 Orden al bate**")
                        data_b = {
                            "Turno":   [clean(b.get("order"))  for b in batters],
                            "Jugador": [clean(b.get("name"))   for b in batters],
                            "Pos":     [clean(b.get("pos"))    for b in batters],
                            "#":       [clean(b.get("number")) for b in batters],
                        }
                        st.dataframe(pd.DataFrame(data_b), use_container_width=True, hide_index=True)

                    if not pitchers and not batters:
                        st.info("Sin datos de alineación.")
        else:
            st.info("Alineaciones no disponibles para este partido de béisbol.")

    else:
        st.info(f"Alineaciones no disponibles para {selected_deporte_label}.")


# ── Tab 4: Predictor multijugador ─────────────────────────────────────────────
with tab4:
    st.subheader("🎯 Predictor multijugador")

    usuario = st.text_input("Tu nombre o apodo", placeholder="Ej: Antonio")

    with st.form("prediccion"):
        pred_gol       = st.radio("Próximo en anotar:", [home, away, "Nadie"])
        pred_resultado = st.selectbox("Resultado final:", [f"Gana {home}", f"Gana {away}", "Empate"])
        pred_goles     = st.slider("Total de puntos/goles:", 0, 150 if deporte == "basketball" else 30, 2)
        submitted      = st.form_submit_button("✅ Enviar predicción")

    if submitted and usuario:
        supabase.table("predicciones").insert({
            "usuario":     usuario,
            "fixture_id":  fixture_id,
            "deporte":     deporte,
            "resultado":   pred_resultado,
            "proximo_gol": pred_gol,
            "total_goles": pred_goles,
        }).execute()
        st.success(f"¡Predicción guardada, {usuario}!")
        st.balloons()
    elif submitted and not usuario:
        st.warning("Ingresa tu nombre antes de enviar.")

    st.subheader("📊 Predicciones del grupo")
    response = supabase.table("predicciones").select("*").eq("fixture_id", fixture_id).execute()
    if response.data:
        df_pred = pd.DataFrame(response.data)[["usuario", "resultado", "proximo_gol", "total_goles"]]
        df_pred.columns = ["Usuario", "Resultado", "Próx. anotador", "Total puntos/goles"]
        st.dataframe(df_pred.astype(str), use_container_width=True, hide_index=True)
    else:
        st.info("Nadie ha predicho aún. ¡Sé el primero!")


# ── Alerta de gol/punto nuevo ─────────────────────────────────────────────────
if "ultimo_marcador" not in st.session_state:
    st.session_state.ultimo_marcador = (score_h, score_a)

marcador_actual = (score_h, score_a)
if marcador_actual != st.session_state.ultimo_marcador:
    emoji = {"football": "⚽", "basketball": "🏀", "baseball": "⚾", "americanfootball": "🏈"}.get(deporte, "🏆")
    st.toast(f"{emoji} ¡PUNTO/GOL! {home} {score_h} - {score_a} {away}", icon=emoji)
    st.session_state.ultimo_marcador = marcador_actual