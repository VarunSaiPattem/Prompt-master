import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ======================================================
# FIREBASE INIT
# ======================================================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="IQUEST | Admin Command Center",
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
.login-card {
    max-width: 420px;
    margin: auto;
    padding: 36px;
    border-radius: 18px;
    background: rgba(22,27,34,0.9);
    border: 1px solid rgba(167,139,250,0.35);
    box-shadow: 0 0 45px rgba(124,58,237,0.35);
}
.round-card {
    background: linear-gradient(180deg, #0b1220, #020617);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 25px;
    border: 1px solid rgba(167,139,250,0.25);
}
.stButton > button {
    background: linear-gradient(135deg,#6d28d9,#7c3aed);
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# ADMIN LOGIN
# ======================================================
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.title("🛡️ IQUEST ADMIN LOGIN")
    pwd = st.text_input("Admin Password", type="password")
    if st.button("Unlock"):
        if pwd == "1234":  # CHANGE THIS
            st.session_state.admin_auth = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ======================================================
# HEADER
# ======================================================
st.title("🚀 IQUEST | Master Command Center")

# ======================================================
# GLOBAL CONTROLS
# ======================================================
with st.sidebar:
    st.header("🌐 Global Controls")

    status_ref = db.collection("config").document("status")
    status = status_ref.get().to_dict() or {
        "current_round": 1,
        "is_active": False
    }

    g_round = st.selectbox(
        "Active Round",
        [1, 2, 3],
        index=status["current_round"] - 1
    )

    g_live = st.toggle("Go Live", value=status["is_active"])

    if st.button("💾 Save Global State"):
        status_ref.set(
            {"current_round": g_round, "is_active": g_live},
            merge=True
        )
        st.success("Global state updated")

# ======================================================
# HELPERS
# ======================================================
def load_round(round_id):
    doc = db.collection("rounds").document(f"round_{round_id}").get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("questions", []), data.get("max_marks", 20)
    return [], 20

# ======================================================
# TABS
# ======================================================
t1, t2, t3 = st.tabs([
    "🖼️ Round 1 – Visual",
    "🚫 Round 2 – Forbidden",
    "💻 Round 3 – Code"
])

# ======================================================
# ROUND 1
# ======================================================
with t1:
    questions, max_marks = load_round(1)

    round_marks = st.number_input(
        "🏆 Max Marks for EACH Question in Round 1",
        1, 100, max_marks
    )

    count = st.number_input(
        "Number of Questions",
        1, 20,
        len(questions) if questions else 5
    )

    updated = []
    for i in range(count):
        q = questions[i] if i < len(questions) else {}
        st.markdown("<div class='round-card'>", unsafe_allow_html=True)
        st.subheader(f"Question {i+1}")

        img = st.text_input("Image URL", q.get("image_url", ""), key=f"r1_img{i}")
        gold = st.text_input("Golden Prompt", q.get("golden_prompt", ""), key=f"r1_gold{i}")

        updated.append({
            "image_url": img,
            "golden_prompt": gold
        })
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾 Save Round 1"):
        db.collection("rounds").document("round_1").set({
            "max_marks": round_marks,
            "questions": updated
        })
        st.success("Round 1 saved")

# ======================================================
# ROUND 2
# ======================================================
with t2:
    questions, max_marks = load_round(2)

    round_marks = st.number_input(
        "🏆 Max Marks for EACH Question in Round 2",
        1, 100, max_marks
    )

    count = st.number_input(
        "Number of Questions",
        1, 20,
        len(questions) if questions else 5
    )

    updated = []
    for i in range(count):
        q = questions[i] if i < len(questions) else {}
        st.markdown("<div class='round-card'>", unsafe_allow_html=True)
        st.subheader(f"Question {i+1}")

        img = st.text_input("Image URL", q.get("image_url", ""), key=f"r2_img{i}")
        forb = st.text_input(
            "Forbidden Words (comma separated)",
            q.get("forbidden_words", ""),
            key=f"r2_forb{i}"
        )
        gold = st.text_input("Golden Prompt", q.get("golden_prompt", ""), key=f"r2_gold{i}")

        updated.append({
            "image_url": img,
            "forbidden_words": forb,
            "golden_prompt": gold
        })
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾 Save Round 2"):
        db.collection("rounds").document("round_2").set({
            "max_marks": round_marks,
            "questions": updated
        })
        st.success("Round 2 saved")

# ======================================================
# ROUND 3
# ======================================================
with t3:
    questions, max_marks = load_round(3)

    round_marks = st.number_input(
        "🏆 Max Marks for EACH Question in Round 3",
        1, 100, max_marks
    )

    count = st.number_input(
        "Number of Questions",
        1, 20,
        len(questions) if questions else 5
    )

    updated = []
    for i in range(count):
        q = questions[i] if i < len(questions) else {}
        st.markdown("<div class='round-card'>", unsafe_allow_html=True)
        st.subheader(f"Question {i+1}")

        out = st.text_area(
            "Target Output / Code",
            q.get("output_code", ""),
            height=120,
            key=f"r3_out{i}"
        )
        desc = st.text_area(
            "Description / Rules",
            q.get("description", ""),
            height=120,
            key=f"r3_desc{i}"
        )
        gold = st.text_input(
            "Golden Prompt",
            q.get("golden_prompt", ""),
            key=f"r3_gold{i}"
        )

        updated.append({
            "output_code": out,
            "description": desc,
            "golden_prompt": gold
        })
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾 Save Round 3"):
        db.collection("rounds").document("round_3").set({
            "max_marks": round_marks,
            "questions": updated
        })
        st.success("Round 3 saved")
