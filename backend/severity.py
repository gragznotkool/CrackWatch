"""
Severity scoring engine for detected infrastructure damage.
Composite score from: area ratio, confidence, density, damage type.
"""

DAMAGE_WEIGHTS = {
    "crack": 0.7,
    "pothole": 1.0,
    "spalling": 0.5,
    "corrosion": 0.6,
    "leak": 0.9,
    "D00": 0.7,
    "D10": 0.75,
    "D20": 1.0,
    "D40": 0.9,
    "building_crack": 0.85,
    "pipe_damage": 0.95,
    "Longitudinal Crack": 0.7,
    "Transverse Crack": 0.75,
    "Alligator Crack": 1.0,
    "Potholes": 0.9,
}

def compute_severity(detections: list, image_width: int, image_height: int) -> list:
    """
    Add severity scores to each detection.

    Each detection dict should have:
        - bbox: [x1, y1, x2, y2]
        - confidence: float
        - class_name: str

    Returns detections with added 'severity' (0-100) and 'severity_label' fields.
    """
    image_area = image_width * image_height
    total_detections = len(detections)

    scored = []
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        bbox_area = (x2 - x1) * (y2 - y1)
        area_ratio = bbox_area / image_area if image_area > 0 else 0

        confidence = det["confidence"]
        class_name = det["class_name"].lower()

        # Density factor: more detections = worse structural condition
        density = min(total_detections / 10, 1.0)

        # Type weight
        type_weight = DAMAGE_WEIGHTS.get(class_name, 0.5)

        # Composite severity (0-100)
        raw = (
            0.30 * min(area_ratio * 50, 1.0) +  # area contribution (larger = worse)
            0.25 * confidence +                    # model certainty
            0.20 * density +                       # damage density
            0.25 * type_weight                     # damage type severity
        )
        severity = round(min(raw * 100, 100), 1)

        # Label
        if severity >= 70:
            label = "critical"
        elif severity >= 40:
            label = "warning"
        else:
            label = "minor"

        scored.append({
            **det,
            "severity": severity,
            "severity_label": label,
            "area_ratio": round(area_ratio * 100, 2),
        })

    # Sort by severity descending
    scored.sort(key=lambda x: x["severity"], reverse=True)
    return scored


def compute_overall_stats(detections: list) -> dict:
    """Compute aggregate statistics from all detections."""
    if not detections:
        return {
            "total_defects": 0,
            "critical_count": 0,
            "warning_count": 0,
            "minor_count": 0,
            "avg_severity": 0,
            "max_severity": 0,
            "structural_integrity": 100,
            "damage_types": {},
        }

    severities = [d["severity"] for d in detections]
    labels = [d["severity_label"] for d in detections]

    # Count damage types
    type_counts = {}
    for d in detections:
        name = d["class_name"]
        type_counts[name] = type_counts.get(name, 0) + 1

    avg_sev = sum(severities) / len(severities)
    max_sev = max(severities)

    # Structural integrity: inverse of aggregate damage
    integrity = max(0, 100 - (avg_sev * 0.6 + max_sev * 0.4))

    return {
        "total_defects": len(detections),
        "critical_count": labels.count("critical"),
        "warning_count": labels.count("warning"),
        "minor_count": labels.count("minor"),
        "avg_severity": round(avg_sev, 1),
        "max_severity": round(max_sev, 1),
        "structural_integrity": round(integrity, 1),
        "damage_types": type_counts,
    }
