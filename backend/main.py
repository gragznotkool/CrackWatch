"""
CRACKWATCH Backend — FastAPI server for infrastructure damage detection.
"""

import os
import uuid
import time
import io
import json
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv

from inference import get_detector, check_image_authenticity
from severity import compute_severity, compute_overall_stats
from cost_engine import estimate_cost, rank_priorities, generate_repair_plan, explain_severity
from auth import login, register_citizen, verify_token
from fraud_detection import run_full_fraud_check
from analytics_engine import generate_wall_of_shame, generate_heatmap_data, generate_priority_queue, generate_city_health_scores
from predictive_engine import predict_all_detections, generate_area_forecast
from gamification import (
    award_points, get_leaderboard, get_user_profile_full, get_daily_challenges,
    community_vote, ai_challenge_round, check_ai_challenge, get_authority_fix_streaks,
)

# Load .env (Twilio credentials etc.)
load_dotenv(Path(__file__).parent / ".env")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

app = FastAPI(
    title="CRACKWATCH API",
    description="AI-powered infrastructure damage detection system",
    version="1.0.0",
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for detections (hackathon — no DB needed)
detection_store: list[dict] = []
alert_store: list[dict] = []

# ── Shared file store (lets 2 backend processes share state) ──
SHARED_STORE_FILE = Path(__file__).parent / "shared_store.json"

def _persist_shared_store():
    """Write in-memory stores to disk so other backend process can read."""
    try:
        SHARED_STORE_FILE.write_text(json.dumps({
            "citizen_reports": citizen_reports,
            "detection_store": detection_store,
        }, default=str))
    except Exception as e:
        print(f"[STORE] Persist error: {e}")

def _reload_shared_store():
    """Merge shared file into in-memory stores (dedupe by id, file wins)."""
    try:
        if not SHARED_STORE_FILE.exists():
            return
        data = json.loads(SHARED_STORE_FILE.read_text())
        shared_cr = data.get("citizen_reports", [])
        shared_ds = data.get("detection_store", [])
        if shared_cr:
            merged = {r["id"]: r for r in citizen_reports}
            for r in shared_cr:
                merged[r["id"]] = r
            citizen_reports.clear()
            citizen_reports.extend(merged.values())
        if shared_ds:
            merged = {r["id"]: r for r in detection_store}
            for r in shared_ds:
                merged[r["id"]] = r
            detection_store.clear()
            detection_store.extend(merged.values())
    except Exception as e:
        print(f"[STORE] Reload error: {e}")

# System settings — controllable by government admin
system_settings = {
    "fraud_detection_enabled": True,
}

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup():
    """Pre-load model on startup so first request is fast. Load demo data."""
    print("[CRACKWATCH] Starting up...")
    get_detector()
    try:
        await seed_demo_gamification()
        # Load pre-seeded image-based reports from shared_store.json if present.
        # If the file is missing, fall back to legacy hardcoded 8-report seed.
        _reload_shared_store()
        if not citizen_reports:
            await seed_demo_reports()
            print("[CRACKWATCH] Fallback seed (8 hardcoded reports) loaded.")
        else:
            print(f"[CRACKWATCH] Loaded {len(citizen_reports)} reports from shared_store.json")
    except Exception as e:
        print(f"[CRACKWATCH] Auto-seed error: {e}")
    print("[CRACKWATCH] Ready.")


@app.get("/")
async def root():
    return {"status": "online", "service": "CRACKWATCH API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/auth/login")
async def auth_login(username: str = Form(...), password: str = Form(...)):
    """Government login with username + password."""
    result = login(username, password)
    if not result:
        raise HTTPException(401, "Invalid username or password")
    return result


@app.post("/auth/register")
async def auth_register(name: str = Form(...)):
    """Citizen registration — just a name, no password."""
    if not name.strip():
        raise HTTPException(400, "Name is required")
    return register_citizen(name.strip())


@app.get("/auth/me")
async def auth_me(request: Request):
    """Verify token and return user info."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    return {"username": payload["sub"], "role": payload["role"], "name": payload["name"]}


@app.get("/sectors")
async def get_sectors():
    """List available infrastructure sectors for targeted detection."""
    detector = get_detector()
    return {"sectors": detector.get_available_sectors()}


@app.get("/admin/settings")
async def get_settings():
    """ADMIN: Get system settings."""
    return system_settings


@app.patch("/admin/settings")
async def update_settings(fraud_detection_enabled: Optional[bool] = Form(default=None)):
    """ADMIN: Update system settings."""
    if fraud_detection_enabled is not None:
        system_settings["fraud_detection_enabled"] = fraud_detection_enabled
    return system_settings


@app.post("/detect")
async def detect_damage(
    file: UploadFile = File(...),
    confidence: float = Form(default=0.25),
    sector: str = Form(default="all"),
    latitude: Optional[float] = Form(default=None),
    longitude: Optional[float] = Form(default=None),
    location_name: Optional[str] = Form(default=None),
):
    """
    Upload an image and detect infrastructure damage.

    Returns detections with bounding boxes, severity scores,
    and an annotated image.
    """
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (JPEG, PNG, etc.)")

    # Read image bytes
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(400, "Empty file")

    # Run detection
    start_time = time.time()
    detector = get_detector()
    result = detector.detect_from_bytes(image_bytes, confidence, sector)
    inference_time = round((time.time() - start_time) * 1000, 1)  # ms

    # Compute severity scores
    scored_detections = compute_severity(
        result["detections"],
        result["image_width"],
        result["image_height"],
    )

    # Compute overall stats
    stats = compute_overall_stats(scored_detections)

    # Rank priorities + cost estimation
    ranked_detections = rank_priorities(scored_detections)

    # Add explainability to each detection
    for det in ranked_detections:
        det["explanation"] = explain_severity(det)

    # Build detection record
    detection_id = str(uuid.uuid4())[:8]
    record = {
        "id": detection_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "filename": file.filename,
        "image_width": result["image_width"],
        "image_height": result["image_height"],
        "detections": ranked_detections,
        "annotated_image": result["annotated_image"],
        "stats": stats,
        "inference_time_ms": inference_time,
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "name": location_name,
        },
    }

    # Store in memory
    detection_store.append(record)

    # Generate alerts for critical detections
    for det in ranked_detections:
        if det["severity_label"] == "critical":
            alert = {
                "id": len(alert_store) + 1,
                "time": record["timestamp"],
                "type": "CRITICAL_DAMAGE",
                "severity": "critical",
                "message": f'{det["display_name"]} detected — severity {det["severity"]}% — {location_name or "Unknown location"}',
                "detection_id": detection_id,
                "class_name": det["class_name"],
            }
            alert_store.append(alert)
        elif det["severity_label"] == "warning":
            alert = {
                "id": len(alert_store) + 1,
                "time": record["timestamp"],
                "type": "DAMAGE_WARNING",
                "severity": "warning",
                "message": f'{det["display_name"]} detected — severity {det["severity"]}% — monitoring recommended',
                "detection_id": detection_id,
                "class_name": det["class_name"],
            }
            alert_store.append(alert)

    # Run image authenticity check
    from PIL import Image as PILImage
    import io as _io
    try:
        pil_img = PILImage.open(_io.BytesIO(image_bytes)).convert("RGB")
        authenticity = check_image_authenticity(pil_img)
    except:
        authenticity = {"trust_score": 100, "is_likely_authentic": True, "flags": [], "recommendation": "Check skipped"}

    return JSONResponse(content={
        "id": detection_id,
        "detections": ranked_detections,
        "annotated_image": result["annotated_image"],
        "stats": stats,
        "inference_time_ms": inference_time,
        "location": record["location"],
        "authenticity": authenticity,
        "predictions": predict_all_detections(ranked_detections),
    })


@app.get("/detections")
async def list_detections():
    """Get all past detection records (without annotated images to save bandwidth)."""
    records = []
    for r in detection_store:
        records.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "filename": r["filename"],
            "stats": r["stats"],
            "inference_time_ms": r["inference_time_ms"],
            "location": r["location"],
            "detection_count": len(r["detections"]),
        })
    return {"detections": list(reversed(records)), "total": len(records)}


@app.get("/detections/{detection_id}")
async def get_detection(detection_id: str):
    """Get a specific detection by ID (includes annotated image)."""
    for r in detection_store:
        if r["id"] == detection_id:
            return r
    raise HTTPException(404, "Detection not found")


@app.get("/stats")
async def get_aggregate_stats():
    """Get aggregate statistics across all detections."""
    all_detections = []
    for r in detection_store:
        all_detections.extend(r["detections"])

    stats = compute_overall_stats(all_detections)
    stats["total_scans"] = len(detection_store)
    stats["total_images"] = len(detection_store)

    # Location stats
    locations_with_damage = sum(
        1 for r in detection_store if r["stats"]["total_defects"] > 0
    )
    stats["locations_with_damage"] = locations_with_damage

    return stats


@app.get("/alerts")
async def get_alerts():
    """Get all alerts sorted by most recent."""
    return {"alerts": list(reversed(alert_store)), "total": len(alert_store)}


@app.post("/detect/batch")
async def detect_batch(
    files: list[UploadFile] = File(...),
    confidence: float = Form(default=0.25),
):
    """Process multiple images at once."""
    results = []
    detector = get_detector()

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            results.append({"filename": file.filename, "error": "Not an image"})
            continue

        image_bytes = await file.read()
        start_time = time.time()
        result = detector.detect_from_bytes(image_bytes, confidence)
        inference_time = round((time.time() - start_time) * 1000, 1)

        scored = compute_severity(
            result["detections"],
            result["image_width"],
            result["image_height"],
        )
        stats = compute_overall_stats(scored)

        detection_id = str(uuid.uuid4())[:8]
        record = {
            "id": detection_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "filename": file.filename,
            "image_width": result["image_width"],
            "image_height": result["image_height"],
            "detections": scored,
            "annotated_image": result["annotated_image"],
            "stats": stats,
            "inference_time_ms": inference_time,
            "location": {"latitude": None, "longitude": None, "name": None},
        }
        detection_store.append(record)

        results.append({
            "id": detection_id,
            "filename": file.filename,
            "detection_count": len(scored),
            "stats": stats,
            "inference_time_ms": inference_time,
        })

    return {"results": results, "total_processed": len(results)}


# ============================================================
# VIDEO PROCESSING
# ============================================================

@app.post("/detect/video")
async def detect_video(
    file: UploadFile = File(...),
    confidence: float = Form(default=0.25),
    frame_interval: int = Form(default=30),
    sector: str = Form(default="all"),
):
    """
    Upload a video → extract frames at intervals → run AI on each frame.
    Returns per-frame detections and an aggregate summary.
    frame_interval: extract 1 frame every N frames (default 30 = ~1 per second at 30fps)
    """
    import tempfile
    import cv2 as _cv2
    import base64 as _b64
    from PIL import Image as _PILImage

    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video (MP4, AVI, etc.)")

    # Save to temp file (OpenCV needs file path)
    video_bytes = await file.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(video_bytes)
    tmp.close()

    try:
        cap = _cv2.VideoCapture(tmp.name)
        if not cap.isOpened():
            raise HTTPException(400, "Could not open video file")

        total_frames = int(cap.get(_cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(_cv2.CAP_PROP_FPS) or 30
        duration = total_frames / fps if fps > 0 else 0

        detector = get_detector()
        frame_results = []
        frame_num = 0
        all_detections = []

        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_num % frame_interval == 0:
                # Convert BGR to RGB
                rgb = _cv2.cvtColor(frame, _cv2.COLOR_BGR2RGB)
                pil_img = _PILImage.fromarray(rgb)

                result = detector.detect(pil_img, confidence, sector)
                scored = compute_severity(result["detections"], result["image_width"], result["image_height"])
                ranked = rank_priorities(scored)

                timestamp_sec = round(frame_num / fps, 2)

                # Only include frames with detections
                if ranked:
                    frame_results.append({
                        "frame_number": frame_num,
                        "timestamp_sec": timestamp_sec,
                        "timestamp_display": f"{int(timestamp_sec//60)}:{int(timestamp_sec%60):02d}",
                        "detections": ranked,
                        "detection_count": len(ranked),
                        "annotated_image": result["annotated_image"],
                    })
                    all_detections.extend(ranked)

            frame_num += 1

            # Safety limit — max 100 frames processed
            if len(frame_results) >= 100:
                break

        cap.release()
        total_time = round((time.time() - start_time) * 1000, 1)

        # Aggregate stats
        stats = compute_overall_stats(all_detections)

        return {
            "video_info": {
                "filename": file.filename,
                "total_frames": total_frames,
                "fps": round(fps, 1),
                "duration_sec": round(duration, 1),
                "frames_analyzed": len(frame_results),
                "frame_interval": frame_interval,
            },
            "frame_results": frame_results,
            "aggregate_stats": stats,
            "total_detections": len(all_detections),
            "processing_time_ms": total_time,
        }

    finally:
        os.unlink(tmp.name)


@app.post("/detect/frame")
async def detect_single_frame(
    frame_data: str = Form(...),
    confidence: float = Form(default=0.25),
    sector: str = Form(default="all"),
):
    """
    Live feed: receive a single base64-encoded frame, return detections.
    Used by the frontend webcam/live camera feature.
    """
    import base64 as _b64
    from PIL import Image as _PILImage
    import io as _io

    try:
        # Strip data URL prefix if present
        if "," in frame_data:
            frame_data = frame_data.split(",")[1]

        img_bytes = _b64.b64decode(frame_data)
        pil_img = _PILImage.open(_io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid frame data")

    start_time = time.time()
    detector = get_detector()
    result = detector.detect(pil_img, confidence, sector)
    scored = compute_severity(result["detections"], result["image_width"], result["image_height"])
    ranked = rank_priorities(scored)
    inference_time = round((time.time() - start_time) * 1000, 1)

    return {
        "detections": ranked,
        "annotated_image": result["annotated_image"],
        "detection_count": len(ranked),
        "inference_time_ms": inference_time,
    }


@app.get("/repair-plan")
async def get_repair_plan():
    """
    Generate Today's Repair Plan — the 'What should I fix today?' feature.
    Aggregates all detections, ranks by priority, estimates costs.
    """
    all_detections = []
    for r in detection_store:
        for det in r["detections"]:
            det_copy = {**det}
            det_copy["source_scan"] = r["id"]
            det_copy["scan_time"] = r["timestamp"]
            loc = r.get("location", {})
            det_copy["location_name"] = loc.get("name") or r.get("filename", "Unknown")
            all_detections.append(det_copy)

    if not all_detections:
        return {
            "message": "No scans yet. Upload images to generate a repair plan.",
            "summary": None,
            "top_priorities": [],
        }

    plan = generate_repair_plan(all_detections, location="Survey Area")
    return plan


@app.get("/repair-plan/{detection_id}")
async def get_detection_repair_plan(detection_id: str):
    """Generate repair plan for a specific scan."""
    for r in detection_store:
        if r["id"] == detection_id:
            loc = r.get("location", {})
            location_name = loc.get("name") or r.get("filename", "Unknown")
            plan = generate_repair_plan(r["detections"], location=location_name)
            return plan
    raise HTTPException(404, "Detection not found")


# ============================================================
# ============================================================
# ADVANCED ANALYTICS
# ============================================================

@app.get("/analytics/wall-of-shame")
async def wall_of_shame():
    """Wall of Shame — contractor accountability leaderboard."""
    all_reports = citizen_reports + [r for r in detection_store if r.get("source") != "citizen_report"]
    return generate_wall_of_shame(all_reports)


@app.get("/analytics/heatmap")
async def damage_heatmap():
    """Smart Damage Heatmap data points."""
    all_reports = citizen_reports + [r for r in detection_store if r.get("source") != "citizen_report"]
    points = generate_heatmap_data(all_reports)
    return {"points": points, "total": len(points)}


@app.get("/analytics/priority-queue")
async def maintenance_priority():
    """Maintenance Priority Engine — what to fix first."""
    all_reports = citizen_reports + [r for r in detection_store if r.get("source") != "citizen_report"]
    priorities = generate_priority_queue(all_reports)
    return {"priorities": priorities[:10], "total_unfixed": len(priorities)}


@app.get("/analytics/city-health")
async def city_health():
    """Road Health Score per city/area."""
    all_reports = citizen_reports + [r for r in detection_store if r.get("source") != "citizen_report"]
    scores = generate_city_health_scores(all_reports)
    return {"cities": scores, "total_cities": len(scores)}


@app.get("/analytics/forecast")
async def area_forecast():
    """Predictive maintenance — which zones will fail next."""
    all_reports = citizen_reports + [r for r in detection_store if r.get("source") != "citizen_report"]
    return generate_area_forecast(all_reports)


@app.post("/analytics/before-after")
async def before_after_comparison(
    before_file: UploadFile = File(...),
    after_file: UploadFile = File(...),
    sector: str = Form(default="road"),
):
    """Before vs After — compare two images and show improvement."""
    detector = get_detector()

    before_bytes = await before_file.read()
    after_bytes = await after_file.read()

    before_result = detector.detect_from_bytes(before_bytes, 0.20, sector)
    after_result = detector.detect_from_bytes(after_bytes, 0.20, sector)

    before_scored = compute_severity(before_result["detections"], before_result["image_width"], before_result["image_height"])
    after_scored = compute_severity(after_result["detections"], after_result["image_width"], after_result["image_height"])

    before_stats = compute_overall_stats(before_scored)
    after_stats = compute_overall_stats(after_scored)

    # Calculate improvement
    sev_before = before_stats.get("avg_severity", 0)
    sev_after = after_stats.get("avg_severity", 0)
    improvement = round(((sev_before - sev_after) / max(sev_before, 1)) * 100, 1)

    return {
        "before": {
            "detections": len(before_scored),
            "avg_severity": sev_before,
            "integrity": before_stats.get("structural_integrity", 0),
            "annotated_image": before_result["annotated_image"],
        },
        "after": {
            "detections": len(after_scored),
            "avg_severity": sev_after,
            "integrity": after_stats.get("structural_integrity", 0),
            "annotated_image": after_result["annotated_image"],
        },
        "improvement_pct": improvement,
        "severity_reduced": round(sev_before - sev_after, 1),
        "verdict": "Improved" if improvement > 10 else "Minimal change" if improvement > -10 else "Worsened",
    }


# ============================================================
# PUBLIC CITIZEN APP ENDPOINTS
# ============================================================

# In-memory store for citizen reports
citizen_reports: list[dict] = []

@app.post("/public/report")
async def submit_citizen_report(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    sector: str = Form(default="road"),
    description: Optional[str] = Form(default=""),
    reporter_name: Optional[str] = Form(default="Anonymous"),
    location_name: Optional[str] = Form(default=""),
):
    """
    PUBLIC: Citizens submit damage reports with photo + GPS location.
    Auto-runs AI detection on the uploaded image.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    image_bytes = await file.read()

    # Run AI detection on citizen's photo
    start_time = time.time()
    detector = get_detector()
    result = detector.detect_from_bytes(image_bytes, 0.30, sector)
    inference_time = round((time.time() - start_time) * 1000, 1)

    scored = compute_severity(result["detections"], result["image_width"], result["image_height"])
    ranked = rank_priorities(scored)
    stats = compute_overall_stats(ranked)

    # ── Early exit: no substantial damage detected ──
    # Filter out weak/ambiguous detections; require at least one with decent confidence
    CONF_THRESHOLD = 0.35
    strong_detections = [d for d in ranked if d.get("confidence", 0) >= CONF_THRESHOLD]
    if not strong_detections:
        return {
            "id": None,
            "status": "no_damage",
            "message": "No infrastructure damage detected in this photo. Please take a clearer photo of road, building, pipeline, or bridge damage.",
            "detections_count": len(ranked),
            "max_confidence": max([d.get("confidence", 0) for d in ranked], default=0),
            "annotated_image": result["annotated_image"],
            "hint": "Tips: (1) Stand closer to the damage. (2) Good lighting helps. (3) Make sure the crack/pothole fills most of the frame.",
        }

    report_id = f"RPT-{str(uuid.uuid4())[:6].upper()}"
    report = {
        "id": report_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reporter": reporter_name,
        "description": description,
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "name": location_name,
        },
        "image_filename": file.filename,
        "annotated_image": result["annotated_image"],
        "detections": ranked,
        "stats": stats,
        "inference_time_ms": inference_time,
        # Government tracking fields
        "status": "submitted",
        "status_history": [
            {"status": "submitted", "time": datetime.now(timezone.utc).isoformat(), "note": "Citizen report received"}
        ],
        "assigned_to": None,
        "fix_date": None,
        "upvotes": 1,
    }

    # ── Run fraud detection (if enabled by govt admin) ──
    if not system_settings.get("fraud_detection_enabled", True):
        fraud_report = {"combined_trust_score": 100, "verdict": "trusted", "action": "auto_approve", "flags": [], "scores": {}, "checks": {}, "skipped": True}
    else:
        from PIL import Image as _PILImage
        import io as _io
        try:
            pil_img = _PILImage.open(_io.BytesIO(image_bytes)).convert("RGB")
            fraud_report = run_full_fraud_check(
                image=pil_img,
                latitude=latitude,
                longitude=longitude,
                detections=ranked,
                existing_reports=citizen_reports,
                user_token=reporter_name or "anonymous",
            )
        except Exception as e:
            print(f"[CRACKWATCH] Fraud check error: {e}")
            fraud_report = {"combined_trust_score": 75, "verdict": "trusted", "action": "auto_approve", "flags": [], "checks": {}}

    report["fraud_check"] = fraud_report
    report["trust_score"] = fraud_report["combined_trust_score"]

    # Block if trust score too low
    if fraud_report["action"] == "block_submission":
        return {
            "id": None,
            "status": "rejected",
            "message": "Report rejected — our system detected this may not be a genuine damage report.",
            "trust_score": fraud_report["combined_trust_score"],
            "flags": fraud_report["flags"],
            "fraud_check": fraud_report,
        }

    citizen_reports.append(report)

    # Also add to govt detection_store
    detection_store.append({
        "id": report_id,
        "timestamp": report["timestamp"],
        "filename": file.filename,
        "image_width": result["image_width"],
        "image_height": result["image_height"],
        "detections": ranked,
        "annotated_image": result["annotated_image"],
        "stats": stats,
        "inference_time_ms": inference_time,
        "location": report["location"],
        "source": "citizen_report",
        "trust_score": fraud_report["combined_trust_score"],
    })
    _persist_shared_store()

    # ── Award gamification points ──
    gamification_result = {}
    if fraud_report["action"] != "block_submission":
        try:
            gamification_result = award_points(reporter_name or "anonymous", report, ranked)
        except Exception as e:
            print(f"[CRACKWATCH] Gamification error: {e}")

    return {
        "id": report_id,
        "status": "submitted" if fraud_report["action"] == "auto_approve" else "under_review",
        "detections_count": len(ranked),
        "severity_summary": {
            "critical": stats["critical_count"],
            "warning": stats["warning_count"],
            "minor": stats["minor_count"],
        },
        "trust_score": fraud_report["combined_trust_score"],
        "trust_verdict": fraud_report["verdict"],
        "flags": fraud_report["flags"],
        "gamification": gamification_result,
        "message": (
            "Report submitted! Authorities have been notified."
            if fraud_report["action"] == "auto_approve"
            else "Report submitted for manual review — some anomalies were detected."
        ),
        "fraud_check": fraud_report,
    }


# ============================================================
# WHATSAPP BOT (Twilio Sandbox)
# ============================================================

def _twiml(text: str) -> Response:
    """Helper — wrap text in TwiML XML for Twilio to parse."""
    # Escape XML special chars
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    xml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'
    return Response(content=xml, media_type="application/xml")


async def _download_twilio_media(url: str) -> Optional[bytes]:
    """Fetch an image Twilio is hosting. Requires Account SID + Auth Token."""
    import httpx
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            r = await client.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            if r.status_code == 200:
                return r.content
    except Exception as e:
        print(f"[WhatsApp] Media download failed: {e}")
    return None


def _extract_gps_from_exif(image_bytes: bytes):
    """Pull GPS lat/lng from image EXIF data. Returns (lat, lng) or None."""
    try:
        from PIL import Image as _PILImage
        from PIL.ExifTags import TAGS, GPSTAGS
        img = _PILImage.open(io.BytesIO(image_bytes))
        exif = img._getexif() if hasattr(img, "_getexif") else None
        if not exif:
            return None
        for tag_id, val in exif.items():
            if TAGS.get(tag_id) == "GPSInfo":
                gps = {GPSTAGS.get(k, k): v for k, v in val.items()}
                def _dms_to_deg(dms, ref):
                    d = float(dms[0]); m = float(dms[1]); s = float(dms[2])
                    deg = d + m/60 + s/3600
                    if ref in ("S", "W"):
                        deg = -deg
                    return deg
                lat = _dms_to_deg(gps["GPSLatitude"], gps.get("GPSLatitudeRef", "N"))
                lng = _dms_to_deg(gps["GPSLongitude"], gps.get("GPSLongitudeRef", "E"))
                return (lat, lng)
    except Exception as e:
        print(f"[WhatsApp] EXIF parse failed: {e}")
    return None


# Per-phone session state — tracks pending photos + last interaction for stateful convo
whatsapp_sessions: dict[str, dict] = {}

WELCOME_MSG = (
    "👋 Welcome to *CRACKWATCH* — India's AI-powered infrastructure damage reporter.\n\n"
    "📸 *Step 1:* Send a photo of a pothole, crack, or damaged infrastructure.\n"
    "📍 *Step 2:* Share your location (tap 📎 → Location → Send current location).\n\n"
    "I'll detect the damage with AI, estimate repair cost, and submit it to authorities — all in under 10 seconds."
)

NO_DAMAGE_MSG = (
    "🤖 AI analysis complete.\n\n"
    "❌ *No clear damage detected* in this photo.\n\n"
    "💡 Tips:\n"
    "• Stand closer to the damage\n"
    "• Good lighting helps\n"
    "• Fill the frame with the crack/pothole\n\n"
    "Try another photo!"
)


def _finalize_whatsapp_report(phone: str, reporter: str, lat: float, lng: float, pending: dict, loc_source: str) -> Response:
    """Create the actual report once we have BOTH the photo (pre-detected) AND location."""
    ranked = pending["ranked"]
    strong = pending["strong"]
    annotated_image = pending["annotated_image"]
    image_width = pending["image_width"]
    image_height = pending["image_height"]
    stats = compute_overall_stats(ranked)

    report_id = f"RPT-{str(uuid.uuid4())[:6].upper()}"
    now_iso = datetime.now(timezone.utc).isoformat()
    report = {
        "id": report_id,
        "timestamp": now_iso,
        "reporter": reporter,
        "description": pending.get("description") or "(via WhatsApp)",
        "location": {"latitude": lat, "longitude": lng, "name": f"WhatsApp ({loc_source})"},
        "image_filename": f"whatsapp_{phone[-4:]}.jpg",
        "annotated_image": annotated_image,
        "detections": ranked,
        "stats": stats,
        "inference_time_ms": 0,
        "status": "submitted",
        "status_history": [{"status": "submitted", "time": now_iso, "note": "WhatsApp report received"}],
        "assigned_to": None,
        "fix_date": None,
        "upvotes": 1,
        "source": "whatsapp",
        "whatsapp_phone": phone,
        "trust_score": 90,
    }
    citizen_reports.append(report)
    detection_store.append({
        "id": report_id,
        "timestamp": now_iso,
        "filename": report["image_filename"],
        "image_width": image_width,
        "image_height": image_height,
        "detections": ranked,
        "annotated_image": annotated_image,
        "stats": stats,
        "inference_time_ms": 0,
        "location": report["location"],
        "source": "whatsapp_report",
        "trust_score": 90,
    })
    _persist_shared_store()

    gami = {}
    try:
        gami = award_points(reporter, report, ranked)
    except Exception as e:
        print(f"[WhatsApp] Gamification error: {e}")

    # Clear pending photo, save report id
    whatsapp_sessions[phone]["pending_photo"] = None
    whatsapp_sessions[phone]["last_report_id"] = report_id
    whatsapp_sessions[phone]["last_interaction"] = now_iso

    # Build reply
    top = strong[0]
    severity = top.get("severity", 0)
    cost = (top.get("cost") or {}).get("cost_estimated", 0)
    repair_method = (top.get("cost") or {}).get("repair_method", "Standard repair")
    icon = "🔴" if severity >= 70 else "🟡" if severity >= 40 else "🟢"
    loc_label = {"whatsapp_location": "📍 (from your WhatsApp location share)",
                 "exif": "📍 (from photo GPS)",
                 "default_mumbai": "📍 (default — Mumbai)"}.get(loc_source, "📍")

    lines = [
        f"✅ *Report {report_id}* submitted!",
        "",
        "🤖 AI Detection:",
        f"{icon} *{top.get('display_name', 'Damage')}*",
        f"• Severity: {severity:.0f}/100",
        f"• Confidence: {top.get('confidence', 0)*100:.0f}%",
        f"• {len(ranked)} defect(s) found",
        "",
        f"💰 Estimated repair: ₹{cost:,}",
        f"🔧 Method: {repair_method}",
        "",
        f"{loc_label}",
        f"   {lat:.4f}, {lng:.4f}",
    ]
    if gami and gami.get("points_earned", 0) > 0:
        lines += [
            "",
            f"🏆 +{gami['xp_earned']} XP · +{gami['coins_earned']} coins",
            f"📊 Level {gami.get('level', 1)}" + (f" · 🔥 {gami['streak_days']}-day streak" if gami.get("streak_days", 0) > 0 else ""),
        ]
        if gami.get("new_achievements"):
            lines.append(f"🏅 New badge: {gami['new_achievements'][0]['name']}")
    lines += [
        "",
        "🔗 Track on the public map.",
        "Authority has been notified. Thank you!",
    ]
    return _twiml("\n".join(lines))


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(default=""),
    NumMedia: int = Form(default=0),
    MediaUrl0: Optional[str] = Form(default=None),
    MediaContentType0: Optional[str] = Form(default=None),
    Latitude: Optional[float] = Form(default=None),
    Longitude: Optional[float] = Form(default=None),
    ProfileName: Optional[str] = Form(default="Citizen"),
):
    """
    Stateful WhatsApp webhook — two-step flow:
      1. User sends photo  → AI detection runs, bot asks for location
      2. User shares location → report finalized, bot replies with full summary
    """
    body = (Body or "").strip().lower()
    phone = From.replace("whatsapp:", "")
    reporter = ProfileName or f"WhatsApp {phone[-4:]}"
    session = whatsapp_sessions.setdefault(phone, {"pending_photo": None})

    # ─── Path 1: User shared a LOCATION (no image attached) ───
    if Latitude is not None and Longitude is not None and NumMedia == 0:
        pending = session.get("pending_photo")
        if not pending:
            return _twiml(
                "📍 Got your location — but I don't have a damage photo yet!\n\n"
                "Please send a *photo* of the damage first, then share this location again."
            )
        # Check pending photo age (expire after 15 min)
        try:
            p_ts = datetime.fromisoformat(pending["timestamp"])
            age_min = (datetime.now(timezone.utc) - p_ts).total_seconds() / 60
            if age_min > 15:
                session["pending_photo"] = None
                return _twiml("⏱️ Your previous photo expired (>15 min). Please send a fresh photo.")
        except Exception:
            pass
        return _finalize_whatsapp_report(phone, reporter, float(Latitude), float(Longitude), pending, "whatsapp_location")

    # ─── Path 2: User sent a PHOTO ───
    if NumMedia > 0:
        if not (MediaContentType0 or "").startswith("image/"):
            return _twiml("⚠️ Only image attachments are supported right now.")

        image_bytes = await _download_twilio_media(MediaUrl0)
        if not image_bytes:
            return _twiml("❌ Couldn't download your image. Please try again.")

        # Run AI detection immediately so user gets instant feedback
        detector = get_detector()
        result = detector.detect_from_bytes(image_bytes, 0.30, "all")
        scored = compute_severity(result["detections"], result["image_width"], result["image_height"])
        ranked = rank_priorities(scored)
        strong = [d for d in ranked if d.get("confidence", 0) >= 0.35]

        if not strong:
            # Clear any pending photo — this one was invalid
            session["pending_photo"] = None
            return _twiml(NO_DAMAGE_MSG)

        # Store pending state (image bytes NOT kept — annotated base64 is enough)
        pending = {
            "annotated_image": result["annotated_image"],
            "image_width": result["image_width"],
            "image_height": result["image_height"],
            "ranked": ranked,
            "strong": strong,
            "description": Body,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        session["pending_photo"] = pending

        # Try EXIF GPS first (rare — WhatsApp strips this — but try anyway)
        exif = _extract_gps_from_exif(image_bytes)
        if exif:
            return _finalize_whatsapp_report(phone, reporter, exif[0], exif[1], pending, "exif")

        # Otherwise, ask for location explicitly
        top = strong[0]
        severity = top.get("severity", 0)
        icon = "🔴" if severity >= 70 else "🟡" if severity >= 40 else "🟢"
        return _twiml(
            "📸 *Got your photo!*\n\n"
            f"🤖 AI preview:\n"
            f"{icon} *{top.get('display_name', 'Damage')}* ({top.get('confidence', 0)*100:.0f}% confidence, {severity:.0f}/100 severity)\n\n"
            "📍 *Now share your location* so we can map exactly where this is:\n"
            "Tap 📎 (attachment) → *Location* → *Send current location*\n\n"
            "_Your report will be finalized as soon as location arrives._"
        )

    # ─── Path 3: Text message (greeting or unknown) ───
    if body in ("hi", "hello", "help", "start", "hey", "menu", ""):
        return _twiml(WELCOME_MSG)
    return _twiml(
        "I didn't catch that. 🤖\n\n"
        "Send me a *photo* of damage, or reply 'help' for instructions."
    )


# ============================================================
# GAMIFICATION ENDPOINTS
# ============================================================

@app.get("/gamification/leaderboard")
async def leaderboard():
    """Pothole Hunter leaderboard — top citizens by XP."""
    return {"leaderboard": get_leaderboard(20)}


@app.get("/gamification/profile/{user_id}")
async def user_profile(user_id: str):
    """Get full user gamification profile."""
    return get_user_profile_full(user_id)


@app.get("/gamification/challenges/{user_id}")
async def daily_challenges(user_id: str):
    """Get today's challenges with progress."""
    return {"challenges": get_daily_challenges(user_id)}


@app.post("/gamification/verify")
async def verify_report(
    report_id: str = Form(...),
    voter_id: str = Form(...),
    vote: str = Form(...),
):
    """Community verification vote — valid or invalid."""
    if vote not in ("valid", "invalid"):
        raise HTTPException(400, "Vote must be 'valid' or 'invalid'")
    return community_vote(report_id, voter_id, vote)


@app.get("/gamification/ai-challenge")
async def ai_challenge():
    """Get an AI Challenge Mode round."""
    return ai_challenge_round()


@app.post("/gamification/ai-challenge/answer")
async def ai_challenge_answer(
    user_id: str = Form(...),
    answer: str = Form(...),
    correct_answer: str = Form(...),
):
    """Submit AI challenge answer."""
    return check_ai_challenge(user_id, answer, correct_answer)


@app.get("/gamification/fix-streaks")
async def fix_streaks():
    """Authority fix streak leaderboard."""
    all_reports = citizen_reports + [r for r in detection_store if r.get("source") != "citizen_report"]
    return {"streaks": get_authority_fix_streaks(all_reports)}


@app.post("/gamification/seed-demo")
async def seed_demo_gamification():
    """Seed demo gamification data for presentation."""
    from gamification import user_profiles, get_or_create_profile, calculate_level, ACHIEVEMENTS
    import random

    demo = [
        ("Saud Vinchu", 3200, 180, 45, 21, ["first_report","five_reports","ten_reports","twenty_five_reports","streak_3","streak_7","critical_finder","fast_reporter","multi_sector","ai_challenger"]),
        ("Amit Kumar", 2100, 120, 38, 12, ["first_report","five_reports","ten_reports","twenty_five_reports","streak_3","streak_7","critical_finder"]),
        ("Priya Sharma", 1650, 95, 22, 8, ["first_report","five_reports","ten_reports","streak_3","fast_reporter","verifier"]),
        ("Vikram Thakur", 1400, 80, 28, 15, ["first_report","five_reports","ten_reports","streak_3","streak_7","critical_finder"]),
        ("Rahul Mehta", 1100, 60, 15, 5, ["first_report","five_reports","ten_reports","streak_3"]),
        ("Anjali Rao", 850, 45, 14, 4, ["first_report","five_reports","ten_reports"]),
        ("Neha Desai", 650, 35, 9, 3, ["first_report","five_reports"]),
        ("Kiran Patil", 400, 20, 7, 1, ["first_report","five_reports"]),
        ("Dhrupad R.", 300, 15, 5, 2, ["first_report","five_reports"]),
        ("Anshika S.", 200, 10, 3, 1, ["first_report"]),
    ]

    for name, xp, coins, reports, streak, achs in demo:
        profile = get_or_create_profile(name, name)
        profile["xp"] = xp
        profile["coins"] = coins
        profile["total_reports"] = reports
        profile["streak_days"] = streak
        profile["achievements"] = achs
        profile["level"] = calculate_level(xp)
        profile["verifications"] = random.randint(2, 15)
        profile["ai_challenge_score"] = random.randint(5, 20)
        profile["ai_challenges_played"] = random.randint(8, 25)
        profile["last_report_date"] = datetime.now(timezone.utc).date().isoformat()

    return {"seeded": len(demo), "message": "Demo gamification data loaded!"}


@app.post("/admin/reports/seed-demo")
async def seed_demo_reports():
    """Seed demo citizen reports for presentation — same data visible on govt + public apps."""
    demo = [
        ("RPT-001", 19.0330, 73.0297, "Ghodbunder Road, Thane",        "Pothole",           82, "submitted",    23, 3, "Rahul M.",      "Massive pothole near bus stop, bikes at risk",                      "2026-04-13T09:42:00Z", 4500, "Hot mix asphalt patching"),
        ("RPT-002", 19.0176, 73.0596, "Panvel Station Road",           "Alligator Crack",   65, "in_progress", 12, 2, "Priya S.",      "Road surface breaking apart near railway crossing",                 "2026-04-12T14:07:00Z", 3200, "Mill and overlay"),
        ("RPT-003", 19.0450, 73.0200, "Mumbai-Pune Expressway KM 42",  "Pothole",           91, "submitted",   47, 5, "Saud Vinchu",   "Multiple deep potholes, caused 2 accidents last week",              "2026-04-11T08:23:00Z", 8500, "Deep patching + sealant"),
        ("RPT-004", 19.0280, 73.0450, "Amity University Road",         "Transverse Crack",  28, "fixed",        5, 1, "Saud Vinchu",   "Minor crack near university gate",                                  "2026-04-10T17:50:00Z",  800, "Crack sealing"),
        ("RPT-005", 19.0550, 73.0100, "Kalamboli Flyover",             "Pothole",           73, "acknowledged",18, 2, "Neha D.",       "Pothole on flyover causing traffic slowdown",                       "2026-04-09T11:30:00Z", 5200, "Hot mix patching"),
        ("RPT-006", 19.0100, 73.0700, "Old Panvel Bridge",             "Alligator Crack",   87, "submitted",   34, 4, "Saud Vinchu",   "Bridge surface severely cracked, structural concern",               "2026-04-08T06:15:00Z", 9800, "Full-depth reconstruction"),
        ("RPT-007", 19.0380, 73.0350, "Kharghar Sector 12",            "Surface Spalling",  45, "in_progress",  8, 1, "Anjali R.",     "Concrete surface peeling off on main road",                         "2026-04-13T20:00:00Z", 1800, "Resurfacing"),
        ("RPT-008", 19.0600, 73.0050, "Belapur CBD",                   "Longitudinal Crack",38, "fixed",        3, 1, "Kiran P.",      "Long crack along road, was fixed last week",                        "2026-04-07T15:45:00Z",  950, "Crack sealing"),
    ]

    existing_ids = {r["id"] for r in citizen_reports}
    seeded = 0
    for rid, lat, lng, loc_name, dtype, severity, status, upvotes, defects, reporter, desc, ts, cost, method in demo:
        if rid in existing_ids:
            continue
        citizen_reports.append({
            "id": rid,
            "timestamp": ts,
            "reporter": reporter,
            "description": desc,
            "location": {"latitude": lat, "longitude": lng, "name": loc_name},
            "image_filename": "",
            "annotated_image": "",
            "detections": [{
                "display_name": dtype,
                "class_name": dtype.lower().replace(" ", "_"),
                "severity": severity,
                "confidence": 0.92,
                "cost": {"cost_estimated": cost, "repair_method": method},
            }],
            "stats": {"avg_severity": severity, "total_defects": defects, "critical": 1 if severity >= 70 else 0, "warning": 1 if 40 <= severity < 70 else 0, "minor": 1 if severity < 40 else 0},
            "inference_time_ms": 0,
            "status": status,
            "status_history": [{"status": status, "time": ts, "note": "Demo seeded report"}],
            "assigned_to": None,
            "fix_date": None,
            "upvotes": upvotes,
            "trust_score": 95,
            "fraud_check": {"combined_trust_score": 95, "verdict": "trusted", "action": "auto_approve", "flags": []},
        })
        seeded += 1

    return {"seeded": seeded, "total_reports": len(citizen_reports), "message": f"Seeded {seeded} demo reports"}


@app.get("/gamification/achievements")
async def all_achievements():
    """List all available achievements."""
    from gamification import ACHIEVEMENTS
    return {"achievements": [{"id": k, **v} for k, v in ACHIEVEMENTS.items()]}


@app.get("/public/reports/map")
async def get_map_reports():
    """PUBLIC: All reports for map display (lightweight, no images)."""
    _reload_shared_store()
    map_data = []
    for r in citizen_reports:
        loc = r["location"]
        if loc["latitude"] and loc["longitude"]:
            damage_type = r["detections"][0].get("display_name", "Damage") if r["detections"] else "Unknown"
            map_data.append({
                "id": r["id"],
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "location_name": loc.get("name", ""),
                "damage_type": damage_type,
                "severity": r["stats"].get("avg_severity", 0),
                "status": r["status"],
                "timestamp": r["timestamp"],
                "reporter": r["reporter"],
                "description": r["description"],
                "upvotes": r["upvotes"],
                "defect_count": r["stats"]["total_defects"],
            })
    return {"reports": map_data, "total": len(map_data)}


@app.get("/public/reports/map/detail")
async def get_map_reports_with_images():
    """PUBLIC: All reports WITH annotated images for detail view."""
    _reload_shared_store()
    map_data = []
    for r in citizen_reports:
        loc = r["location"]
        if loc["latitude"] and loc["longitude"]:
            damage_type = r["detections"][0].get("display_name", "Damage") if r["detections"] else "Unknown"
            # Include cost from first detection
            cost_est = 0
            repair_method = ""
            if r["detections"]:
                c = r["detections"][0].get("cost", {})
                cost_est = c.get("cost_estimated", 0)
                repair_method = c.get("repair_method", "")

            map_data.append({
                "id": r["id"],
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "location_name": loc.get("name", ""),
                "damage_type": damage_type,
                "severity": r["stats"].get("avg_severity", 0),
                "status": r["status"],
                "timestamp": r["timestamp"],
                "reporter": r["reporter"],
                "description": r["description"],
                "upvotes": r["upvotes"],
                "defect_count": r["stats"]["total_defects"],
                "annotated_image": r.get("annotated_image", ""),
                "cost_estimated": cost_est,
                "repair_method": repair_method,
                "status_history": r.get("status_history", []),
            })
    return {"reports": map_data, "total": len(map_data)}


@app.get("/admin/reports/map")
async def get_admin_map_reports():
    """ADMIN: All reports with images + admin controls for government dashboard."""
    _reload_shared_store()
    map_data = []
    for r in citizen_reports:
        loc = r["location"]
        if loc["latitude"] and loc["longitude"]:
            damage_type = r["detections"][0].get("display_name", "Damage") if r["detections"] else "Unknown"
            cost_est = 0
            repair_method = ""
            if r["detections"]:
                c = r["detections"][0].get("cost", {})
                cost_est = c.get("cost_estimated", 0)
                repair_method = c.get("repair_method", "")

            map_data.append({
                "id": r["id"],
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "location_name": loc.get("name", ""),
                "damage_type": damage_type,
                "severity": r["stats"].get("avg_severity", 0),
                "status": r["status"],
                "timestamp": r["timestamp"],
                "reporter": r["reporter"],
                "description": r["description"],
                "upvotes": r["upvotes"],
                "defect_count": r["stats"]["total_defects"],
                "annotated_image": r.get("annotated_image", ""),
                "cost_estimated": cost_est,
                "repair_method": repair_method,
                "status_history": r.get("status_history", []),
                "assigned_to": r.get("assigned_to"),
                "detections": r.get("detections", []),
            })
    return {"reports": map_data, "total": len(map_data)}


@app.get("/public/reports/{report_id}")
async def get_citizen_report(report_id: str):
    """PUBLIC: Full details of a specific report."""
    for r in citizen_reports:
        if r["id"] == report_id:
            return r
    raise HTTPException(404, "Report not found")


@app.post("/public/reports/{report_id}/upvote")
async def upvote_report(report_id: str):
    """PUBLIC: Upvote a report to increase priority."""
    for r in citizen_reports:
        if r["id"] == report_id:
            r["upvotes"] += 1
            return {"id": report_id, "upvotes": r["upvotes"]}
    raise HTTPException(404, "Report not found")


@app.get("/public/stats")
async def get_public_transparency_stats():
    """PUBLIC: Government transparency & accountability stats."""
    total = len(citizen_reports)
    fixed = sum(1 for r in citizen_reports if r["status"] == "fixed")
    in_progress = sum(1 for r in citizen_reports if r["status"] == "in_progress")
    acknowledged = sum(1 for r in citizen_reports if r["status"] == "acknowledged")
    pending = sum(1 for r in citizen_reports if r["status"] == "submitted")

    addressed = fixed + in_progress + acknowledged
    performance_score = round((addressed / total * 100) if total > 0 else 0, 1)

    total_cost = 0
    for r in citizen_reports:
        for det in r.get("detections", []):
            if "cost" in det:
                total_cost += det["cost"].get("cost_estimated", 0)

    return {
        "total_reports": total,
        "fixed": fixed,
        "in_progress": in_progress,
        "acknowledged": acknowledged,
        "pending": pending,
        "performance_score": performance_score,
        "total_estimated_cost": total_cost,
        "total_estimated_cost_formatted": f"₹{total_cost:,}",
    }


@app.patch("/admin/reports/{report_id}/status")
async def update_report_status(
    report_id: str,
    status: str = Form(...),
    note: str = Form(default=""),
):
    """ADMIN: Update report status (submitted → acknowledged → in_progress → fixed)."""
    valid_statuses = ["submitted", "acknowledged", "in_progress", "fixed"]
    if status not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of: {valid_statuses}")

    for r in citizen_reports:
        if r["id"] == report_id:
            r["status"] = status
            r["status_history"].append({
                "status": status,
                "time": datetime.now(timezone.utc).isoformat(),
                "note": note,
            })
            if status == "fixed":
                r["fix_date"] = datetime.now(timezone.utc).isoformat()
            return {"id": report_id, "status": status, "message": f"Status updated to {status}"}

    raise HTTPException(404, "Report not found")
