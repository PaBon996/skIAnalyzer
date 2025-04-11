import streamlit as st
from analysis_utils import analyze_image
from PIL import Image
import tempfile

st.set_page_config(page_title="Analisi Sciatore", layout="centered")

st.title("🏂 Analisi Postura Sciatore")
st.write("Carica una foto per analizzare la postura dello sciatore.")

uploaded = st.file_uploader("Carica immagine", type=["jpg", "jpeg", "png"])
if uploaded:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded.read())
        tmp_path = tmp_file.name
    result = analyze_image(tmp_path)

    if "error" in result:
        st.error(result["error"])
    else:
        st.image(result["img_out"], caption="📸 Immagine analizzata", use_column_width=True)
        st.subheader("📊 Risultati")
        st.metric("Parallelismo", f"{result['parallelism_score']:.1f}/100")
        st.metric("Perpendicolarità busto", f"{result['perpendicularity_score']:.1f}/100")
        st.metric("Curva", result["turn_direction"])
        st.metric("Gamba sinistra", f"{result['left_knee_score']:.1f}/100")
        st.metric("Gamba destra", f"{result['right_knee_score']:.1f}/100")
