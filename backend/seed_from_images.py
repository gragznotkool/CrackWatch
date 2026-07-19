"""
One-shot demo seeding script.

Reads all images from C:\\Users\\topaz\\OneDrive\\Desktop\\Cracks, runs the full
AI detection pipeline on each, and writes 20 rich citizen_reports to
shared_store.json (spread across Mumbai + Navi Mumbai landmarks).

Run once:    python seed_from_images.py
Then restart (or just reload) both backends — they'll pick up shared_store.json.
"""

import json
import uuid
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

from inference import get_detector
from severity import compute_severity, compute_overall_stats
from cost_engine import rank_priorities

# ── Paths ──
BACKEND_DIR = Path(__file__).parent
CRACKS_DIR = Path(r"C:\Users\topaz\OneDrive\Desktop\Cracks")
OUTPUT_FILE = BACKEND_DIR / "shared_store.json"

# ── 20 locations across Mumbai + Navi Mumbai ──
LOCATIONS = [
    # Mumbai
    (18.9430, 72.8238, "Marine Drive, South Mumbai"),
    (19.0434, 72.8198, "Bandra-Worli Sea Link"),
    (19.0178, 72.8478, "Dadar TT Circle"),
    (19.1197, 72.8464, "Andheri East, WEH"),
    (19.1181, 72.9026, "Powai Lake Road"),
    (19.0680, 72.8680, "BKC, Bandra"),
    (19.1358, 72.8340, "Lokhandwala, Andheri West"),
    (19.0627, 72.8994, "Chembur Diamond Garden"),
    (19.0870, 72.9080, "Ghatkopar East"),
    (19.2307, 72.8567, "Borivali West, Linking Rd"),
    # Navi Mumbai
    (19.0770, 72.9989, "Vashi Sector 17"),
    (19.0330, 73.0190, "Nerul, Palm Beach Rd"),
    (19.0150, 73.0380, "Belapur CBD"),
    (19.0420, 73.0600, "Kharghar Sector 12"),
    (18.9897, 73.1100, "Panvel Station Road"),
    (19.1570, 72.9980, "Airoli Bridge"),
    (19.0200, 73.0170, "Seawoods Darave"),
    (19.1050, 73.0127, "Kopar Khairane Sec 11"),
    (19.0670, 73.1028, "Taloja MIDC"),
    (18.8767, 72.9500, "Uran Road Junction"),
]

REPORTERS = [
    "Saud Vinchu", "Amit Kumar", "Priya Sharma", "Vikram Thakur",
    "Rahul Mehta", "Anjali Rao", "Neha Desai", "Kiran Patil",
    "Anonymous", "Dhrupad R.", "Anshika S.", "Citizen",
]

STATUSES_WEIGHTED = (
    ["submitted"] * 9 +
    ["in_progress"] * 5 +
    ["acknowledged"] * 3 +
    ["fixed"] * 3
)

DESCRIPTIONS_BY_TYPE = {
    "Potholes": [
        "Deep pothole right before the bus stop — two-wheelers swerving dangerously.",
        "Wide crater in the fast lane, already caused a fender-bender yesterday.",
        "Massive pothole near the signal; rainwater accumulating.",
        "Pothole cluster — 4 within 10 meters. Entire stretch needs resurfacing.",
    ],
    "Alligator Crack": [
        "Road surface breaking into a honeycomb pattern near the junction.",
        "Extensive alligator cracking — looks like the base layer is failing.",
        "Structural crack network spreading across both lanes.",
    ],
    "Longitudinal Crack": [
        "Long crack running parallel to lane markings — 20+ meter stretch.",
        "Linear crack along the centerline, gradually widening.",
    ],
    "Transverse Crack": [
        "Thermal crack across the full road width.",
        "Transverse cracks spaced ~5m apart throughout this block.",
    ],
    "Surface Spalling": [
        "Concrete surface peeling and flaking — reinforcement exposed.",
    ],
    "default": [
        "Infrastructure damage reported by citizen — needs immediate inspection.",
        "Significant pavement distress; priority repair recommended.",
    ],
}


def pick_desc(display_name: str) -> str:
    bucket = DESCRIPTIONS_BY_TYPE.get(display_name, DESCRIPTIONS_BY_TYPE["default"])
    return random.choice(bucket)


def build_status_history(final_status: str, created_iso: str):
    history = [{"status": "submitted", "time": created_iso, "note": "Citizen report received"}]
    if final_status in ("acknowledged", "in_progress", "fixed"):
        ack_time = (datetime.fromisoformat(created_iso) + timedelta(hours=random.randint(4, 48))).isoformat()
        history.append({"status": "acknowledged", "time": ack_time, "note": "Inspector assigned"})
    if final_status in ("in_progress", "fixed"):
        ip_time = (datetime.fromisoformat(created_iso) + timedelta(days=random.randint(1, 4))).isoformat()
        history.append({"status": "in_progress", "time": ip_time, "note": "Repair crew dispatched"})
    if final_status == "fixed":
        fix_time = (datetime.fromisoformat(created_iso) + timedelta(days=random.randint(2, 10))).isoformat()
        history.append({"status": "fixed", "time": fix_time, "note": "Repair completed"})
    return history


def main():
    random.seed(42)  # deterministic demo data

    images = sorted(CRACKS_DIR.glob("*.jpeg")) + sorted(CRACKS_DIR.glob("*.jpg")) + sorted(CRACKS_DIR.glob("*.png"))
    if not images:
        print(f"❌ No images found in {CRACKS_DIR}")
        return

    print(f"📁 Found {len(images)} images in {CRACKS_DIR}")

    # Pre-run detection once per unique image (expensive) — reuse twice for 20 reports
    detector = get_detector()
    img_results = []
    for i, img_path in enumerate(images):
        print(f"[{i+1}/{len(images)}] Detecting: {img_path.name}")
        img_bytes = img_path.read_bytes()
        try:
            res = detector.detect_from_bytes(img_bytes, 0.25, "all")
            scored = compute_severity(res["detections"], res["image_width"], res["image_height"])
            ranked = rank_priorities(scored)
            strong = [d for d in ranked if d.get("confidence", 0) >= 0.30]
            if not strong and ranked:
                strong = ranked[:1]  # fallback to keep a report if detection weak
            img_results.append({
                "image_bytes_len": len(img_bytes),
                "annotated_image": res["annotated_image"],
                "image_width": res["image_width"],
                "image_height": res["image_height"],
                "ranked": ranked,
                "strong": strong,
                "filename": img_path.name,
            })
        except Exception as e:
            print(f"  ⚠️  Detection failed: {e}")

    # Build 20 reports: cycle through results, each image reused twice
    num_reports = min(20, len(img_results) * 2)
    print(f"\n🏗️  Building {num_reports} reports across Mumbai + Navi Mumbai...")

    reports = []
    detection_store_entries = []
    now = datetime.now(timezone.utc)

    for i in range(num_reports):
        result = img_results[i % len(img_results)]
        ranked = result["ranked"]
        if not ranked:
            continue
        top = ranked[0]
        display_name = top.get("display_name", "Damage")
        severity = top.get("severity", 0)
        stats = compute_overall_stats(ranked)

        # Location
        lat, lng, loc_name = LOCATIONS[i]

        # Timestamp — last 14 days, spread
        hours_ago = random.randint(2, 14 * 24)
        ts = (now - timedelta(hours=hours_ago)).isoformat()

        # Status
        status = STATUSES_WEIGHTED[i % len(STATUSES_WEIGHTED)]

        # Upvotes — scale with severity
        upvote_base = int(5 + severity * 0.4)
        upvotes = upvote_base + random.randint(-2, 15)

        # Report ID
        rid = f"RPT-{str(uuid.uuid4())[:6].upper()}"

        # Reporter
        reporter = random.choice(REPORTERS)

        report = {
            "id": rid,
            "timestamp": ts,
            "reporter": reporter,
            "description": pick_desc(display_name),
            "location": {"latitude": lat, "longitude": lng, "name": loc_name},
            "image_filename": result["filename"],
            "annotated_image": result["annotated_image"],
            "detections": ranked,
            "stats": stats,
            "inference_time_ms": random.randint(620, 860),
            "status": status,
            "status_history": build_status_history(status, ts),
            "assigned_to": None if status == "submitted" else random.choice(["Inspector Sharma", "Er. Patel", "Officer Kumar"]),
            "fix_date": (datetime.fromisoformat(ts) + timedelta(days=random.randint(3, 14))).isoformat() if status == "fixed" else None,
            "upvotes": upvotes,
            "source": "seeded_demo",
            "trust_score": random.randint(82, 98),
            "fraud_check": {"combined_trust_score": 90, "verdict": "trusted", "action": "auto_approve", "flags": []},
        }
        reports.append(report)

        detection_store_entries.append({
            "id": rid,
            "timestamp": ts,
            "filename": result["filename"],
            "image_width": result["image_width"],
            "image_height": result["image_height"],
            "detections": ranked,
            "annotated_image": result["annotated_image"],
            "stats": stats,
            "inference_time_ms": report["inference_time_ms"],
            "location": report["location"],
            "source": "seeded_demo",
            "trust_score": report["trust_score"],
        })

        print(f"  #{i+1:02d}  {rid}  {display_name:<20} {loc_name:<30} {status}")

    # Write shared_store.json
    OUTPUT_FILE.write_text(json.dumps({
        "citizen_reports": reports,
        "detection_store": detection_store_entries,
    }, default=str))

    print(f"\n✅ Wrote {len(reports)} reports to {OUTPUT_FILE}")
    print("ℹ️  Backends will load on next read endpoint call (via _reload_shared_store).")
    print("💡 If seeded data doesn't show up, hit any map endpoint — e.g.:")
    print("     curl -k https://10.5.221.246:8000/admin/reports/map")


if __name__ == "__main__":
    main()
