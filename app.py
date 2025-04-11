import streamlit as st
from analysis_utils import analyze_image
from PIL import Image
import tempfile
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Analisi Sciatore", layout="centered")

custom_css = """
<style>
body {
    background-color: #0f172a;
    color: #e2e8f0;
}
h1 {
    font-size: 3em;
    font-weight: bold;
    margin-top: 0.5em;
}
h2 {
    color: #7dd3fc;
}
.stButton>button {
    background-color: #14b8a6;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.6em 2em;
    border: none;
}
.stButton>button:hover {
    background-color: #0d9488;
}
.st-emotion-cache-1avcm0n {
    background-color: #0f172a;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

menu = st.sidebar.selectbox("📂 Menu", ["🧪 Analisi", "📁 Archivio"])
ARCHIVE_FILE = "archivio.csv"

if menu == "🧪 Analisi":
    st.markdown("## Sports Image Analysis")
    st.markdown("Analyze posture and technique of skiers with our AI-powered tool.")
    st.markdown("")

    uploaded_file = st.file_uploader("📤 Carica un'immagine", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        result = analyze_image(tmp_path)

        if "error" in result:
            st.error(result["error"])
        else:
            st.image(result["img_out"], caption="Analisi immagine", use_container_width=True)

            st.subheader("📊 Risultati")
            st.metric("Parallelismo", f"{result['parallelism_score']:.1f}/100")
            st.metric("Perpendicolarità busto", f"{result['perpendicularity_score']:.1f}/100")
            st.metric("Curva", result["turn_direction"])
            st.metric("Gamba sinistra", f"{result['left_knee_score']:.1f}/100")
            st.metric("Gamba destra", f"{result['right_knee_score']:.1f}/100")

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

elif menu == "📁 Archivio":
    st.title("📁 Archivio Analisi")
    if os.path.exists(ARCHIVE_FILE):
        df = pd.read_csv(ARCHIVE_FILE)
        st.dataframe(df)
        if st.button("🗑 Svuota archivio"):
            os.remove(ARCHIVE_FILE)
            st.success("Archivio eliminato.")
    else:
        st.info("Nessuna analisi salvata al momento.")
