import streamlit as st
import subprocess
import os
import json
import tempfile
import pandas as pd
WA_TXT_PATH="_chat.txt"
WA_TRANSLATED_CSV="whatsapp_translated.csv"
MAPPING_JSON="character_user_mapping.json"

st.set_page_config(
    page_title="XYZ",
    layout="centered"
)

st.markdown("""<style>...</style>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload WhatsApp chat (.txt)", type=["txt"])
if uploaded_file:
    with open(WA_TXT_PATH, "wb") as f:
        f.write(uploaded_file.read())

subprocess.run(["python3", "wa_parse.py"], check=True)

subprocess.run(["python3", "embed_wa.py"], check=True)

subprocess.run(["python3", "similarity.py"], check=True)

with open(MAPPING_JSON) as f:
    mapping = json.load(f)

result_df = pd.DataFrame(
    mapping.items(),
    columns=["Character", "Assigned User"]
)

st.download_button("Download JSON", ...)
st.download_button("Download CSV", ...)

