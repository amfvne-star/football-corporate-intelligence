"""Shared formatting and normalization helpers used across all pages."""

from __future__ import annotations

import ast
import re

import pandas as pd

CANONICAL_CLUBS = {
    "benfica": "Benfica",
    "sport lisboa e benfica": "Benfica",
    "porto": "FC Porto",
    "fcporto": "FC Porto",
    "fc porto": "FC Porto",
    "futebol clube do porto": "FC Porto",
    "sporting": "Sporting",
    "sporting clube de portugal": "Sporting",
}

TRUE_VALUES = {"1", "true", "verdadeiro", "sim", "yes", "relevante", "relevant"}


def normalize_boolean(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin(TRUE_VALUES)


def _parts_of(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value]
    if not isinstance(value, str):
        if pd.isna(value):
            return []
        return [str(value)]

    text = value.strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple, set)):
            return [str(v) for v in parsed]
        return [str(parsed)]
    except (ValueError, SyntaxError):
        return re.split(r"[,;|/]", text)


def extract_clubs(value) -> list[str]:
    """Normalizes the 'clubes' column (any raw format) to canonical club names."""
    clubs = set()
    for part in _parts_of(value):
        name = part.lower().strip(" []'\"")
        for key, canonical in CANONICAL_CLUBS.items():
            if key in name:
                clubs.add(canonical)
                break
    return sorted(clubs)


def list_clubs(series: pd.Series) -> list[str]:
    clubs = set()
    for value in series.dropna():
        clubs.update(extract_clubs(value))
    return sorted(clubs)


def format_percentage(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.1%}"


def format_thousands(value: int) -> str:
    return f"{value:,}".replace(",", " ")
