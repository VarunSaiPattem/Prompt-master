import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import re

# ======================================================
# FIREBASE INIT (LOCAL TEST MODE)
# ======================================================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="IQUEST | Participant Arena",
    layout="wide"
)

# ======================================================
# UI STYLES
# ======================================================
st.markdown("""
<style>
.main {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #e5e7eb;
}
h1, h2, h3 {
    color: #a78bfa !important;
    text-align: center;
}

/* LOGIN CARD */
.login-card {
    max-width: 420px;
    margin: auto;
    padding: 35px;
    border-radius: 18px;
    background: rgba(22,27,34,0.9);
    border: 1px solid rgba(167,139,250,0.35);
    box-shadow: 0 0 45px rgba(124,58,237,0.35);
}

/* QUESTION CARD */
.question-card {
    background: linear-gradient(180deg, #0b1220, #020617);
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 28px;
    border: 1px solid rgba(167,139,250,0.25);
    box-shadow: 0 0 25px rgba(124,58,237,0.18);
}

/* FIXED IMAGE (SMALL & NO CROPPING) */
.image-box {
    width: 100%;
    height: 200px;
    background-color: #020617;
    border-radius: 10px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
    border: 1px solid rgba(167,139,250,0.25);
}
.image-box img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(135deg, #6d28d9, #7c3aed);
    color: white;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SCORING FUNCTION
# ======================================================
def compute_score(user_prompt, golden_prompt, max_marks):
    user = user_prompt.lower().strip()
    golden = golden_prompt.lower().strip()

    length = len(user.split())
    length_score = 0.4 if length < 10 else 0.7 if length < 40 else 1.0

    gw = set(re.findall(r"\b\w+\b", golden))
    uw = set(re.findall(r"\b\w+\b", user))
    keyword_score = len(gw & uw) / len(gw) if gw else 0.4
    keyword_score = min(keyword_score, 0.95)

    structure_score = 0.0
    if "\n" in user_prompt: structure_score += 0.3
    if ":" in user_prompt: structure_score += 0.3
    if any(k in user for k in ["step", "format", "output", "constraint"]):
        structure_score += 0.4
    structure_score = min(structure_score, 1.0)

    normalized = (
        0.15 * length_score +
        0.60 * keyword_score +
        0.25 * structure_score
    )

    score = round(max_marks * normalized, 2)
    return max(1.0, min(score, max_marks))

# ======================================================
# TEAM RANK
# ======================================================
def get_team_rank(team_id):
    docs = db.collection("teams").stream()
    teams = []
    for d in docs:
        data = d.to_dict()
        teams.append({
            "id": d.id,
            "score": float(data.get("total_score", 0))
        })
    teams.sort(key=lambda x: x["score"], reverse=True)
    for i, t in enumerate(teams):
        if t["id"] == team_id:
            return i + 1, len(teams)
    return None, len(teams)

# ======================================================
# LOGIN
# ======================================================
if "team_id" not in st.session_state:
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.title("🚀 IQUEST | Team Login")

    team_id = st.text_input("Team ID").strip().upper()
    password = st.text_input("Team Password", type="password")

    if st.button("Enter Arena"):
        doc = db.collection("teams").document(team_id).get()
        if not doc.exists:
            st.error("Invalid Team ID")
        elif doc.to_dict().get("password") != password:
            st.error("Incorrect Password")
        else:
            st.session_state.team_id = team_id
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

team_id = st.session_state.team_id

# ======================================================
# TEAM POSITION
# ======================================================
rank, total = get_team_rank(team_id)
st.markdown(
    f"""
    <div style="text-align:center;margin-bottom:22px;
    background:linear-gradient(135deg,#1e293b,#020617);
    padding:14px;border-radius:14px;border:1px solid #7c3aed;">
        <div style="color:#c7d2fe;">🏆 Your Team Position</div>
        <div style="font-size:2.4rem;color:#a78bfa;font-weight:900;">#{rank}</div>
        <div style="color:#9ca3af;">out of {total} teams</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ======================================================
# GAME STATUS
# ======================================================
status = db.collection("config").document("status").get().to_dict()
if not status.get("is_active"):
    st.title("⏳ Waiting for IQUEST to Go Live")
    st.stop()

current_round = status.get("current_round")

# ======================================================
# ROUND DATA
# ======================================================
round_data = db.collection("rounds").document(
    f"round_{current_round}"
).get().to_dict()

questions = round_data.get("questions", [])
max_marks = round_data.get("max_marks", 50)

st.title(f"🔥 IQUEST | Round {current_round}")
st.caption(f"🎯 Max Marks per Question: {max_marks}")

# ======================================================
# QUESTIONS
# ======================================================
for i, q in enumerate(questions):
    qno = i + 1
    sid = f"{team_id}_R{current_round}_Q{qno}"
    ref = db.collection("submissions").document(sid)
    sub = ref.get()

    st.markdown("<div class='question-card'>", unsafe_allow_html=True)
    st.subheader(f"Question {qno}")

    if current_round in [1, 2] and q.get("image_url"):
        st.markdown(
            f"<div class='image-box'><img src='{q['image_url']}'></div>",
            unsafe_allow_html=True
        )

    if sub.exists:
        st.success(f"✅ Submitted | Score: {sub.to_dict().get('score')}")
    else:
        prompt = st.text_area("Enter your final prompt", height=130, key=sid)

        if st.button("🔒 Lock & Submit", key=f"btn_{sid}"):

            if ref.get().exists:
                st.error("Already submitted.")
                st.stop()

            score = compute_score(
                prompt,
                q.get("golden_prompt", ""),
                max_marks
            )

            ref.set({
                "team_id": team_id,
                "round": current_round,
                "question": qno,
                "prompt": prompt,
                "score": score,
                "submitted_at": firestore.SERVER_TIMESTAMP
            })

            db.collection("teams").document(team_id).update({
                "total_score": firestore.Increment(score)
            })

            st.success(f"Submitted successfully! Score: {score}")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
