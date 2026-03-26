"""
Energy-aware recommendation service.

Combines energy score, mood, purpose, time-of-day, day-of-week and purchase
history to recommend the most fitting flavour from the catalogue.
"""

from __future__ import annotations

import datetime
import logging
from typing import Optional

from backend.models.sabor import listar_sabores
from backend.models.energy import save_recommendation

logger = logging.getLogger(__name__)

# ── Flavour affinity maps ────────────────────────────────────────────────────

_MOOD_FLAVOUR: dict[str, list[str]] = {
    "feliz":      ["Morango", "Pistache", "Limão"],
    "triste":     ["Chocolate", "Baunilha"],
    "cansado":    ["Limão", "Morango", "Chocolate"],
    "motivado":   ["Pistache", "Morango", "Limão"],
    "apaixonado": ["Chocolate", "Morango", "Pistache"],
    "estressado": ["Baunilha", "Chocolate"],
    "confuso":    [],
    "confiante":  ["Pistache", "Limão"],
}

_PURPOSE_FLAVOUR: dict[str, list[str]] = {
    "malhar":    ["Limão", "Morango"],
    "preguiça":  ["Chocolate", "Baunilha"],
    "estudar":   ["Limão", "Pistache"],
    "festa":     ["Morango", "Pistache"],
    "romântico": ["Chocolate", "Morango"],
    "recuperar": ["Baunilha", "Morango"],
}

_ENERGY_BAND_FLAVOUR: dict[str, list[str]] = {
    "very_high":  ["Pistache", "Limão", "Morango"],   # 90–100
    "high":       ["Morango", "Pistache", "Limão"],   # 70–89
    "medium":     ["Baunilha", "Morango", "Chocolate"],  # 50–69
    "low":        ["Chocolate", "Baunilha"],           # 30–49
    "very_low":   ["Limão", "Morango"],               # 0–29
}

_TIME_FLAVOUR: dict[str, list[str]] = {
    "manha_cedo":    ["Limão", "Morango"],    # 06–09
    "manha":         ["Pistache", "Limão"],   # 09–12
    "almoco":        ["Baunilha", "Chocolate"],  # 12–14
    "tarde":         ["Chocolate", "Baunilha"],  # 14–17
    "fim_tarde":     ["Morango", "Limão"],    # 17–19
    "noite_cedo":    ["Pistache", "Morango"], # 19–21
    "noite":         ["Chocolate", "Morango"],  # 21–23
    "madrugada":     ["Chocolate", "Baunilha"],  # 23–06
}


def _energy_band(score: int) -> str:
    if score >= 90:
        return "very_high"
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "low"
    return "very_low"


def _time_slot(hour: int) -> str:
    if 6 <= hour < 9:
        return "manha_cedo"
    if 9 <= hour < 12:
        return "manha"
    if 12 <= hour < 14:
        return "almoco"
    if 14 <= hour < 17:
        return "tarde"
    if 17 <= hour < 19:
        return "fim_tarde"
    if 19 <= hour < 21:
        return "noite_cedo"
    if 21 <= hour < 24:
        return "noite"
    return "madrugada"


def recommend(
    session_id: str,
    energy_score: int,
    mood: Optional[str] = None,
    purpose: Optional[str] = None,
    hour: Optional[int] = None,
) -> dict:
    """
    Return the best-matching flavour dict and save a recommendation record.
    Falls back to the first available flavour if no match is found.
    """
    sabores = listar_sabores()
    if not sabores:
        return {"flavor": None, "confidence": 0.0, "reason": "Nenhum sabor cadastrado."}

    catalogue = {s["nome"].lower(): s for s in sabores}
    score_map: dict[str, int] = {name: 0 for name in catalogue}

    if hour is None:
        hour = datetime.datetime.now().hour

    # Energy band votes
    band = _energy_band(energy_score)
    for f in _ENERGY_BAND_FLAVOUR.get(band, []):
        key = f.lower()
        if key in score_map:
            score_map[key] += 3

    # Mood votes
    if mood:
        mood_key = mood.lower().strip()
        # Exact match first, then check if mood_key starts with a known mood
        matched_flavours = _MOOD_FLAVOUR.get(mood_key)
        if matched_flavours is None:
            for candidate_mood, flavours in _MOOD_FLAVOUR.items():
                if mood_key.startswith(candidate_mood):
                    matched_flavours = flavours
                    break
        if matched_flavours:
            for f in matched_flavours:
                key = f.lower()
                if key in score_map:
                    score_map[key] += 2

    # Purpose votes
    if purpose:
        purpose_lower = purpose.lower().strip()
        for kw, flavours in _PURPOSE_FLAVOUR.items():
            if kw in purpose_lower:
                for f in flavours:
                    key = f.lower()
                    if key in score_map:
                        score_map[key] += 2
                break

    # Time-of-day votes
    slot = _time_slot(hour)
    for f in _TIME_FLAVOUR.get(slot, []):
        key = f.lower()
        if key in score_map:
            score_map[key] += 1

    best_key = max(score_map, key=lambda k: score_map[k])
    best_sabor = catalogue[best_key]
    total_votes = sum(score_map.values()) or 1
    confidence = round(score_map[best_key] / total_votes, 2)

    reasoning = {
        "energy_band": band,
        "mood": mood,
        "purpose": purpose,
        "time_slot": slot,
        "scores": score_map,
    }

    try:
        save_recommendation(
            session_id, energy_score,
            best_sabor["nome"], confidence, reasoning,
        )
    except Exception as exc:
        logger.warning("Could not persist recommendation: %s", exc)

    copy_map = {
        "very_high": "VAI SER ÉPICO! 🔥",
        "high":      "Descubra algo novo! 🚀",
        "medium":    "Perfeito para você ⚖️",
        "low":       "Seu refúgio 🧘",
        "very_low":  "ACORDA! ⚡ Energia instantânea",
    }

    return {
        "flavor": best_sabor["nome"],
        "price": float(best_sabor["preco"]),
        "confidence": confidence,
        "copy": copy_map.get(band, "Recomendado para você"),
        "energy_band": band,
        "reason": reasoning,
    }
