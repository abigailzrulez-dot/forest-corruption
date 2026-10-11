import cv2
import numpy as np
import torch
import open_clip
from PIL import Image
from ultralytics import YOLO
from flask import Flask, Response, jsonify, send_from_directory
import threading

# ---------- Models ----------
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
    "vegetable scraps", "a plastic bag", "a chip bag",
    "a battery", "a phone charger cable",
    "a paper cup", "a styrofoam cup", "a used tissue", "a candy wrapper",
    "a shoe", "a toy",
]

ROUTE_MAP = {
    "a plastic bottle": "RECYCLE", "an aluminum can": "RECYCLE",
    "a glass bottle": "RECYCLE", "a cardboard box": "RECYCLE",
    "a sheet of paper": "RECYCLE", "a newspaper": "RECYCLE", "a tin can": "RECYCLE",
    "a banana peel": "COMPOST", "an apple core": "COMPOST",
    "a coffee filter": "COMPOST", "a tea bag": "COMPOST", "vegetable scraps": "COMPOST",
    "a plastic bag": "ECO-BRICK", "a chip bag": "ECO-BRICK",
    "a battery": "E-WASTE CENTER", "a phone charger cable": "E-WASTE CENTER",
    "a paper cup": "TRASH", "a styrofoam cup": "TRASH",
    "a used tissue": "TRASH", "a candy wrapper": "TRASH",
    "a shoe": "WASTE CENTER", "a toy": "WASTE CENTER",
}

CONFIDENCE = 0.30
YOLO_CONF = 0.35

text_tokens = tokenizer(CATEGORIES).to(device)
with torch.no_grad():
    text_features = clip_model.encode_text(text_tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

# ---------- Camera shared state ----------
CAM_INDEX = 1
cam_lock = threading.Lock()
last_frame = None
last_result = None
scanning = False
frame_ready = threading.Event()

def classify(crop_bgr):
    img = preprocess(Image.fromarray(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB))
                     ).unsqueeze(0).to(device)
    with torch.no_grad():
        feats = clip_model.encode_image(img)
        feats /= feats.norm(dim=-1, keepdim=True)
        probs = (100.0 * feats @ text_features.T).softmax(dim=-1)[0].cpu().numpy()
    i = int(probs.argmax())
    return CATEGORIES[i], ROUTE_MAP[CATEGORIES[i]], float(probs[i])

def annotate(frame):
    global last_frame, last_result
    result = None
    for r in yolo(frame, verbose=False):
        for box in r.boxes:
            if float(box.conf[0]) < YOLO_CONF:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = frame[max(y1, 0):y2, max(x1, 0):x2]
            if crop.shape[0] == 0 or crop.shape[1] == 0:
                continue
            label, route, conf = classify(crop)
            if conf > CONFIDENCE and route:
                color = (0, 255, 0) if route in ("RECYCLE", "COMPOST") else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} -> {route}",
                            (x1, max(y1 - 8, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                if result is None or conf > result["confidence"]:
                    result = {"item": label, "bin": route, "confidence": round(conf, 3)}
    last_result = result
    ok, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if ok:
        with cam_lock:
            last_frame = jpeg.tobytes()
        frame_ready.set()

def camera_loop():
    global scanning
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print(f"!! Could not open camera {CAM_INDEX}. Try CAM_INDEX = 0.")
        return
    print("Camera ready.")
    idle_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if scanning:
            annotate(frame)
            idle_count = 0
        else:
            idle_count += 1
            if idle_count > 900:
                cap.release()
                while not scanning:
                    frame_ready.wait(timeout=1)
                cap = cv2.VideoCapture(CAM_INDEX)
                idle_count = 0
        frame_ready.wait(timeout=0.05)
        frame_ready.clear()
    cap.release()

threading.Thread(target=camera_loop, daemon=True).start()

# ---------- Flask app ----------
app = Flask(__name__, static_folder='.')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

def mjpeg():
    global scanning
    scanning = True
    try:
        while True:
            frame_ready.wait(timeout=2)
            with cam_lock:
                chunk = last_frame
            if chunk:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                       + chunk + b'\r\n')
    finally:
        scanning = False

@app.route('/scan/stream')
def stream():
    return Response(mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/scan/result')
def result():
    return jsonify(last_result or {"item": None})

if __name__ == '__main__':
    print("Open http://localhost:8000")
    app.run(host='127.0.0.1', port=8000, threaded=True)