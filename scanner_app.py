import os
import re
import threading

import cv2
import torch
import open_clip
from PIL import Image
from ultralytics import YOLO
from flask import Flask, Response, jsonify, render_template, send_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Loading YOLO...")
yolo = YOLO('yolov8n.pt')

print("Loading CLIP...")
device = "cpu"
clip_model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32', pretrained='laion2b_s34b_b79k', device=device
)
tokenizer = open_clip.get_tokenizer('ViT-B-32')
clip_model.eval()

CATEGORIES = [
    "a plastic bottle", "an aluminum can", "a glass bottle",
    "a cardboard box", "a sheet of paper", "a newspaper", "a tin can",
    "a banana peel", "an apple core", "a coffee filter", "a tea bag",
    "vegetable scraps",
    "a plastic bag", "a chip bag",
    "a battery", "a phone charger cable",
    "a paper cup", "a styrofoam cup", "a used tissue", "a candy wrapper",
    "a shoe", "a toy",
    "a human face", "a person", "a hand", "a desk", "a laptop keyboard",
    "a chair", "a wall",
]

ROUTE_MAP = {
    "a plastic bottle": "RECYCLE",
    "an aluminum can": "RECYCLE",
    "a glass bottle": "RECYCLE",
    "a cardboard box": "RECYCLE",
    "a sheet of paper": "RECYCLE",
    "a newspaper": "RECYCLE",
    "a tin can": "RECYCLE",
    "a banana peel": "COMPOST",
    "an apple core": "COMPOST",
    "a coffee filter": "COMPOST",
    "a tea bag": "COMPOST",
    "vegetable scraps": "COMPOST",
    "a plastic bag": "ECO-BRICK",
    "a chip bag": "ECO-BRICK",
    "a battery": "E-WASTE CENTER",
    "a phone charger cable": "E-WASTE CENTER",
    "a paper cup": "TRASH",
    "a styrofoam cup": "TRASH",
    "a used tissue": "TRASH",
    "a candy wrapper": "TRASH",
    "a shoe": "WASTE CENTER",
    "a toy": "WASTE CENTER",
    "a human face": "", "a person": "", "a hand": "",
    "a desk": "", "a laptop keyboard": "",
    "a chair": "", "a wall": "",
}

CONFIDENCE = 0.30

text_tokens = tokenizer(CATEGORIES).to(device)
with torch.no_grad():
    text_features = clip_model.encode_text(text_tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

app = Flask(__name__)
cam_lock = threading.Lock()      # only one video stream may own the camera
latest = {"items": []}           # what the scanner currently sees


def annotate(frame):
    results = yolo(frame, verbose=False)
    detections = []
    for r in results:
        for box in r.boxes:
            if float(box.conf[0]) < 0.35:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = frame[max(y1, 0):y2, max(x1, 0):x2]
            if crop.size == 0:
                continue

            img = preprocess(Image.fromarray(
                cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            )).unsqueeze(0).to(device)

            with torch.no_grad():
                feats = clip_model.encode_image(img)
                feats /= feats.norm(dim=-1, keepdim=True)
                probs = (100.0 * feats @ text_features.T).softmax(dim=-1)[0].cpu().numpy()

            i = int(probs.argmax())
            label, route = CATEGORIES[i], ROUTE_MAP[CATEGORIES[i]]
            if probs[i] > CONFIDENCE and route:
                color = (0, 255, 0) if route in ("RECYCLE", "COMPOST") else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} -> {route}",
                            (x1, max(y1 - 8, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                detections.append({
                    "label": re.sub(r"^(a|an) ", "", label),
                    "route": route,
                })
    return frame, detections


def gen_frames():
    if not cam_lock.acquire(blocking=False):
        return                               # camera already in use
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW = Windows camera backend
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.resize(frame, (640, 480))
            frame, items = annotate(frame)
            latest["items"] = items
            ok, jpg = cv2.imencode('.jpg', frame)
            if not ok:
                break
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                   + jpg.tobytes() + b'\r\n')
    finally:                                 # runs when the page is closed
        cap.release()
        latest["items"] = []
        cam_lock.release()


@app.route("/")
def home():
    # index.html sits in the main folder, not in templates\
    return send_file(os.path.join(BASE_DIR, "index.html"))


@app.route("/scanner")
def scanner_page():
    return render_template("scanner.html")   # templates\scanner.html


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/detections")
def detections():
    return jsonify(latest)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)