"""
CRACKWATCH Advanced Analytics Engine.
Wall of Shame, Heatmap, Priority Engine, Before/After, Road Health Score.
"""

import math
import time
from datetime import datetime, timezone
from collections import defaultdict

# ── Mock contractor data (for hackathon demo) ──
CONTRACTORS = {
    "CTR-001": {"name": "Mumbai Road Corp", "area": "Thane", "city": "Mumbai"},
    "CTR-002": {"name": "Panvel Infrastructure Ltd", "area": "Raigad", "city": "Navi Mumbai"},
    "CTR-003": {"name": "Navi Mumbai PWD", "area": "NMMC Central", "city": "Navi Mumbai"},
    "CTR-004": {"name": "Kalamboli Builders", "area": "Kalamboli", "city": "Navi Mumbai"},
    "CTR-005": {"name": "Pune Smart Roads", "area": "Pune Central", "city": "Pune"},
    "CTR-006": {"name": "Pune Municipal Works", "area": "Pune East", "city": "Pune"},
    "CTR-007": {"name": "South Mumbai Roadworks", "area": "South Mumbai", "city": "Mumbai"},
    "CTR-008": {"name": "Western Suburbs Builders", "area": "Western Suburbs", "city": "Mumbai"},
    "CTR-009": {"name": "Eastern Suburbs Contractor", "area": "Eastern Suburbs", "city": "Mumbai"},
    "CTR-010": {"name": "CIDCO Infrastructure", "area": "CIDCO Zone", "city": "Navi Mumbai"},
}

# Location → contractor mapping (keyword-based, first match wins).
# Order matters — most specific first.
AREA_CONTRACTOR = {
    # South Mumbai
    "Marine Drive": "CTR-007",
    "Dadar": "CTR-007",
    "Sea Link": "CTR-007",
    "Worli": "CTR-007",
    "South Mumbai": "CTR-007",
    # Western Suburbs
    "Bandra": "CTR-008",
    "BKC": "CTR-008",
    "Andheri": "CTR-008",
    "Lokhandwala": "CTR-008",
    "Borivali": "CTR-008",
    "Juhu": "CTR-008",
    "Malad": "CTR-008",
    # Eastern Suburbs
    "Chembur": "CTR-009",
    "Ghatkopar": "CTR-009",
    "Powai": "CTR-009",
    "Mulund": "CTR-009",
    "Kanjurmarg": "CTR-009",
    # Navi Mumbai — NMMC central
    "Vashi": "CTR-003",
    "Nerul": "CTR-003",
    "Belapur": "CTR-003",
    "Seawoods": "CTR-003",
    "Airoli": "CTR-003",
    "Kopar Khairane": "CTR-003",
    "Navi Mumbai": "CTR-003",
    # CIDCO zones — Kharghar, Taloja, Uran
    "Kharghar": "CTR-010",
    "Taloja": "CTR-010",
    "Uran": "CTR-010",
    "Kamothe": "CTR-010",
    # Raigad / Panvel
    "Panvel": "CTR-002",
    "Kalamboli": "CTR-004",
    # Thane
    "Thane": "CTR-001",
    "Ghodbunder": "CTR-001",
    # Pune
    "Pune": "CTR-005",
}


def assign_contractor(location_name: str) -> dict:
    """Assign a contractor based on location."""
    for area, ctr_id in AREA_CONTRACTOR.items():
        if area.lower() in (location_name or "").lower():
            ctr = CONTRACTORS[ctr_id]
            return {"id": ctr_id, **ctr}
    # Default
    return {"id": "CTR-003", **CONTRACTORS["CTR-003"]}


def calculate_negligence_score(severity: float, hours_unresolved: float) -> float:
    """Negligence = severity × time unresolved (hours). Higher = worse."""
    return round(severity * max(1, hours_unresolved / 24), 1)  # Normalized to days


def generate_wall_of_shame(reports: list) -> dict:
    """
    Rank contractors by performance. Wall of Shame leaderboard.
    """
    contractor_stats = defaultdict(lambda: {
        "total_reports": 0, "fixed": 0, "unfixed": 0,
        "total_severity": 0, "total_negligence": 0,
        "avg_fix_time_hrs": 0, "fix_times": [],
    })

    now = datetime.now(timezone.utc)

    for r in reports:
        loc = r.get("location", {}).get("name", "") or r.get("location_name", "")
        ctr = assign_contractor(loc)
        ctr_id = ctr["id"]
        stats = contractor_stats[ctr_id]
        stats["contractor"] = ctr
        stats["total_reports"] += 1

        avg_sev = r.get("stats", {}).get("avg_severity", 50)
        stats["total_severity"] += avg_sev

        if r.get("status") == "fixed":
            stats["fixed"] += 1
            if r.get("fix_date"):
                submitted = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
                fixed_at = datetime.fromisoformat(r["fix_date"].replace("Z", "+00:00"))
                hrs = (fixed_at - submitted).total_seconds() / 3600
                stats["fix_times"].append(hrs)
        else:
            stats["unfixed"] += 1
            submitted = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            hrs_unresolved = (now - submitted).total_seconds() / 3600
            stats["total_negligence"] += calculate_negligence_score(avg_sev, hrs_unresolved)

    # Build leaderboard
    leaderboard = []
    for ctr_id, stats in contractor_stats.items():
        fix_rate = (stats["fixed"] / stats["total_reports"] * 100) if stats["total_reports"] > 0 else 0
        avg_fix_time = (sum(stats["fix_times"]) / len(stats["fix_times"])) if stats["fix_times"] else 0
        avg_severity = stats["total_severity"] / stats["total_reports"] if stats["total_reports"] > 0 else 0

        # Performance score: higher = better
        performance = fix_rate - (stats["total_negligence"] / max(1, stats["total_reports"]))
        performance = max(0, min(100, performance))

        leaderboard.append({
            "contractor_id": ctr_id,
            "contractor_name": stats["contractor"]["name"],
            "area": stats["contractor"]["area"],
            "city": stats["contractor"]["city"],
            "total_reports": stats["total_reports"],
            "fixed": stats["fixed"],
            "unfixed": stats["unfixed"],
            "fix_rate": round(fix_rate, 1),
            "avg_severity": round(avg_severity, 1),
            "avg_fix_time_hrs": round(avg_fix_time, 1),
            "negligence_score": round(stats["total_negligence"], 1),
            "performance_score": round(performance, 1),
            "rank": 0,
        })

    # Sort: worst performer first (lowest performance = rank 1 = most shameful)
    leaderboard.sort(key=lambda x: x["performance_score"])
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1

    return {
        "leaderboard": leaderboard,
        "total_contractors": len(leaderboard),
        "worst_performer": leaderboard[0] if leaderboard else None,
        "best_performer": leaderboard[-1] if leaderboard else None,
    }


def generate_heatmap_data(reports: list) -> list:
    """
    Generate heatmap points for damage visualization.
    Returns list of {lat, lng, intensity} for map rendering.
    """
    points = []
    for r in reports:
        loc = r.get("location", {})
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        if lat and lng:
            severity = r.get("stats", {}).get("avg_severity", 50)
            status = r.get("status", "submitted")
            # Fixed = low intensity, unfixed = high
            intensity = severity / 100 if status != "fixed" else 0.1
            points.append({
                "lat": lat, "lng": lng,
                "intensity": round(intensity, 2),
                "severity": severity,
                "status": status,
                "type": r.get("detections", [{}])[0].get("display_name", "Damage") if r.get("detections") else "Unknown",
            })
    return points


def generate_priority_queue(reports: list, traffic_multiplier: float = 1.0) -> list:
    """
    Maintenance Priority Engine.
    Priority = Severity × Traffic Density × Time Unresolved
    Returns top urgent repairs.
    """
    now = datetime.now(timezone.utc)
    priorities = []

    for r in reports:
        if r.get("status") == "fixed":
            continue

        avg_sev = r.get("stats", {}).get("avg_severity", 50)
        submitted = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
        hours_unresolved = (now - submitted).total_seconds() / 3600
        days_unresolved = hours_unresolved / 24

        # Priority formula
        time_factor = min(days_unresolved, 30) / 30  # Cap at 30 days
        upvotes = r.get("upvotes", 1)
        traffic_factor = min(upvotes / 10, 2.0) * traffic_multiplier  # More upvotes = more traffic
        priority_score = avg_sev * (1 + time_factor) * (1 + traffic_factor)

        loc = r.get("location", {})
        cost = 0
        repair_method = ""
        if r.get("detections"):
            det = r["detections"][0]
            if "cost" in det:
                cost = det["cost"].get("cost_estimated", 0)
                repair_method = det["cost"].get("repair_method", "")

        priorities.append({
            "report_id": r.get("id"),
            "location": loc.get("name", "Unknown"),
            "damage_type": r.get("detections", [{}])[0].get("display_name", "Damage") if r.get("detections") else "Unknown",
            "severity": avg_sev,
            "days_unresolved": round(days_unresolved, 1),
            "upvotes": upvotes,
            "priority_score": round(priority_score, 1),
            "estimated_cost": cost,
            "repair_method": repair_method,
            "status": r.get("status"),
        })

    priorities.sort(key=lambda x: x["priority_score"], reverse=True)
    for i, p in enumerate(priorities):
        p["rank"] = i + 1

    return priorities


def generate_city_health_scores(reports: list) -> list:
    """
    Road Health Score per city/area.
    Score = 100 - (damage_density × severity_factor × unresolved_factor)
    """
    city_data = defaultdict(lambda: {
        "total": 0, "fixed": 0, "unfixed": 0,
        "total_severity": 0, "total_fix_time": 0, "fix_count": 0,
    })

    now = datetime.now(timezone.utc)

    for r in reports:
        loc = r.get("location", {})
        # Determine city/area
        loc_name = loc.get("name", "") or ""
        city = "Navi Mumbai"  # default
        for c in ["Thane", "Panvel", "Kalamboli", "Kharghar", "Belapur", "Pune"]:
            if c.lower() in loc_name.lower():
                city = c
                break

        stats = city_data[city]
        stats["total"] += 1
        stats["total_severity"] += r.get("stats", {}).get("avg_severity", 50)

        if r.get("status") == "fixed":
            stats["fixed"] += 1
            if r.get("fix_date"):
                submitted = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
                fixed_at = datetime.fromisoformat(r["fix_date"].replace("Z", "+00:00"))
                stats["total_fix_time"] += (fixed_at - submitted).total_seconds() / 3600
                stats["fix_count"] += 1
        else:
            stats["unfixed"] += 1

    scores = []
    for city, stats in city_data.items():
        fix_rate = (stats["fixed"] / stats["total"]) if stats["total"] > 0 else 0
        avg_severity = stats["total_severity"] / stats["total"] if stats["total"] > 0 else 0
        avg_fix_time = stats["total_fix_time"] / stats["fix_count"] if stats["fix_count"] > 0 else 999

        # Health = 100 - penalties
        damage_penalty = min(30, stats["unfixed"] * 5)
        severity_penalty = min(30, avg_severity * 0.4)
        speed_penalty = min(20, avg_fix_time / 24 * 5)  # Slow fix = penalty
        fix_bonus = fix_rate * 20  # Good fix rate = bonus

        health = max(0, min(100, 100 - damage_penalty - severity_penalty - speed_penalty + fix_bonus))

        # Trend — simplified (for hackathon)
        trend = "improving" if fix_rate > 0.5 else "stable" if fix_rate > 0.2 else "worsening"

        scores.append({
            "city": city,
            "health_score": round(health, 1),
            "total_reports": stats["total"],
            "fixed": stats["fixed"],
            "unfixed": stats["unfixed"],
            "fix_rate": round(fix_rate * 100, 1),
            "avg_severity": round(avg_severity, 1),
            "avg_fix_time_hrs": round(avg_fix_time, 1) if stats["fix_count"] > 0 else None,
            "trend": trend,
        })

    scores.sort(key=lambda x: x["health_score"], reverse=True)
    for i, s in enumerate(scores):
        s["rank"] = i + 1

    return scores
