"""Installing: the skill is where `npx skills add` looks, the wheel carries the templates and docs, and `viz path`
finds them in a checkout and in an installed copy alike."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "viz" / "SKILL.md"


def test_skill_is_in_the_skills_cli_layout():
    front = SKILL.read_text().split("---")[1]
    assert re.search(r"^name: viz$", front, re.M) and re.search(r"^description: ", front, re.M)
    assert not (ROOT / "skill").exists() and not (ROOT / "install.sh").exists()


def test_skill_names_the_real_install_and_run_commands():
    text = SKILL.read_text()
    assert "uv tool install --force git+https://github.com/parallx-ai/plxviz" in text
    assert "command -v viz" not in text  # an upstream viz command must not skip installing the fork
    assert "viz run " in text and "viz/install.sh" not in text and "run `install.sh`" not in text
    reference = (ROOT / "docs" / "reference.md").read_text()
    assert "npx skills add parallx-ai/plxviz" in reference
    for doc in (text, reference):
        assert "https://github.com/safety-research/viz" not in doc
        assert 'uv add "viz @ git+https://github.com/parallx-ai/plxviz"' in doc


def test_viz_path_prints_this_checkout(capsys):
    from viz.cli import main
    assert main(["path"]) == 0
    assert Path(capsys.readouterr().out.strip()) == ROOT


def test_viz_path_falls_back_to_the_package(monkeypatch, tmp_path):
    from viz import cli
    pkg = tmp_path / "site-packages" / "viz"
    pkg.mkdir(parents=True)
    monkeypatch.setattr(cli, "__file__", str(pkg / "cli.py"))
    assert cli.checkout() is None and cli.home() == pkg


def test_viz_run_uses_this_python(tmp_path):
    script = tmp_path / "s.py"
    script.write_text("import sys, viz; print(sys.executable, *sys.argv[1:])\n")
    r = subprocess.run([sys.executable, "-m", "viz.cli", "run", str(script), "a", "--b"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == [sys.executable, "a", "--b"]


@pytest.fixture(scope="module")
def wheel(tmp_path_factory):
    out = tmp_path_factory.mktemp("wheel")
    subprocess.run(["uv", "build", "--quiet", "--wheel", "--out-dir", str(out), str(ROOT)], check=True)
    return next(out.glob("viz-*.whl"))


def test_wheel_ships_the_templates_and_docs(wheel):
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    for f in ["viz/examples/01_hbar.py", "viz/examples/README.md", "viz/docs/guide.md", "viz/docs/reference.md",
              "viz/docs/gallery/01_hbar.png", "viz/cli.py", "viz/fonts"]:
        assert any(n == f or n.startswith(f + "/") for n in names), f


def test_gallery_works_from_wheel(wheel, tmp_path):
    # Run the packaged code away from the checkout, using this environment's rendering dependencies.
    installed = tmp_path / "site-packages"
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(installed)
    env = os.environ | {"PYTHONPATH": str(installed)}
    home = subprocess.run([sys.executable, "-m", "viz.cli", "path"], cwd=tmp_path, env=env,
                          capture_output=True, text=True, check=True)
    assert Path(home.stdout.strip()) == installed / "viz"
    result = subprocess.run([sys.executable, "-m", "viz.cli", "gallery", "-o", "gallery",
                             "--examples", "examples.md"], cwd=tmp_path, env=env,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    from viz.gallery import STEM
    for stem in STEM.values():
        for folder in (tmp_path / "gallery", tmp_path / "gallery" / "cards"):
            assert (folder / f"{stem}.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert (tmp_path / "examples.md").read_text() == (ROOT / "examples" / "README.md").read_text()
