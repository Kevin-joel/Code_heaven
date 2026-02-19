import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import base64
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=2,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


def decode_image(image_data):
    try:
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except:
        return None


def is_mouth_open(landmarks, h):
    upper = landmarks[13]
    lower = landmarks[14]
    distance = abs((lower.y - upper.y) * h)
    return distance > 18


def is_head_turned(landmarks):
    nose = landmarks[1]
    left = landmarks[234]
    right = landmarks[454]

    left_dist = abs(nose.x - left.x)
    right_dist = abs(nose.x - right.x)

    ratio = left_dist / (right_dist + 1e-6)

    return ratio > 1.7 or ratio < 0.55


def detect_cheating(image_data):
    frame = decode_image(image_data)
    if frame is None:
        return "Camera frame error"

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return "No face detected"

    if len(results.multi_face_landmarks) > 1:
        return "Multiple persons detected"

    landmarks = results.multi_face_landmarks[0].landmark
    h, w, _ = frame.shape

    if is_head_turned(landmarks):
        return "Looking away from screen"

    if is_mouth_open(landmarks, h):
        return "Speaking detected"

    return "OK"
