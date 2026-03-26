"""
Energy-First Product Design — database helpers.

Handles user_energy_profile, energy_events and energy_recommendations tables.
"""

from backend.database import get_db


# ── Session profile ──────────────────────────────────────────────────────────

def upsert_profile(session_id: str, data: dict):
    """Create or update the energy profile for a session."""
    fields = {
        "baseline_energy": data.get("energy_score"),
        "preferred_interaction": data.get("preferred_interaction"),
        "decision_speed_ms": data.get("decision_speed_ms"),
        "exploration_rate": data.get("exploration_rate"),
        "peak_energy_hour": data.get("peak_energy_hour"),
        "energy_curve": data.get("energy_curve"),
        "favorite_mood": data.get("mood"),
        "introvert_score": data.get("introvert_score"),
        "sharer_score": data.get("sharer_score"),
    }
    # Remove None values so we only update supplied fields
    fields = {k: v for k, v in fields.items() if v is not None}

    if not fields:
        return get_profile(session_id)

    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values())

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO user_energy_profile (session_id, {", ".join(fields)})
                VALUES (%s, {", ".join(["%s"] * len(fields))})
                ON CONFLICT (session_id)
                DO UPDATE SET {set_clause}, updated_at = NOW()
                RETURNING *
                """,
                [session_id] + values + values,
            )
            return cur.fetchone()


def get_profile(session_id: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM user_energy_profile WHERE session_id = %s",
                (session_id,),
            )
            return cur.fetchone()


# ── Energy events ────────────────────────────────────────────────────────────

def record_event(session_id: str, data: dict):
    """Persist a single energy snapshot event."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO energy_events (
                    session_id, energy_score, mood, purpose, stress_level,
                    location_context, time_of_day, day_of_week, battery_level,
                    device_motion, click_speed_ms, scroll_pattern,
                    typing_speed_cpm, flavor_recommended
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                ) RETURNING *
                """,
                (
                    session_id,
                    data.get("energy_score"),
                    data.get("mood"),
                    data.get("purpose"),
                    data.get("stress_level"),
                    data.get("location_context"),
                    data.get("time_of_day"),
                    data.get("day_of_week"),
                    data.get("battery_level"),
                    data.get("device_motion"),
                    data.get("click_speed_ms"),
                    data.get("scroll_pattern"),
                    data.get("typing_speed_cpm"),
                    data.get("flavor_recommended"),
                ),
            )
            return cur.fetchone()


def get_events(session_id: str, limit: int = 50):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM energy_events
                WHERE session_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (session_id, limit),
            )
            return cur.fetchall()


# ── Recommendations ──────────────────────────────────────────────────────────

def save_recommendation(session_id: str, energy_score: int, flavor: str,
                        confidence: float, reasoning: dict):
    with get_db() as conn:
        with conn.cursor() as cur:
            import json
            cur.execute(
                """
                INSERT INTO energy_recommendations
                    (session_id, energy_score, recommended_flavor, confidence_score, reasoning)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (session_id, energy_score, flavor, confidence, json.dumps(reasoning)),
            )
            return cur.fetchone()


def mark_recommendation_purchased(rec_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE energy_recommendations SET purchased = TRUE WHERE id = %s RETURNING *",
                (rec_id,),
            )
            return cur.fetchone()
