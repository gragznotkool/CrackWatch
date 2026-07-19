"""
CRACKWATCH Predictive Maintenance Engine.
Predicts future damage progression based on current detection data.

Model: Rule-based prediction using damage type, severity, age, and environmental factors.
In production, this would be an ML model trained on historical progression data.
"""

from datetime import datetime, timezone
import math

# Damage progression rates (days to worsen by severity tier)
PROGRESSION_RATES = {
    "Longitudinal Crack": {
        "growth_rate": 0.8,       # mm/day width growth
        "to_pothole_days": 90,    # days until it becomes a pothole if untreated
        "worsen_factor": 1.2,     # severity increase per week
        "risk": "Develops into transverse cracks, then alligator pattern. Water ingress accelerates failure.",
    },
    "Transverse Crack": {
        "growth_rate": 1.0,
        "to_pothole_days": 60,
        "worsen_factor": 1.5,
        "risk": "Indicates thermal stress or base failure. Leads to block cracking and eventual pothole.",
    },
    "Alligator Crack": {
        "growth_rate": 2.5,
        "to_pothole_days": 21,
        "worsen_factor": 2.0,
        "risk": "CRITICAL — Interconnected fatigue cracks. Imminent pothole formation. Structural failure in progress.",
    },
    "Potholes": {
        "growth_rate": 5.0,
        "to_pothole_days": 0,     # Already a pothole
        "worsen_factor": 3.0,
        "risk": "Active pothole expands rapidly with traffic and rain. Accident risk increases daily.",
    },
    "Building/Wall Crack": {
        "growth_rate": 0.3,
        "to_pothole_days": 180,
        "worsen_factor": 0.8,
        "risk": "May indicate foundation settlement. Monitor for widening. Structural assessment needed if > 2mm.",
    },
    "Surface Spalling": {
        "growth_rate": 1.5,
        "to_pothole_days": 45,
        "worsen_factor": 1.3,
        "risk": "Concrete surface deterioration exposes rebar to corrosion. Leads to structural weakening.",
    },
    "Pipeline Break / Damage": {
        "growth_rate": 0,
        "to_pothole_days": 14,
        "worsen_factor": 2.5,
        "risk": "Water leak undermines road base. Sudden collapse possible. Emergency priority.",
    },
    "Corrosion / Rust": {
        "growth_rate": 0.5,
        "to_pothole_days": 120,
        "worsen_factor": 1.0,
        "risk": "Metal structural member weakening. Load capacity reduces over time.",
    },
    "Water Stain / Leak": {
        "growth_rate": 0,
        "to_pothole_days": 30,
        "worsen_factor": 1.8,
        "risk": "Subsurface erosion in progress. Road may collapse without visible warning.",
    },
}

# Monsoon acceleration (India-specific)
MONSOON_MONTHS = {6, 7, 8, 9}  # June-September
MONSOON_MULTIPLIER = 2.5  # Damage progresses 2.5x faster during monsoon


def predict_damage_progression(detection: dict, report_timestamp: str = None) -> dict:
    """
    Predict how a detected damage will progress over time.
    Returns timeline with severity predictions.
    """
    damage_type = detection.get("display_name", detection.get("class_name", "Unknown"))
    current_severity = detection.get("severity", 50)
    confidence = detection.get("confidence", 0.5)

    # Get progression data
    prog = PROGRESSION_RATES.get(damage_type, PROGRESSION_RATES.get("Longitudinal Crack"))

    now = datetime.now(timezone.utc)
    current_month = now.month
    is_monsoon = current_month in MONSOON_MONTHS
    weather_mult = MONSOON_MULTIPLIER if is_monsoon else 1.0

    # Calculate timeline predictions
    worsen_per_week = prog["worsen_factor"] * weather_mult
    days_to_pothole = max(0, prog["to_pothole_days"] * (1 - current_severity / 100) / weather_mult)

    # Severity predictions at different timepoints
    timeline = []
    for weeks in [1, 2, 4, 8, 12]:
        future_severity = min(100, current_severity + (worsen_per_week * weeks))
        status = (
            "critical" if future_severity >= 80 else
            "warning" if future_severity >= 50 else
            "monitor"
        )
        timeline.append({
            "weeks": weeks,
            "label": f"{weeks} week{'s' if weeks > 1 else ''}",
            "predicted_severity": round(future_severity, 1),
            "status": status,
            "description": (
                f"Severity reaches {future_severity:.0f}% — {'immediate repair needed' if status == 'critical' else 'schedule maintenance' if status == 'warning' else 'monitor periodically'}"
            ),
        })

    # Cost projection
    cost_now = detection.get("cost", {}).get("cost_estimated", 5000)
    cost_if_delayed = {
        "1_week": int(cost_now * 1.2),
        "2_weeks": int(cost_now * 1.5),
        "1_month": int(cost_now * 2.5),
        "3_months": int(cost_now * 5.0),
    }

    # Risk assessment
    if current_severity >= 70 or days_to_pothole < 14:
        urgency = "IMMEDIATE"
        urgency_color = "critical"
        action = "Deploy repair crew within 48 hours"
    elif current_severity >= 40 or days_to_pothole < 30:
        urgency = "HIGH"
        urgency_color = "warning"
        action = "Schedule repair within 2 weeks"
    elif current_severity >= 20:
        urgency = "MODERATE"
        urgency_color = "moderate"
        action = "Add to next maintenance cycle"
    else:
        urgency = "LOW"
        urgency_color = "low"
        action = "Monitor during routine inspections"

    return {
        "damage_type": damage_type,
        "current_severity": current_severity,
        "confidence": confidence,
        "prediction": {
            "days_to_pothole": round(days_to_pothole),
            "pothole_eta": f"{int(days_to_pothole)} days" if days_to_pothole > 0 else "Already a pothole",
            "growth_rate_mm_day": prog["growth_rate"] * weather_mult,
            "worsen_per_week": round(worsen_per_week, 1),
            "monsoon_active": is_monsoon,
            "weather_multiplier": weather_mult,
        },
        "timeline": timeline,
        "urgency": urgency,
        "urgency_color": urgency_color,
        "recommended_action": action,
        "risk_description": prog["risk"],
        "cost_projection": cost_now,
        "cost_if_delayed": cost_if_delayed,
    }


def predict_all_detections(detections: list) -> list:
    """Run predictions on all detections in a report."""
    return [predict_damage_progression(det) for det in detections]


def generate_area_forecast(reports: list) -> dict:
    """
    Generate area-wide prediction: which zones will worsen next.
    """
    now = datetime.now(timezone.utc)
    zone_risks = {}

    for r in reports:
        if r.get("status") == "fixed":
            continue

        loc = r.get("location", {}).get("name", "Unknown")
        if loc not in zone_risks:
            zone_risks[loc] = {"reports": 0, "total_severity": 0, "predictions": []}

        zone_risks[loc]["reports"] += 1
        avg_sev = r.get("stats", {}).get("avg_severity", 50)
        zone_risks[loc]["total_severity"] += avg_sev

        for det in r.get("detections", [])[:2]:
            pred = predict_damage_progression(det)
            zone_risks[loc]["predictions"].append(pred)

    # Score each zone
    forecasts = []
    for zone, data in zone_risks.items():
        avg_sev = data["total_severity"] / data["reports"] if data["reports"] > 0 else 0
        worst_eta = min((p["prediction"]["days_to_pothole"] for p in data["predictions"]), default=999)
        risk_score = min(100, avg_sev + (100 - worst_eta) * 0.3 + data["reports"] * 5)

        forecasts.append({
            "zone": zone,
            "risk_score": round(risk_score, 1),
            "active_issues": data["reports"],
            "avg_severity": round(avg_sev, 1),
            "earliest_failure_days": worst_eta,
            "forecast": (
                f"Critical failure expected in {worst_eta} days"
                if worst_eta < 14 else
                f"Deterioration likely within {worst_eta} days"
                if worst_eta < 60 else
                "Gradual degradation — monitor quarterly"
            ),
        })

    forecasts.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"zones": forecasts, "total_zones": len(forecasts)}
