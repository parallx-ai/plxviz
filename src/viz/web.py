"""The palette as data, for drawing in the same colors outside viz.

Parallax's article template (github.com/parallx-ai/blog-template) reads it for its interactive figures, so a chart
drawn with viz and one drawn in the browser give each condition the same color, and their heatmaps and shaded tokens
the same scales. `viz colors --json` prints it; docs/palette.json holds a copy, which tests/test_palette_json.py
keeps current.

Everything is the light theme, whichever theme is in effect. "reference" holds values computed here (scale tones,
ordered ramps, text on fills), so a port of the formulas can check that it draws the same colors.
"""
from __future__ import annotations

from . import theme as th
from .colors import ALIASES, ROLES

TONE_STEPS = (0.0, 0.25, 0.5, 0.75, 1.0)
RAMP_SIZES = (2, 3, 5)


def palette() -> dict:
    """The light theme's colors, color roles, color scales, fonts and text sizes, as plain data (JSON-ready)."""
    previous = th.THEME
    th.use_theme("light")
    try:
        return {
            "source": "plxviz",
            "theme": "light",
            "surfaces": {"background": th.BG, "card": th.CARD, "card-light": th.CARD_LIGHT, "episode": th.EP_CARD,
                         "code": th.CODE_BG, "surface": th.SURFACE},
            "ink": {"ink": th.INK, "ink2": th.INK2, "muted": th.MUTED, "faint": th.FAINT, "grid": th.GRID,
                    "axis": th.AXIS, "rule": th.RULE},
            "colors": dict(th.PALETTE),
            "tints": dict(th.TINT),
            "roles": dict(ROLES),
            "aliases": dict(ALIASES),
            "series": list(th.SERIES),
            "muted": list(th.MUTED_SHADES),
            "ordered": list(th.RAMP),
            "outcomes": dict(th.OUTCOMES),
            "strong": dict(th.STRONG),
            "scale": {
                "lightness": list(th.SCALE_L),
                "start": th.SCALE_START,
                "hues": {name: {"light": h0, "deep": h1, "chroma": c} for name, (h0, h1, c) in th.SCALES.items()},
                "diverging": {"low": "coral", "high": "blue"},
            },
            "fonts": dict(th.FAMILIES),
            "text": {"title": th.TITLE_SIZE, "subtitle": th.SUBTITLE_SIZE, "legend": th.LEGEND_SIZE,
                     "tick": th.TICK_SIZE, "min": th.MIN_TEXT},
            "reference": {
                "tone": {name: [[t, th.tone(name, t)] for t in TONE_STEPS] for name in (*th.SCALES, "plum")},
                "ramp": {str(n): th.ramp(n) for n in RAMP_SIZES},
                "text-on": {name: th.text_on(th.PALETTE[name]) for name in (*th.SERIES, "gray", "navy")},
            },
        }
    finally:
        th.use_theme(previous)
