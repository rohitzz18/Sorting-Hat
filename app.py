import streamlit as st
import json
import subprocess
import random
import base64

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="The Sorting Hat✨",
    layout="centered"
)

# ---------------- BACKGROUND IMAGE ----------------
def set_bg(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg("bg3.jpeg")  # <-- make sure this exists

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cinzel', serif;
}

h1, h2, h3 {
    text-align: center;
    color: #f5d76e;
    text-shadow: 0 0 15px rgba(245,215,110,0.7);
}

.name-btn button {
    width: 100%;
    background: rgba(0,0,0,0.7) !important;
    border: 1px solid gold !important;
    border-radius: 16px !important;
    padding: 18px !important;
    font-size: 20px !important;
    color: gold !important;
    transition: all 0.3s ease;
}

.name-btn button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 30px rgba(212,175,55,0.8);
}

.detail-card {
    background: rgba(0,0,0,0.85);
    border-left: 4px solid gold;
    border-radius: 0 0 16px 16px;
    padding: 20px;
    margin-bottom: 25px;
    animation: expand 0.4s ease-in-out;
}

@keyframes expand {
    from {
        opacity: 0;
        transform: translateY(-8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.bar {
    height: 8px;
    border-radius: 10px;
    background: linear-gradient(90deg, gold, orange);
    margin-top: 10px;
}

.gryffindor { color: #ae0001; }
.ravenclaw  { color: #0e1a40; }
.hufflepuff { color: #ecb939; }
.slytherin  { color: #2a623d; }

.footer {
    text-align: center;
    margin-top: 40px;
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HOUSE QUOTES ----------------
HOUSE_QUOTES = {
    "Gryffindor": ["🔥 Courage chose you.", "Bold hearts lead the way."],
    "Ravenclaw": ["🧠 Wisdom defines you.", "Your mind is your wand."],
    "Hufflepuff": ["💛 Loyalty shines.", "Kindness is strength."],
    "Slytherin": ["🐍 Ambition detected.", "You think five steps ahead."]
}

# ---------------- HEADER ----------------
st.markdown("### Built with ❤️ using NLP & Streamlit")
st.title("ONE 🎩 … FOUR DESTINIES ⚡")

uploaded = st.file_uploader("Upload WhatsApp Chat (.txt)", type="txt")

# ---------------- SESSION STATE ----------------
if "open_user" not in st.session_state:
    st.session_state.open_user = None

# ---------------- PIPELINE ----------------
if uploaded:
    with open("hogwarts_chat.txt", "wb") as f:
        f.write(uploaded.read())

    with st.spinner("🎩 The Hat is reading your soul..."):
        subprocess.run(["python3", "wa_parse_and_classify.py"], check=True)

    with open("character_user_mapping.json") as f:
        mapping = json.load(f)

    st.subheader("✨ Tap a Name — Let the Sorting Hat Decide")

    # ---------------- RESULTS ----------------
    for user, info in mapping.items():
        house = info["primary_house"]
        scores = info["scores"]
        confidence = int(max(scores.values()) * 100)

        # NAME PLACARD
        st.markdown("<div class='name-btn'>", unsafe_allow_html=True)
        if st.button(f"🪄 {user}", key=user):
            if st.session_state.open_user == user:
                st.session_state.open_user = None
            else:
                st.session_state.open_user = user
        st.markdown("</div>", unsafe_allow_html=True)

        # EXPANDED CARD
        if st.session_state.open_user == user:
            sorted_vals = sorted(scores.values(), reverse=True)
            hesitation = sorted_vals[0] - sorted_vals[1] < 0.05

            quote = (
                "⚖️ Even the Hat hesitated..."
                if hesitation
                else random.choice(HOUSE_QUOTES[house])
            )

            st.markdown(f"""
            <div class="detail-card">
                <h2 class="{house.lower()}">{house}</h2>
                <p>{quote}</p>
                <small>Second choice: <b>{info['secondary_house']}</b></small>
                <div class="bar" style="width:{confidence}%"></div>
                <small>Confidence: {confidence}%</small>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        "⬇️ Download Results (JSON)",
        json.dumps(mapping, indent=2),
        file_name="character_user_mapping.json"
    )

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    © 2026 • Created by Tech Hallows ✨
</div>
""", unsafe_allow_html=True)