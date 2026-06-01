"""Exact, variant, and fuzzy matching logic for APP-004."""
from difflib import SequenceMatcher
import pandas as pd
from .mapping_model import ColumnMapping, MatchResult


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match_value(
    value: str,
    master_list: list,
    variant_map: dict,
    threshold: float = 0.72,
) -> MatchResult:
    """Classify a single value: exact / variant / fuzzy / unmatched."""
    v = str(value).strip()
    v_lower = v.lower()

    if not v or v_lower in ("nan", "none", "n/a", ""):
        return MatchResult(input_value=v, canonical_value="", match_type="blank",
                           confidence=0.0, status="blank")

    # 1. Exact match (case-insensitive)
    for item in master_list:
        if v_lower == item.lower():
            return MatchResult(input_value=v, canonical_value=item,
                               match_type="exact", confidence=1.0, status="exact")

    # 2. Known variant
    if v_lower in variant_map:
        canonical = variant_map[v_lower]
        if canonical:  # some variants are None (ambiguous)
            return MatchResult(input_value=v, canonical_value=canonical,
                               match_type="variant", confidence=0.95, status="variant")

    # 3. Fuzzy match
    scored = sorted(
        [(item, _ratio(v, item)) for item in master_list],
        key=lambda x: x[1], reverse=True,
    )
    top_item, top_score = scored[0] if scored else ("", 0.0)
    suggestions = [s[0] for s in scored[:4] if s[1] > threshold * 0.7]

    if top_score >= threshold:
        return MatchResult(
            input_value=v, canonical_value=top_item,
            match_type="fuzzy", confidence=round(top_score, 3),
            suggestions=suggestions, status="pending",
        )

    # 4. No match
    return MatchResult(
        input_value=v, canonical_value=top_item,
        match_type="unmatched", confidence=round(top_score, 3),
        suggestions=[s[0] for s in scored[:3]],
        status="unmatched",
    )


def run_matching(
    series: pd.Series, cm: ColumnMapping
) -> dict:
    """
    Match all unique values in series against cm.master_list.
    Returns {input_value_str: MatchResult}.
    """
    unique_vals = series.dropna().astype(str).str.strip().unique()
    results = {}
    for v in unique_vals:
        if v.lower() in ("nan", "none", "n/a", ""):
            continue
        results[v] = match_value(v, cm.master_list, cm.variant_map, cm.fuzzy_threshold)
    return results


def summarize_matches(results: dict) -> dict:
    """Return count breakdown by match type."""
    counts = {"exact": 0, "variant": 0, "pending": 0, "unmatched": 0,
              "approved": 0, "rejected": 0, "manual": 0, "blank": 0}
    for r in results.values():
        counts[r.status] = counts.get(r.status, 0) + 1
    return counts
