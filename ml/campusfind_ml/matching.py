"""Transparent lost/found matching.

Score = weighted sum of per-attribute similarities (TF-IDF cosine for free text, exact match for
categorical fields, linear decay for date proximity). It is a *match score* (0-100), not a
probability.
"""

from dataclasses import dataclass
from datetime import date

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

WEIGHTS = {
    "title": 0.20,
    "description": 0.25,
    "category": 0.15,
    "brand": 0.10,
    "color": 0.10,
    "location": 0.10,
    "date": 0.10,
}
DATE_WINDOW_DAYS = 14
MIN_SCORE = 50


@dataclass(frozen=True)
class ItemFeatures:
    id: int
    title: str
    description: str | None
    category: str
    brand: str | None
    color: str | None
    location: str
    date: date


@dataclass(frozen=True)
class MatchResult:
    item_id: int
    score: int
    attributes: list[str]
    explanation: str


def _norm(v: str | None) -> str:
    return (v or "").strip().lower()


def _same(a: str | None, b: str | None) -> bool:
    return bool(_norm(a)) and _norm(a) == _norm(b)


def _text_similarities(query: str | None, candidates: list[str | None]) -> list[float]:
    docs = [_norm(query)] + [_norm(c) for c in candidates]
    if not docs[0] or not any(docs[1:]):
        return [0.0] * len(candidates)
    try:
        matrix = TfidfVectorizer(stop_words="english").fit_transform(docs)
    except ValueError:  # empty vocabulary (e.g. only stop words)
        return [0.0] * len(candidates)
    return [float(x) for x in cosine_similarity(matrix[0], matrix[1:])[0]]


def find_matches(
    query: ItemFeatures, candidates: list[ItemFeatures], limit: int = 10
) -> list[MatchResult]:
    if not candidates:
        return []
    title_sims = _text_similarities(query.title, [c.title for c in candidates])
    desc_sims = _text_similarities(query.description, [c.description for c in candidates])

    results: list[MatchResult] = []
    for cand, t_sim, d_sim in zip(candidates, title_sims, desc_sims):
        days = abs((query.date - cand.date).days)
        parts = {
            "title": t_sim,
            "description": d_sim,
            "category": 1.0 if _same(query.category, cand.category) else 0.0,
            "brand": 1.0 if _same(query.brand, cand.brand) else 0.0,
            "color": 1.0 if _same(query.color, cand.color) else 0.0,
            "location": 1.0 if _same(query.location, cand.location) else 0.0,
            "date": max(0.0, 1 - days / DATE_WINDOW_DAYS),
        }
        score = round(100 * sum(WEIGHTS[k] * v for k, v in parts.items()))
        if score < MIN_SCORE:
            continue

        attrs = []
        if parts["category"]:
            attrs.append("same category")
        if parts["brand"]:
            attrs.append("same brand")
        if parts["color"]:
            attrs.append("same color")
        if t_sim >= 0.5:
            attrs.append("similar title")
        if d_sim >= 0.3:
            attrs.append("similar description")
        if parts["location"]:
            attrs.append("same location")
        if days <= 3:
            attrs.append("close dates")
        results.append(
            MatchResult(cand.id, score, attrs, _explain(query, cand, parts, days))
        )
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]


def _explain(q: ItemFeatures, c: ItemFeatures, parts: dict, days: int) -> str:
    if parts["title"] >= 0.5:
        subject = f"a {_norm(c.title)}"
    else:
        quals = ", ".join(x for x in (q.color if parts["color"] else None, q.brand if parts["brand"] else None) if x)
        subject = f"{quals + ' ' if quals else ''}items in the {q.category} category"
    text = f"Both reports describe {subject}"
    if parts["location"]:
        text += f" reported near the {q.location}"
    if days <= 3:
        text += f", within {days} day{'s' if days != 1 else ''} of each other" if days else ", on the same day"
    return text + "."
