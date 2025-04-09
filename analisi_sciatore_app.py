
import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

st.set_page_config(page_title="Analisi Sciatore", layout="centered")
st.title("⛷️ Analisi Postura Sciatore")

st.markdown("""
Carica un'immagine di uno sciatore per analizzare la postura.  
L'app userà **MediaPipe** per rilevare i punti chiave del corpo.
""")

uploaded_file = st.file_uploader("📁 Carica un'immagine", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    st.image(image, caption="📸 Immagine Originale", use_column_width=True)

    # Inizializza MediaPipe
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))

        if results.pose_landmarks:
            annotated_image = img_np.copy()
            mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS)

            st.image(annotated_image, caption="✅ Punti Chiave Rilevati", use_column_width=True)
            st.success("Analisi completata! 🎯")
        else:
            st.warning("⚠️ Nessun corpo rilevato nell'immagine.")
