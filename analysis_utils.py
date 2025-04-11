import numpy as np
import math
import mediapipe as mp
import cv2
from PIL import Image

mp_pose = mp.solutions.pose

def get_landmark_coords(landmarks, name, w, h):
    try:
        lm = landmarks[mp_pose.PoseLandmark[name].value]
        if lm.visibility > 0.6:
            return [int(lm.x * w), int(lm.y * h)]
    except:
        return None

def angle_with_vertical(p1, p2):
    if p1 is None or p2 is None: return None
    vec = [p2[0] - p1[0], p2[1] - p1[1]]
    return vector_angle(vec, [0, 1])

def vector_angle(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0: return None
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
    return np.degrees(angle)

def gaussian_score(angle, target, sigma=15, max_score=100):
    if angle is None: return 0
    return max_score * math.exp(-((angle - target) ** 2) / (2 * sigma ** 2))

def analyze_image(image_path):
    img_bgr = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w, _ = img_rgb.shape

    with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose:
        results = pose.process(img_rgb)
        if not results.pose_landmarks:
            return {"img_out": img_rgb, "error": "No landmarks found"}

        landmarks = results.pose_landmarks.landmark
        lm = lambda name: get_landmark_coords(landmarks, name, w, h)

        lk, la = lm('LEFT_KNEE'), lm('LEFT_ANKLE')
        rk, ra = lm('RIGHT_KNEE'), lm('RIGHT_ANKLE')
        angle_l = angle_with_vertical(lk, la)
        angle_r = angle_with_vertical(rk, ra)
        diff_parallel = abs(angle_l - angle_r) if angle_l and angle_r else None
        parallelism_score = gaussian_score(diff_parallel, 0)

        ls, rs = lm('LEFT_SHOULDER'), lm('RIGHT_SHOULDER')
        lh, rh = lm('LEFT_HIP'), lm('RIGHT_HIP')
        la, ra = lm('LEFT_ANKLE'), lm('RIGHT_ANKLE')

        mid_sh = [(ls[0] + rs[0]) // 2, (ls[1] + rs[1]) // 2] if ls and rs else None
        mid_hip = [(lh[0] + rh[0]) // 2, (lh[1] + rh[1]) // 2] if lh and rh else None
        vec_body = [mid_sh[0] - mid_hip[0], mid_sh[1] - mid_hip[1]] if mid_sh and mid_hip else None
        vec_slope = [ra[0] - la[0], ra[1] - la[1]] if ra and la else None

        angle_body_slope = vector_angle(vec_body, vec_slope) if vec_body and vec_slope else None
        perpendicularity_score = gaussian_score(abs(angle_body_slope - 90), 0, sigma=20) if angle_body_slope is not None else 0

        lean_angle = math.degrees(math.atan2(vec_body[0], vec_body[1])) if vec_body else 0
        turn_direction = "Sinistra" if lean_angle > 5 else ("Destra" if lean_angle < -5 else "Dritto")

        left_knee_score = gaussian_score(angle_with_vertical(lk, la), 10)
        right_knee_score = gaussian_score(angle_with_vertical(rk, ra), 10)

        mp.solutions.drawing_utils.draw_landmarks(
            image=img_bgr,
            landmark_list=results.pose_landmarks,
            connections=mp_pose.POSE_CONNECTIONS)

        return {
            "img_out": cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB),
            "parallelism_score": parallelism_score,
            "perpendicularity_score": perpendicularity_score,
            "turn_direction": turn_direction,
            "left_knee_score": left_knee_score,
            "right_knee_score": right_knee_score
        }
