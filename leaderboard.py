import streamlit as st
import requests
import time

# ======================================================
# FIREBASE REST CONFIG
# ======================================================
PROJECT_ID = "event-organiser-3cbca"
API_KEY = "AIzaSyBzvvf22QUsTKFStQXRlSXz93TgvLc5No8"
COLLECTION = "teams"

REFRESH_SECONDS = 1.2  # smooth & safe

# ======================================================
# PAGE CONFIG (PROJECTOR MODE)
# ======================================================
st.set_page_config(
    page_title="IQUEST | Live Leaderboard",
    layout="wide"
)

# ======================================================
# ULTRA-PREMIUM GOLD UI
# ======================================================
st.markdown("""
<style>
/* ---------- BACKGROUND ---------- */
.main {
    background:
        radial-gradient(circle at top, #fff4c2 0%, #e6b800 25%, #5c4300 55%, #050505 100%);
    color: #fff;
    font-family: 'Segoe UI', sans-serif;
}

/* ---------- TITLE ---------- */
.title {
    text-align: center;
    font-size: 4rem;
    font-weight: 900;
    letter-spacing: 4px;
    background: linear-gradient(90deg, #fff6b7, #ffd700, #fff6b7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 35px;
    text-shadow: 0 0 30px rgba(255,215,0,0.6);
}

/* ---------- BOARD ---------- */
.board {
    max-width: 1050px;
    margin: auto;
}

/* ---------- ROW ---------- */
.row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 22px 30px;
    margin-bottom: 16px;
    border-radius: 20px;
    background:
        linear-gradient(135deg,
            rgba(255,255,255,0.25),
            rgba(255,215,0,0.12),
            rgba(0,0,0,0.35));
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,215,0,0.55);
    box-shadow:
        inset 0 0 20px rgba(255,215,0,0.25),
        0 15px 40px rgba(0,0,0,0.6);
    animation: slideIn 0.6s ease;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.row:hover {
    transform: scale(1.015);
    box-shadow:
        inset 0 0 30px rgba(255,215,0,0.45),
        0 25px 60px rgba(0,0,0,0.8);
}

/* ---------- RANK BADGE ---------- */
.rank {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: 900;
    background:
        radial-gradient(circle at top, #fff7cc, #d4af37, #8b6b00);
    color: #1a1400;
    box-shadow:
        inset 0 0 15px rgba(255,255,255,0.6),
        0 0 25px rgba(255,215,0,0.8);
}

/* ---------- TEAM ---------- */
.team {
    flex-grow: 1;
    padding-left: 25px;
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    text-shadow: 0 0 8px rgba(255,215,0,0.4);
}

/* ---------- SCORE ---------- */
.score {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(180deg, #fff6b7, #ffd700, #cfa300);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(255,215,0,0.8);
}

/* ---------- TOP 3 SPECIAL ---------- */
.gold { animation: glowPulse 2s infinite; }
.silver { opacity: 0.95; }
.bronze { opacity: 0.9; }

/* ---------- ANIMATIONS ---------- */
@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes glowPulse {
    0% { box-shadow: 0 0 30px rgba(255,215,0,0.5); }
    50% { box-shadow: 0 0 60px rgba(255,215,0,0.9); }
    100% { box-shadow: 0 0 30px rgba(255,215,0,0.5); }
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# FIRESTORE REST FETCH (FAST)
# ======================================================
def extract_number(field):
    if not field:
        return 0
    if "integerValue" in field:
        return int(field["integerValue"])
    if "stringValue" in field:
        try:
            return int(field["stringValue"])
        except:
            return 0
    return 0


@st.cache_data(ttl=1, show_spinner=False)
def fetch_teams():
    url = (
        f"https://firestore.googleapis.com/v1/projects/"
        f"{PROJECT_ID}/databases/(default)/documents/{COLLECTION}"
        f"?key={API_KEY}"
    )
    try:
        res = requests.get(url, timeout=4)
        docs = res.json().get("documents", [])
    except Exception:
        return []

    teams = []
    for doc in docs:
        fields = doc.get("fields", {})
        name = fields.get("team_name", {}).get("stringValue", "")
        score = extract_number(fields.get("total_score"))
        if name:
            teams.append({"name": name, "score": score})

    teams.sort(key=lambda x: x["score"], reverse=True)
    return teams

# ======================================================
# RENDER
# ======================================================
teams = fetch_teams()

st.markdown("<div class='title'>🏆 IQUEST LEADERBOARD</div>", unsafe_allow_html=True)
st.markdown("<div class='board'>", unsafe_allow_html=True)

for i, team in enumerate(teams[:15]):
    cls = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
    st.markdown(
        f"""
        <div class="row {cls}">
            <div class="rank">#{i+1}</div>
            <div class="team">{team['name']}</div>
            <div class="score">{team['score']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CONTROLLED REFRESH (NO FLICKER)
# ======================================================
time.sleep(REFRESH_SECONDS)
st.rerun()
