import streamlit as st
from PIL import Image
import os
import tempfile
import mediapipe as mp
import cv2
import numpy as np
import math

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

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

if uploaded_file:
    image = Image.open(uploaded_file)
    image_np = np.array(image.convert('RGB'))

    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

        if results.pose_landmarks:
            annotated_image = image_np.copy()
            mp_drawing.draw_landmarks(
                annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            st.image(annotated_image, caption="Punti del corpo rilevati", use_column_width=True)

            # Coordinate utili
            landmarks = results.pose_landmarks.landmark
            get_point = lambda idx: [landmarks[idx].x * image_np.shape[1], landmarks[idx].y * image_np.shape[0]]

            # Calcolo angoli
            angolo_busto = calculate_angle(get_point(mp_pose.PoseLandmark.LEFT_HIP.value),
                                           get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value),
                                           [get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value)[0], get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value)[1] - 100])

            angolo_gambe = calculate_angle(get_point(mp_pose.PoseLandmark.LEFT_HIP.value),
                                           get_point(mp_pose.PoseLandmark.LEFT_KNEE.value),
                                           get_point(mp_pose.PoseLandmark.LEFT_ANKLE.value))

            angolo_bra = calculate_angle(get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value),
                                         get_point(mp_pose.PoseLandmark.LEFT_ELBOW.value),
                                         get_point(mp_pose.PoseLandmark.LEFT_WRIST.value))

            # Mostra risultati
            st.markdown("### Risultato Analisi Posturale")
            st.write(f"**Inclinazione busto** (vs verticale): {round(angolo_busto, 1)}°")
            st.write(f"**Inclinazione gamba sinistra**: {round(angolo_gambe, 1)}°")
            st.write(f"**Angolo braccio sinistro**: {round(angolo_bra, 1)}°")

            # Semplice punteggio e commenti
            score = 100
            feedback = []

            if abs(angolo_busto - 90) > 20:
                score -= 20
                feedback.append("Il busto non è perpendicolare al terreno. Cerca di mantenere la schiena più dritta.")
            else:
                feedback.append("Ottima posizione del busto!")

            if abs(angolo_gambe - 150) > 20:
                score -= 20
                feedback.append("Le gambe non sono abbastanza parallele e piegate. Prova ad abbassare maggiormente il centro di massa.")
            else:
                feedback.append("Buona inclinazione delle gambe!")

            if abs(angolo_bra - 180) > 20:
                score -= 20
                feedback.append("Le braccia non sono parallele al terreno. Prova a tenerle più aperte.")
            else:
                feedback.append("Ottima posizione delle braccia!")

            st.subheader(f"Punteggio posturale: {score}/100")
            st.markdown("### Commenti personalizzati:")
            for msg in feedback:
                st.write("- " + msg)
        else:
            st.warning("Non sono stati rilevati punti del corpo nell'immagine.")
