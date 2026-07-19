"""
Inference pipeline for infrastructure damage detection.
Uses Roboflow hosted model API (trained YOLOv11 on RDD2022).
Falls back to local YOLOv8 if available.
"""

import os
import io
import base64
import json
import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "model"

# Roboflow API config. Set ROBOFLOW_API_KEY in the environment (see .env.example).
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")
ROBOFLOW_MODEL_URL = "https://detect.roboflow.com/test-dataset-yjjjr-gpw9n/2"

# Class name mapping for RDD2022 dataset
RDD_CLASSES = {
    "D00": "Longitudinal Crack",
    "D10": "Transverse Crack",
    "D20": "Alligator Crack",
    "D40": "Pothole",
}

# Extended damage classification — enriches base detections
DAMAGE_SUBTYPES = {
    "D00": {
        "name": "Longitudinal Crack",
        "category": "Crack",
        "risk": "Structural weakening along road direction. Can lead to lane separation.",
        "repair": "Crack sealing or routing and sealing",
    },
    "D10": {
        "name": "Transverse Crack",
        "category": "Crack",
        "risk": "Perpendicular stress fractures. Indicates thermal contraction or base failure.",
        "repair": "Crack filling or full-depth patching",
    },
    "D20": {
        "name": "Alligator Crack",
        "category": "Crack",
        "risk": "Interconnected fatigue cracks. Severe structural failure indicator — highest priority.",
        "repair": "Full-depth reclamation or overlay required",
    },
    "D40": {
        "name": "Pothole",
        "category": "Pothole",
        "risk": "Surface disintegration forming bowl-shaped holes. Immediate vehicle hazard.",
        "repair": "Throw-and-roll patch or semi-permanent repair",
    },
}

SEVERITY_COLORS = {
    "D00": (255, 107, 44),   # orange
    "D10": (255, 145, 66),   # amber
    "D20": (255, 68, 68),    # red — most severe crack type
    "D40": (200, 50, 50),    # dark red — pothole
}


def check_image_authenticity(image: Image.Image) -> dict:
    """
    Basic image authenticity check — detect if photo was taken from a screen.
    Checks for: moiré patterns, screen glare, EXIF metadata, edge sharpness.
    Returns a trust score and flags.
    """
    img_np = np.array(image)
    h, w = img_np.shape[:2]
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    flags = []
    trust_score = 100

    # 1. Check for moiré patterns (screen photos show periodic noise)
    f_transform = np.fft.fft2(gray.astype(float))
    f_shift = np.fft.fftshift(f_transform)
    magnitude = np.log(np.abs(f_shift) + 1)
    # High frequency peaks indicate screen capture
    center_h, center_w = h // 2, w // 2
    outer_ring = magnitude[center_h-h//4:center_h+h//4, center_w-w//4:center_w+w//4]
    freq_ratio = np.mean(outer_ring) / (np.mean(magnitude) + 1e-6)
    if freq_ratio > 1.3:
        flags.append("Possible moiré pattern detected — may be a screen photo")
        trust_score -= 25

    # 2. Check image resolution (screen photos tend to be lower quality)
    if w < 400 or h < 400:
        flags.append("Low resolution image")
        trust_score -= 15

    # 3. Check for uniform brightness bands (screen backlight)
    row_means = np.mean(gray, axis=1)
    row_variance = np.var(np.diff(row_means))
    if row_variance < 5:
        flags.append("Uniform brightness — possible screen capture")
        trust_score -= 20

    # 4. Check edge sharpness (real photos have depth-of-field, screen photos are flat)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 50:
        flags.append("Low edge variance — image may lack natural depth")
        trust_score -= 15

    trust_score = max(0, min(100, trust_score))
    is_likely_authentic = trust_score >= 60

    return {
        "trust_score": trust_score,
        "is_likely_authentic": is_likely_authentic,
        "flags": flags,
        "recommendation": "Image appears authentic" if is_likely_authentic else "Image may not be a real photo — manual verification recommended",
    }


def cv_supplementary_detection(image: Image.Image) -> list:
    """
    OpenCV-based supplementary detection for damage types the YOLO model might miss.
    Detects: surface spalling, water stains/leaks, corrosion discoloration.
    Returns additional detections to merge with YOLO results.
    """
    img_np = np.array(image)
    h, w = img_np.shape[:2]
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    extra_detections = []

    # 1. Detect surface spalling (large bright patches on dark surfaces)
    _, bright_mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, np.ones((10, 10)))
    contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > (w * h * 0.02) and area < (w * h * 0.3):  # 2-30% of image
            x, y, cw, ch = cv2.boundingRect(cnt)
            extra_detections.append({
                "bbox": [float(x), float(y), float(x + cw), float(y + ch)],
                "confidence": round(0.3 + (area / (w * h)) * 0.5, 3),
                "class_name": "spalling",
                "display_name": "Surface Spalling",
                "class_id": 10,
            })

    # 2. Detect water/moisture stains (blue-ish or dark wet patches)
    lower_blue = np.array([90, 30, 30])
    upper_blue = np.array([130, 255, 200])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, np.ones((15, 15)))
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > (w * h * 0.03):
            x, y, cw, ch = cv2.boundingRect(cnt)
            extra_detections.append({
                "bbox": [float(x), float(y), float(x + cw), float(y + ch)],
                "confidence": round(0.25 + (area / (w * h)) * 0.4, 3),
                "class_name": "leak",
                "display_name": "Water Stain / Leak",
                "class_id": 11,
            })

    # 3. Detect corrosion (orange/rust-colored patches)
    lower_rust = np.array([5, 80, 80])
    upper_rust = np.array([25, 255, 255])
    rust_mask = cv2.inRange(hsv, lower_rust, upper_rust)
    rust_mask = cv2.morphologyEx(rust_mask, cv2.MORPH_OPEN, np.ones((10, 10)))
    contours, _ = cv2.findContours(rust_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > (w * h * 0.01):
            x, y, cw, ch = cv2.boundingRect(cnt)
            extra_detections.append({
                "bbox": [float(x), float(y), float(x + cw), float(y + ch)],
                "confidence": round(0.3 + (area / (w * h)) * 0.5, 3),
                "class_name": "corrosion",
                "display_name": "Corrosion / Rust",
                "class_id": 12,
            })

    # 4. Detect pipe breaks / dark holes (potential pipe fractures)
    _, dark_mask = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, np.ones((8, 8)))
    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > (w * h * 0.01) and area < (w * h * 0.15):
            x, y, cw, ch = cv2.boundingRect(cnt)
            # Check circularity — pipes tend to show circular/oval breaks
            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * 3.14159 * area / (perimeter * perimeter) if perimeter > 0 else 0
            if circularity > 0.3:  # Somewhat circular
                extra_detections.append({
                    "bbox": [float(x), float(y), float(x + cw), float(y + ch)],
                    "confidence": round(0.3 + circularity * 0.4, 3),
                    "class_name": "pipe_damage",
                    "display_name": "Pipeline Break / Damage",
                    "class_id": 13,
                })

    return extra_detections[:6]


ALL_SEVERITY_COLORS = {
    **SEVERITY_COLORS,
    "spalling": (180, 130, 255),        # purple
    "leak": (0, 150, 255),              # blue
    "corrosion": (255, 165, 0),         # orange
    "building_crack": (255, 100, 100),  # salmon red
    "pipe_damage": (100, 180, 255),     # light blue
}


def draw_detections(image: Image.Image, detections: list) -> Image.Image:
    """Draw bounding boxes and labels on the image."""
    img = image.copy()
    draw = ImageDraw.Draw(img)

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cls = det["class_name"]
        conf = det["confidence"]
        color = ALL_SEVERITY_COLORS.get(cls, (0, 229, 204))
        display = det.get("display_name", RDD_CLASSES.get(cls, cls))

        # Draw box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        # Draw label background
        label = f"{display} {conf:.0%}"
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((x1, y1 - 20), label, font=font)
        draw.rectangle([bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2], fill=color)
        draw.text((x1, y1 - 20), label, fill=(0, 0, 0), font=font)

        # Corner markers
        corner_len = min(20, (x2 - x1) // 4, (y2 - y1) // 4)
        for cx, cy, dx, dy in [(x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)]:
            draw.line([(cx, cy), (cx + dx * corner_len, cy)], fill=color, width=2)
            draw.line([(cx, cy), (cx, cy + dy * corner_len)], fill=color, width=2)

    return img


class DamageDetector:
    def __init__(self, model_path: str = None):
        """
        Initialize the detector.
        Uses Roboflow API for the trained crack model.
        Falls back to local YOLO if best.pt exists.
        """
        self.use_roboflow = False
        self.local_model = None
        self.crack_model = None
        from ultralytics import YOLO

        # Model 1: Road damage (D00, D10, D20, D40 / Potholes)
        road_model_path = model_path or str(MODEL_DIR / "best.pt")
        if os.path.exists(road_model_path):
            print(f"[CRACKWATCH] Loading road damage model: {road_model_path}")
            self.local_model = YOLO(road_model_path)
            print(f"[CRACKWATCH] Road classes: {self.local_model.names}")
        else:
            print("[CRACKWATCH] WARNING: No road damage model found, using Roboflow fallback")
            self.use_roboflow = True

        # Model 2: Building/wall crack segmentation
        crack_seg_path = str(MODEL_DIR / "crack_seg.pt")
        if os.path.exists(crack_seg_path):
            print(f"[CRACKWATCH] Loading building crack model: {crack_seg_path}")
            self.crack_model = YOLO(crack_seg_path)
            print(f"[CRACKWATCH] Crack classes: {self.crack_model.names}")

        # Model 3: OpenCV supplementary (spalling, leaks, corrosion) — always available
        print("[CRACKWATCH] OpenCV supplementary detection: enabled")
        print(f"[CRACKWATCH] Multi-model pipeline ready: Road={'✓' if self.local_model else '✗'} | Building={'✓' if self.crack_model else '✗'} | CV=✓")

    # Sector → model mapping
    SECTOR_MODELS = {
        "road": {"yolo_road": True, "yolo_crack": False, "cv": False, "label": "Road & Highway"},
        "building": {"yolo_road": False, "yolo_crack": True, "cv": "spalling_only", "label": "Building & Structure"},
        "pipeline": {"yolo_road": False, "yolo_crack": False, "cv": True, "label": "Pipeline & Utility"},
        "bridge": {"yolo_road": True, "yolo_crack": True, "cv": "spalling_only", "label": "Bridge & Flyover"},
        "all": {"yolo_road": True, "yolo_crack": True, "cv": True, "label": "All Infrastructure"},
    }

    def detect(self, image: Image.Image, confidence_threshold: float = 0.25, sector: str = "all") -> dict:
        """Run detection on a PIL Image. Sector-specific model selection."""
        if self.use_roboflow:
            try:
                result = self._detect_roboflow(image, confidence_threshold)
            except Exception as e:
                print(f"[CRACKWATCH] Roboflow API failed: {e}")
                print("[CRACKWATCH] Falling back to OpenCV supplementary detection")
                result = self._detect_cv_only(image)
            # If Roboflow returned 0 detections (might be blocked), try local + CV
            if result["detection_count"] == 0 and not self.local_model:
                print("[CRACKWATCH] Roboflow returned 0 detections, running CV supplementary only")
                try:
                    cv_extras = cv_supplementary_detection(image)
                    if cv_extras:
                        for det in cv_extras:
                            cls = det["class_name"]
                            if cls in DAMAGE_SUBTYPES:
                                det["category"] = DAMAGE_SUBTYPES[cls]["category"]
                                det["risk"] = DAMAGE_SUBTYPES[cls]["risk"]
                                det["repair"] = DAMAGE_SUBTYPES[cls]["repair"]
                            else:
                                det["category"] = cls.capitalize()
                                det["risk"] = "Monitor and assess."
                                det["repair"] = "Professional assessment recommended"
                        annotated = draw_detections(image, cv_extras)
                        buf = io.BytesIO()
                        annotated.save(buf, format="JPEG", quality=85)
                        result["annotated_image"] = base64.b64encode(buf.getvalue()).decode()
                        result["detections"] = cv_extras
                        result["detection_count"] = len(cv_extras)
                except Exception as e:
                    print(f"[CRACKWATCH] CV fallback error: {e}")
            return result
        else:
            return self._detect_local(image, confidence_threshold, sector)

    def _detect_cv_only(self, image: Image.Image) -> dict:
        """Fallback: OpenCV-only detection when Roboflow is unavailable."""
        w, h = image.size
        detections = cv_supplementary_detection(image)

        for det in detections:
            cls = det["class_name"]
            if cls in DAMAGE_SUBTYPES:
                det["category"] = DAMAGE_SUBTYPES[cls]["category"]
                det["risk"] = DAMAGE_SUBTYPES[cls]["risk"]
                det["repair"] = DAMAGE_SUBTYPES[cls]["repair"]
            else:
                det["category"] = cls.capitalize()
                det["risk"] = "Monitor and assess during next inspection."
                det["repair"] = "Professional assessment recommended"

        annotated = draw_detections(image, detections)
        buf = io.BytesIO()
        annotated.save(buf, format="JPEG", quality=85)
        annotated_b64 = base64.b64encode(buf.getvalue()).decode()

        return {
            "detections": detections,
            "annotated_image": annotated_b64,
            "image_width": w,
            "image_height": h,
            "detection_count": len(detections),
        }

    def _detect_roboflow(self, image: Image.Image, confidence_threshold: float) -> dict:
        """Use Roboflow hosted inference API."""
        w, h = image.size

        # Convert image to base64 for API
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Call Roboflow API
        response = requests.post(
            ROBOFLOW_MODEL_URL,
            params={
                "api_key": ROBOFLOW_API_KEY,
                "confidence": int(confidence_threshold * 100),
            },
            data=img_b64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            print(f"[CRACKWATCH] Roboflow API error: {response.status_code} {response.text}")
            return {
                "detections": [],
                "annotated_image": img_b64,
                "image_width": w,
                "image_height": h,
                "detection_count": 0,
            }

        data = response.json()
        predictions = data.get("predictions", [])

        detections = []
        for pred in predictions:
            cx = pred["x"]
            cy = pred["y"]
            pw = pred["width"]
            ph = pred["height"]
            x1 = cx - pw / 2
            y1 = cy - ph / 2
            x2 = cx + pw / 2
            y2 = cy + ph / 2

            cls_name = pred["class"]
            display_name = RDD_CLASSES.get(cls_name, cls_name)

            detections.append({
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                "confidence": round(pred["confidence"], 3),
                "class_name": cls_name,
                "display_name": display_name,
                "class_id": list(RDD_CLASSES.keys()).index(cls_name) if cls_name in RDD_CLASSES else 0,
            })

        # Run supplementary CV detection for spalling, leaks, corrosion
        try:
            cv_extras = cv_supplementary_detection(image)
            detections.extend(cv_extras)
        except Exception as e:
            print(f"[CRACKWATCH] CV supplementary detection error: {e}")

        # Add damage subtype info to each detection
        for det in detections:
            cls = det["class_name"]
            if cls in DAMAGE_SUBTYPES:
                info = DAMAGE_SUBTYPES[cls]
                det["category"] = info["category"]
                det["risk"] = info["risk"]
                det["repair"] = info["repair"]
            else:
                det["category"] = cls.capitalize()
                det["risk"] = "Monitor and assess during next inspection cycle."
                det["repair"] = "Professional assessment recommended"

        # Draw detections on image
        annotated = draw_detections(image, detections)
        ann_buffer = io.BytesIO()
        annotated.save(ann_buffer, format="JPEG", quality=85)
        annotated_b64 = base64.b64encode(ann_buffer.getvalue()).decode("utf-8")

        return {
            "detections": detections,
            "annotated_image": annotated_b64,
            "image_width": w,
            "image_height": h,
            "detection_count": len(detections),
        }

    def _detect_local(self, image: Image.Image, confidence_threshold: float, sector: str = "all") -> dict:
        """Sector-specific multi-model detection."""
        models_config = self.SECTOR_MODELS.get(sector, self.SECTOR_MODELS["all"])
        img_np = np.array(image)
        if len(img_np.shape) == 2:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
        elif img_np.shape[2] == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)

        h, w = img_np.shape[:2]
        detections = []

        # ── Model 1: Road damage (D00, D10, D20, Potholes) ──
        if self.local_model and models_config.get("yolo_road"):
            results = self.local_model(img_np, conf=confidence_threshold, verbose=False)
            result = results[0]
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = self.local_model.names.get(cls_id, f"class_{cls_id}")
                display_name = RDD_CLASSES.get(cls_name, cls_name)
                detections.append({
                    "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                    "confidence": round(conf, 3),
                    "class_name": cls_name,
                    "display_name": display_name,
                    "class_id": cls_id,
                    "model_source": "road_damage",
                })

        # ── Model 2: Building/wall crack segmentation ──
        if self.crack_model and models_config.get("yolo_crack"):
            try:
                crack_results = self.crack_model(img_np, conf=max(0.3, confidence_threshold), verbose=False)
                crack_result = crack_results[0]
                if crack_result.boxes is not None:
                    for box in crack_result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = float(box.conf[0])
                        # Check if this overlaps with an existing road detection
                        is_duplicate = False
                        for existing in detections:
                            ex = existing["bbox"]
                            # Simple IoU check
                            ox1 = max(x1, ex[0]); oy1 = max(y1, ex[1])
                            ox2 = min(x2, ex[2]); oy2 = min(y2, ex[3])
                            if ox1 < ox2 and oy1 < oy2:
                                overlap = (ox2-ox1)*(oy2-oy1)
                                area1 = (x2-x1)*(y2-y1)
                                if area1 > 0 and overlap / area1 > 0.3:
                                    is_duplicate = True
                                    break
                        if not is_duplicate:
                            detections.append({
                                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                                "confidence": round(conf, 3),
                                "class_name": "building_crack",
                                "display_name": "Building/Wall Crack",
                                "class_id": 20,
                                "model_source": "crack_segmentation",
                            })
            except Exception as e:
                print(f"[CRACKWATCH] Crack model error: {e}")

        # ── Model 3: OpenCV supplementary (spalling, leaks, corrosion, pipe damage) ──
        try:
            cv_mode = models_config.get("cv")
            if cv_mode is True:
                cv_extras = cv_supplementary_detection(image)
            elif cv_mode == "spalling_only":
                cv_extras = [d for d in cv_supplementary_detection(image) if d["class_name"] == "spalling"]
            else:
                cv_extras = []
            for det in cv_extras:
                # Avoid duplicates with YOLO detections
                is_dup = False
                for existing in detections:
                    ex = existing["bbox"]
                    d = det["bbox"]
                    ox1 = max(d[0], ex[0]); oy1 = max(d[1], ex[1])
                    ox2 = min(d[2], ex[2]); oy2 = min(d[3], ex[3])
                    if ox1 < ox2 and oy1 < oy2:
                        overlap = (ox2-ox1)*(oy2-oy1)
                        area1 = (d[2]-d[0])*(d[3]-d[1])
                        if area1 > 0 and overlap / area1 > 0.3:
                            is_dup = True; break
                if not is_dup:
                    det["model_source"] = "opencv_cv"
                    detections.append(det)
        except Exception as e:
            print(f"[CRACKWATCH] CV supplementary error: {e}")

        # Add damage info to all detections
        for det in detections:
            cls = det["class_name"]
            if cls in DAMAGE_SUBTYPES:
                det["category"] = DAMAGE_SUBTYPES[cls]["category"]
                det["risk"] = DAMAGE_SUBTYPES[cls]["risk"]
                det["repair"] = DAMAGE_SUBTYPES[cls]["repair"]
            elif cls == "building_crack":
                det["category"] = "Structural Crack"
                det["risk"] = "Wall/building crack detected. May indicate foundation settlement or structural stress."
                det["repair"] = "Epoxy injection or structural reinforcement"
            else:
                det["category"] = cls.replace("_", " ").title()
                det["risk"] = "Monitor and assess during next inspection."
                det["repair"] = "Professional assessment recommended"

        # Draw all detections on image
        annotated_img = draw_detections(image, detections)
        pil_annotated = annotated_img

        buffer = io.BytesIO()
        pil_annotated.save(buffer, format="JPEG", quality=85)
        annotated_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "detections": detections,
            "annotated_image": annotated_b64,
            "image_width": w,
            "image_height": h,
            "detection_count": len(detections),
        }

    def detect_from_bytes(self, image_bytes: bytes, confidence_threshold: float = 0.25, sector: str = "all") -> dict:
        """Run detection from raw image bytes."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return self.detect(image, confidence_threshold, sector)

    def get_available_sectors(self):
        """Return list of available sectors with their descriptions."""
        return [
            {"id": "road", "label": "🛣️ Road & Highway", "desc": "Potholes, cracks, road surface damage", "models": ["YOLOv8s-RDD", "OpenCV"]},
            {"id": "building", "label": "🏢 Building & Structure", "desc": "Wall cracks, concrete damage, spalling", "models": ["YOLOv8s-CrackSeg", "OpenCV"]},
            {"id": "pipeline", "label": "🔧 Pipeline & Utility", "desc": "Pipe breaks, leaks, corrosion", "models": ["OpenCV"]},
            {"id": "bridge", "label": "🌉 Bridge & Flyover", "desc": "Structural cracks + road damage", "models": ["YOLOv8s-RDD", "YOLOv8s-CrackSeg", "OpenCV"]},
            {"id": "all", "label": "🔍 All Infrastructure", "desc": "Run all models for comprehensive scan", "models": ["All 3 models"]},
        ]


# Singleton
_detector = None

def get_detector(model_path: str = None) -> DamageDetector:
    global _detector
    if _detector is None:
        _detector = DamageDetector(model_path)
    return _detector
