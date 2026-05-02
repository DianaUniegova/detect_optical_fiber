import os
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

CONF_THRESHOLD = 0.3

def process_image(path):
    # --- читаємо без втрати ---
    img = cv2.imread(path, cv2.IMREAD_COLOR)

    if img is None:
        return {
            "type": "image",
            "result_image": None,
            "detected": False
        }

    original = img.copy()

    # --- YOLO ---
    results = model(path)[0]
    boxes = results.boxes
    names = results.names

    yolo_detected = False

    if boxes is not None:
        for box in boxes:
            conf = float(box.conf[0])
            if conf < CONF_THRESHOLD:
                continue

            yolo_detected = True

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = names[int(box.cls[0])]

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                img,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

    # --- IMAGE ENHANCEMENT ---
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blur, 30, 120)

    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # --- LINES ---
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=50,
        minLineLength=40,
        maxLineGap=40
    )

    line_detected = False

    if lines is not None:
        for line in lines[:100]:
            x1, y1, x2, y2 = line[0]

            length = np.hypot(x2 - x1, y2 - y1)

            if length < 30:
                continue

            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2, cv2.LINE_AA)
            line_detected = True

    # --- RESULT ---
    detected = line_detected or yolo_detected

    status_text = "Fiber lines detected" if detected else "No lines detected"

    cv2.putText(
        img,
        status_text,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0) if detected else (0, 0, 255),
        2,
        cv2.LINE_AA
    )

    # --- SAVE HIGH QUALITY (ВАЖЛИВО) ---
    filename = os.path.splitext(os.path.basename(path))[0] + "_result.png"
    result_path = os.path.join("results", filename)

    # PNG = без втрати якості
    cv2.imwrite(result_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    # debug edges теж без втрат
    debug_edges_path = os.path.join("results", f"edges_{filename}")
    cv2.imwrite(debug_edges_path, edges)

    return {
        "type": "image",
        "result_image": filename,
        "detected": detected
    }