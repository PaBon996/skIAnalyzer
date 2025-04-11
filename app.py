import streamlit as st
from analysis_utils import analyze_image
from PIL import Image
import tempfile
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Analisi Sciatore", layout="centered")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inizializza lo stato della pagina
if "page" not in st.session_state:
    st.session_state.page = "home"
if "result" not in st.session_state:
    st.session_state.result = None

ARCHIVE_FILE = "archivio.csv"

def go_home():
    st.session_state.page = "home"
    st.session_state.result = None

def analyze_and_switch(img_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(img_file.read())
        tmp_path = tmp_file.name
    result = analyze_image(tmp_path)
    st.session_state.result = result
    st.session_state.page = "result"

if st.session_state.page == "home":
    st.markdown("## 🏂 Analisi Postura Sciatore")
    st.markdown("Carica una foto per analizzare la postura con intelligenza artificiale.")

    uploaded = st.file_uploader("Carica immagine", type=["jpg", "jpeg", "png"])
    if uploaded:
        if st.button("🔍 Avvia analisi"):
            analyze_and_switch(uploaded)

elif st.session_state.page == "result":
    result = st.session_state.result
    if result and "error" not in result:
        st.image(result["img_out"], caption="📸 Immagine analizzata", use_container_width=True)
        st.subheader("📊 Risultati")
        st.metric("Parallelismo", f"{result['parallelism_score']:.1f}/100")
        st.metric("Perpendicolarità busto", f"{result['perpendicularity_score']:.1f}/100")
        st.metric("Curva", result["turn_direction"])
        st.metric("Gamba sinistra", f"{result['left_knee_score']:.1f}/100")
        st.metric("Gamba destra", f"{result['right_knee_score']:.1f}/100")

        # Salva l'analisi
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = {
            "Data": timestamp,
            "Parallelismo": round(result["parallelism_score"], 1),
            "Perpendicolarità": round(result["perpendicularity_score"], 1),
            "Curva": result["turn_direction"],
            "Gamba Sinistra": round(result["left_knee_score"], 1),
            "Gamba Destra": round(result["right_knee_score"], 1)
        }
        if os.path.exists(ARCHIVE_FILE):
            df_old = pd.read_csv(ARCHIVE_FILE)
            df_new = pd.concat([df_old, pd.DataFrame([row])], ignore_index=True)
        else:
            df_new = pd.DataFrame([row])
        df_new.to_csv(ARCHIVE_FILE, index=False)
        st.success("✅ Analisi salvata nell'archivio.")
    else:
        st.error(result.get("error", "Errore sconosciuto"))

    if st.button("↩️ Torna alla Home"):
        go_home()
