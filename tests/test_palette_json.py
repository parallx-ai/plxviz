"""The palette as data (viz.web): docs/palette.json stays current, and it is the light theme whatever is in effect."""
from __future__ import annotations

import json
from pathlib import Path

import viz as vl
from viz import theme as th
from viz import web
from viz.cli import main

COPY = Path(__file__).resolve().parents[1] / "docs" / "palette.json"


def test_the_committed_copy_is_current():
    assert json.loads(COPY.read_text()) == web.palette(), (
        "docs/palette.json is out of date: run `viz colors --json > docs/palette.json`")


def test_the_cli_prints_the_same_data(capsys):
    assert main(["colors", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == web.palette()


def test_it_is_the_light_theme_even_while_drawing_dark():
    light = web.palette()
    try:
        vl.set_defaults(theme="dark")
        assert th.THEME == "dark"
        assert web.palette() == light
        assert th.THEME == "dark"  # and the theme in effect is left alone
    finally:
        vl.set_defaults(theme="light")


def test_roles_and_series_name_colors_in_the_palette():
    p = web.palette()
    for name in (*p["roles"].values(), *p["series"], *p["muted"], *p["ordered"], *p["outcomes"].values()):
        assert name in p["colors"], name
    assert p["colors"][p["roles"]["intervention"]] == "#A37F1F"


def test_reference_values_match_the_formulas():
    ref = web.palette()["reference"]
    assert ref["tone"]["gold"][-1] == [1.0, th.tone("gold", 1.0)]
    assert ref["ramp"]["3"] == th.ramp(3)
    assert ref["text-on"]["navy"] == th.text_on(th.PALETTE["navy"])
