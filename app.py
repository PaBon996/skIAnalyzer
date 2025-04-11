
import streamlit as st
from PIL import Image
import os

# Imposta il titolo della pagina e configurazione
st.set_page_config(page_title="SKIANALYZER", layout="wide")

# Carica il file CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titolo principale con evidenziazione su "AN"
st.markdown("""
<div class="title">
  SKI<span class="highlight">AN</span>ALYZER
</div>
<div class="subtitle">
  L'app intelligente per l'analisi posturale nello sci: carica un'immagine e scopri come migliorare la tua tecnica!
</div>
""", unsafe_allow_html=True)

# Layout immagini esempio e upload
col1, col2 = st.columns(2)

with col1:
    st.image("sciatore1.jpg", caption="Esempio di analisi", use_column_width=True)

with col2:
    st.image("sciatore2.jpg", caption="Rilevamento postura", use_column_width=True)

st.markdown("""
<div class="upload-section">
  <label for="file_uploader">Carica un'immagine per iniziare l'analisi:</label>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Immagine caricata", use_column_width=True)
    st.success("Analisi pronta! (qui si potrebbe avviare l'elaborazione IA)")
