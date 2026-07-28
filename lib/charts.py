"""Shared chart color roles.

Colors come from the validated 8-hue categorical palette (fixed order:
blue, orange, aqua, yellow, magenta, green, violet, red — passes CVD
adjacency + contrast checks at OKLab ΔE ≥ 8, normal-vision ΔE ≥ 15).

Club colors are pinned globally so the same club always wears the same
color across every chart in the app (Dashboard, Research questions).
Other categorical fields (event sub-type, news source) draw from the
remaining slots without needing a manual per-value mapping — reused
across unrelated charts is fine since they never appear color-adjacent
to a club series in the same figure.
"""

PALETTE_BLUE = "#2a78d6"
PALETTE_ORANGE = "#eb6834"
PALETTE_AQUA = "#1baf7a"
PALETTE_YELLOW = "#eda100"
PALETTE_MAGENTA = "#e87ba4"
PALETTE_GREEN = "#008300"
PALETTE_VIOLET = "#4a3aa7"
PALETTE_RED = "#e34948"

CLUB_COLORS = {
    "Benfica": PALETTE_RED,
    "FC Porto": PALETTE_BLUE,
    "Sporting": PALETTE_GREEN,
}
CLUB_ORDER = ["Benfica", "FC Porto", "Sporting"]
CLUB_COLOR_SEQUENCE = [CLUB_COLORS[c] for c in CLUB_ORDER]

# Club crests, hotlinked from Wikipedia/Wikimedia Commons for identification
# purposes in this non-commercial academic prototype. The Benfica and FC
# Porto files are marked "non-free" on Wikipedia (fair use, scoped to
# Wikipedia articles) — reused here on the user's explicit instruction.
# See app_pages/methodology.py for the attribution note.
CLUB_LOGOS = {
    "Benfica": "https://upload.wikimedia.org/wikipedia/en/a/a2/SL_Benfica_logo.svg",
    "FC Porto": "https://upload.wikimedia.org/wikipedia/en/f/f1/FC_Porto.svg",
    "Sporting": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Sporting_Clube_de_Portugal_2026.svg",
}

# Porto Business School logo — public domain on Wikimedia Commons (below the
# threshold of originality), safe to hotlink.
PBS_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/4/48/Porto_Business_School_logo_2017.png"

# Single flat hue for one-series magnitude/ranking bars (no identity to encode).
SINGLE_SERIES_COLOR = PALETTE_BLUE

# For categorical fields other than club (event sub-type, source), in fixed order.
SECONDARY_SEQUENCE = [PALETTE_ORANGE, PALETTE_AQUA, PALETTE_VIOLET, PALETTE_MAGENTA, PALETTE_YELLOW]

MUTED = "#898781"  # chart chrome: axis/labels/annotation bands

MAX_CATEGORIES = 6  # fold the long tail into "Other" beyond this


def fold_long_tail(series, max_categories: int = MAX_CATEGORIES, other_label: str = "Other"):
    """Keeps the top `max_categories` values of a Series, sums the rest into one bucket."""
    import pandas as pd

    if len(series) <= max_categories:
        return series
    top = series.iloc[:max_categories]
    rest = series.iloc[max_categories:].sum()
    return pd.concat([top, pd.Series({other_label: rest})])


def add_period_annotations(fig, covid_label: str):
    """Shades the COVID-19 period on a year-indexed time chart (data covers 2019-2025)."""
    fig.add_vrect(
        x0=2020, x1=2021.6, fillcolor=MUTED, opacity=0.12, line_width=0,
        annotation_text=covid_label, annotation_position="top left",
        annotation_font_size=11, annotation_font_color=MUTED,
    )
    fig.update_xaxes(dtick=1, tickformat="d")
    return fig
