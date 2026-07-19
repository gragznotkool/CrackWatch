"""
CRACKWATCH Gamification Engine.
Leaderboards, achievements, challenges, civic coins, streaks, community verification.
"""

from datetime import datetime, timezone, timedelta
from collections import defaultdict
import random

# ── User profiles store ──
user_profiles: dict[str, dict] = {}

# ── Achievement definitions ──
ACHIEVEMENTS = {
    "first_report": {"name": "🕵️ First Report", "desc": "Submit your first damage report", "xp": 50, "coins": 10},
    "five_reports": {"name": "📸 Scout", "desc": "Submit 5 reports", "xp": 100, "coins": 25},
    "ten_reports": {"name": "🔥 Road Warrior", "desc": "Submit 10 reports", "xp": 250, "coins": 50},
    "twenty_five_reports": {"name": "🛠️ Civic Hero", "desc": "Submit 25 reports", "xp": 500, "coins": 100},
    "fifty_reports": {"name": "🌍 City Saver", "desc": "Submit 50 reports", "xp": 1000, "coins": 250},
    "fast_reporter": {"name": "⚡ Fast Reporter", "desc": "Submit 3 reports in 1 hour", "xp": 150, "coins": 30},
    "streak_3": {"name": "🔥 3-Day Streak", "desc": "Report 3 days in a row", "xp": 100, "coins": 20},
    "streak_7": {"name": "🔥🔥 Week Warrior", "desc": "Report 7 days in a row", "xp": 300, "coins": 75},
    "streak_30": {"name": "🔥🔥🔥 Legend", "desc": "Report 30 days in a row", "xp": 1000, "coins": 300},
    "verifier": {"name": "✅ Verifier", "desc": "Verify 5 community reports", "xp": 100, "coins": 20},
    "critical_finder": {"name": "🚨 Critical Finder", "desc": "Report a critical severity damage", "xp": 200, "coins": 40},
    "multi_sector": {"name": "🔍 Inspector", "desc": "Report in 3 different sectors", "xp": 150, "coins": 30},
    "ai_challenger": {"name": "🤖 AI Master", "desc": "Score 80%+ in AI Challenge Mode", "xp": 200, "coins": 50},
}

# ── Challenge definitions ──
DAILY_CHALLENGES = [
    {"id": "daily_5", "name": "Report 5 potholes today", "target": 5, "type": "reports", "xp": 100, "coins": 20},
    {"id": "daily_3loc", "name": "Scan 3 different locations", "target": 3, "type": "locations", "xp": 75, "coins": 15},
    {"id": "daily_worst", "name": "Find a critical severity road", "target": 1, "type": "critical", "xp": 150, "coins": 30},
    {"id": "daily_verify", "name": "Verify 3 community reports", "target": 3, "type": "verifications", "xp": 75, "coins": 15},
    {"id": "daily_streak", "name": "Maintain your reporting streak", "target": 1, "type": "streak", "xp": 50, "coins": 10},
]

WEEKLY_CHALLENGES = [
    {"id": "weekly_20", "name": "Report 20 issues this week", "target": 20, "type": "reports", "xp": 500, "coins": 100},
    {"id": "weekly_sectors", "name": "Report in all 4 sectors", "target": 4, "type": "sectors", "xp": 300, "coins": 75},
    {"id": "weekly_impact", "name": "Get 50 total upvotes", "target": 50, "type": "upvotes", "xp": 400, "coins": 80},
]

# ── Point values ──
POINT_VALUES = {
    "valid_pothole": 10,
    "valid_crack": 7,
    "valid_minor": 5,
    "valid_critical": 15,
    "false_report": -5,
    "upvote_received": 2,
    "verification": 3,
    "streak_bonus": 5,  # per day
    "ai_challenge_correct": 10,
    "ai_challenge_wrong": -2,
}

# ── Community verification store ──
verification_votes: dict[str, list] = {}  # report_id → [{voter, vote, timestamp}]


def get_or_create_profile(user_id: str, name: str = "Citizen") -> dict:
    """Get or create a user gamification profile."""
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            "user_id": user_id,
            "name": name,
            "xp": 0,
            "coins": 50,  # Starting bonus
            "level": 1,
            "total_reports": 0,
            "total_points": 0,
            "streak_days": 0,
            "last_report_date": None,
            "achievements": [],
            "sectors_reported": set(),
            "reports_today": 0,
            "reports_this_hour": [],
            "verifications": 0,
            "upvotes_received": 0,
            "ai_challenge_score": 0,
            "ai_challenges_played": 0,
            "joined": datetime.now(timezone.utc).isoformat(),
        }
    return user_profiles[user_id]


def calculate_level(xp: int) -> int:
    """Level = sqrt(xp / 100). Level 1 = 0xp, Level 10 = 10000xp."""
    import math
    return max(1, int(math.sqrt(xp / 100)) + 1)


def award_points(user_id: str, report: dict, detections: list) -> dict:
    """Award points, XP, coins for a valid report. Check achievements."""
    profile = get_or_create_profile(user_id)
    now = datetime.now(timezone.utc)
    points_earned = 0
    coins_earned = 0
    xp_earned = 0
    new_achievements = []

    # Calculate points based on detections
    has_critical = False
    for det in detections:
        sev = det.get("severity_label", "minor")
        if sev == "critical":
            points_earned += POINT_VALUES["valid_critical"]
            has_critical = True
        elif sev == "warning":
            points_earned += POINT_VALUES["valid_pothole"]
        else:
            points_earned += POINT_VALUES["valid_minor"]

    if not detections:
        points_earned += POINT_VALUES["false_report"]

    xp_earned = max(0, points_earned * 5)
    coins_earned = max(0, points_earned // 2)

    # Update profile
    profile["total_reports"] += 1
    profile["total_points"] += points_earned
    profile["xp"] += xp_earned
    profile["coins"] += coins_earned
    profile["reports_today"] += 1
    profile["reports_this_hour"].append(now.timestamp())

    # Sector tracking
    sector = report.get("sector", "road")
    if isinstance(profile["sectors_reported"], set):
        profile["sectors_reported"].add(sector)

    # ── Streak calculation ──
    today = now.date().isoformat()
    if profile["last_report_date"] != today:
        if profile["last_report_date"]:
            yesterday = (now - timedelta(days=1)).date().isoformat()
            if profile["last_report_date"] == yesterday:
                profile["streak_days"] += 1
                xp_earned += POINT_VALUES["streak_bonus"] * profile["streak_days"]
            else:
                profile["streak_days"] = 1
        else:
            profile["streak_days"] = 1
        profile["last_report_date"] = today

    # ── Check achievements ──
    count = profile["total_reports"]
    earned = set(profile["achievements"])

    checks = [
        (count >= 1, "first_report"),
        (count >= 5, "five_reports"),
        (count >= 10, "ten_reports"),
        (count >= 25, "twenty_five_reports"),
        (count >= 50, "fifty_reports"),
        (has_critical, "critical_finder"),
        (profile["streak_days"] >= 3, "streak_3"),
        (profile["streak_days"] >= 7, "streak_7"),
        (profile["streak_days"] >= 30, "streak_30"),
        (profile["verifications"] >= 5, "verifier"),
        (len(profile.get("sectors_reported", set())) >= 3, "multi_sector"),
    ]

    # Fast reporter: 3 reports in 1 hour
    recent = [t for t in profile["reports_this_hour"] if t > now.timestamp() - 3600]
    profile["reports_this_hour"] = recent
    if len(recent) >= 3:
        checks.append((True, "fast_reporter"))

    for condition, ach_id in checks:
        if condition and ach_id not in earned:
            profile["achievements"].append(ach_id)
            ach = ACHIEVEMENTS[ach_id]
            profile["xp"] += ach["xp"]
            profile["coins"] += ach["coins"]
            new_achievements.append(ach)

    profile["level"] = calculate_level(profile["xp"])

    return {
        "points_earned": points_earned,
        "xp_earned": xp_earned,
        "coins_earned": coins_earned,
        "new_achievements": new_achievements,
        "streak_days": profile["streak_days"],
        "level": profile["level"],
        "total_xp": profile["xp"],
        "total_coins": profile["coins"],
    }


def get_leaderboard(top_n: int = 20) -> list:
    """Get top players by XP."""
    profiles = list(user_profiles.values())
    profiles.sort(key=lambda p: p["xp"], reverse=True)

    board = []
    for i, p in enumerate(profiles[:top_n]):
        board.append({
            "rank": i + 1,
            "name": p["name"],
            "xp": p["xp"],
            "level": calculate_level(p["xp"]),
            "coins": p["coins"],
            "total_reports": p["total_reports"],
            "streak_days": p["streak_days"],
            "achievements_count": len(p["achievements"]),
            "top_achievement": ACHIEVEMENTS[p["achievements"][-1]]["name"] if p["achievements"] else None,
        })
    return board


def get_user_profile_full(user_id: str) -> dict:
    """Get full profile with achievements list."""
    profile = get_or_create_profile(user_id)
    return {
        **{k: v for k, v in profile.items() if k != "reports_this_hour" and k != "sectors_reported"},
        "sectors_reported": list(profile.get("sectors_reported", set())),
        "level": calculate_level(profile["xp"]),
        "xp_to_next_level": ((calculate_level(profile["xp"])) ** 2) * 100,
        "achievements_detail": [ACHIEVEMENTS[a] for a in profile["achievements"] if a in ACHIEVEMENTS],
    }


def get_daily_challenges(user_id: str) -> list:
    """Get today's challenges with progress."""
    profile = get_or_create_profile(user_id)
    today_idx = datetime.now(timezone.utc).timetuple().tm_yday % len(DAILY_CHALLENGES)
    challenges = DAILY_CHALLENGES[today_idx:today_idx+3] if today_idx + 3 <= len(DAILY_CHALLENGES) else DAILY_CHALLENGES[today_idx:] + DAILY_CHALLENGES[:3-(len(DAILY_CHALLENGES)-today_idx)]

    result = []
    for c in challenges:
        progress = 0
        if c["type"] == "reports":
            progress = min(profile["reports_today"], c["target"])
        elif c["type"] == "streak":
            progress = min(1 if profile["streak_days"] > 0 else 0, 1)
        elif c["type"] == "critical":
            progress = min(1, 1)  # Simplified
        elif c["type"] == "verifications":
            progress = min(profile["verifications"], c["target"])

        result.append({
            **c,
            "progress": progress,
            "completed": progress >= c["target"],
        })
    return result


def community_vote(report_id: str, voter_id: str, vote: str) -> dict:
    """Community verification vote on a report."""
    if report_id not in verification_votes:
        verification_votes[report_id] = []

    # Check if already voted
    for v in verification_votes[report_id]:
        if v["voter"] == voter_id:
            return {"error": "Already voted on this report"}

    verification_votes[report_id].append({
        "voter": voter_id,
        "vote": vote,  # "valid" or "invalid"
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # Award verifier points
    profile = get_or_create_profile(voter_id)
    profile["verifications"] += 1
    profile["xp"] += POINT_VALUES["verification"] * 5
    profile["coins"] += POINT_VALUES["verification"]

    votes = verification_votes[report_id]
    valid = sum(1 for v in votes if v["vote"] == "valid")
    invalid = sum(1 for v in votes if v["vote"] == "invalid")

    return {
        "report_id": report_id,
        "valid_votes": valid,
        "invalid_votes": invalid,
        "total_votes": len(votes),
        "consensus": "valid" if valid > invalid else "invalid" if invalid > valid else "undecided",
        "voter_reward": {"xp": POINT_VALUES["verification"] * 5, "coins": POINT_VALUES["verification"]},
    }


def ai_challenge_round() -> dict:
    """Generate an AI Challenge Mode round."""
    # Random damage scenarios
    scenarios = [
        {"image_desc": "Cracked road surface with interconnected pattern", "answer": "Alligator Crack", "severity": "critical"},
        {"image_desc": "Small round hole in road surface", "answer": "Pothole", "severity": "warning"},
        {"image_desc": "Long straight crack along the road", "answer": "Longitudinal Crack", "severity": "moderate"},
        {"image_desc": "Crack running across the road width", "answer": "Transverse Crack", "severity": "moderate"},
        {"image_desc": "Smooth road with no visible damage", "answer": "Safe", "severity": "none"},
        {"image_desc": "Concrete surface flaking and peeling", "answer": "Surface Spalling", "severity": "warning"},
        {"image_desc": "Orange/brown staining on metal bridge surface", "answer": "Corrosion", "severity": "moderate"},
        {"image_desc": "Water pooling through road crack", "answer": "Water Leak", "severity": "warning"},
    ]

    round_data = random.choice(scenarios)
    options = ["Pothole", "Alligator Crack", "Longitudinal Crack", "Transverse Crack", "Safe", "Surface Spalling", "Corrosion", "Water Leak"]
    # Ensure answer is in options and pick 3 wrong ones
    wrong = [o for o in options if o != round_data["answer"]]
    random.shuffle(wrong)
    choices = [round_data["answer"]] + wrong[:3]
    random.shuffle(choices)

    return {
        "scenario": round_data["image_desc"],
        "correct_answer": round_data["answer"],
        "severity": round_data["severity"],
        "options": choices,
    }


def check_ai_challenge(user_id: str, answer: str, correct: str) -> dict:
    """Check AI challenge answer and award points."""
    profile = get_or_create_profile(user_id)
    is_correct = answer == correct

    if is_correct:
        profile["xp"] += POINT_VALUES["ai_challenge_correct"] * 5
        profile["coins"] += POINT_VALUES["ai_challenge_correct"]
        profile["ai_challenge_score"] += 1
    else:
        profile["xp"] += POINT_VALUES["ai_challenge_wrong"] * 5
        profile["coins"] = max(0, profile["coins"] + POINT_VALUES["ai_challenge_wrong"])

    profile["ai_challenges_played"] += 1
    accuracy = (profile["ai_challenge_score"] / profile["ai_challenges_played"] * 100) if profile["ai_challenges_played"] > 0 else 0

    # Check AI Master achievement
    if accuracy >= 80 and profile["ai_challenges_played"] >= 5 and "ai_challenger" not in profile["achievements"]:
        profile["achievements"].append("ai_challenger")

    return {
        "correct": is_correct,
        "correct_answer": correct,
        "points": POINT_VALUES["ai_challenge_correct"] if is_correct else POINT_VALUES["ai_challenge_wrong"],
        "accuracy": round(accuracy, 1),
        "total_played": profile["ai_challenges_played"],
    }


def get_authority_fix_streaks(reports: list) -> list:
    """Fix Streak system for authorities."""
    # Group by area/contractor
    area_streaks = defaultdict(lambda: {"consecutive_fixes": 0, "last_fix": None, "total_fixed": 0, "pending": 0})

    for r in reports:
        loc = r.get("location", {}).get("name", "Unknown")
        area = loc.split(",")[0].strip() if "," in loc else loc

        if r.get("status") == "fixed":
            area_streaks[area]["total_fixed"] += 1
            area_streaks[area]["consecutive_fixes"] += 1
            area_streaks[area]["last_fix"] = r.get("fix_date")
        elif r.get("status") in ("submitted", "acknowledged"):
            area_streaks[area]["pending"] += 1
            area_streaks[area]["consecutive_fixes"] = 0

    streaks = []
    for area, data in area_streaks.items():
        streaks.append({
            "area": area,
            "streak": data["consecutive_fixes"],
            "total_fixed": data["total_fixed"],
            "pending": data["pending"],
            "status": "🔥 On fire!" if data["consecutive_fixes"] >= 5 else "✅ Good" if data["consecutive_fixes"] >= 2 else "⚠️ Needs attention",
        })

    streaks.sort(key=lambda x: x["streak"], reverse=True)
    return streaks
