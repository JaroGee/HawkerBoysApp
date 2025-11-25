import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("streamlit")

PAGE_FILES = [
    "app.py",
    "pages/1_Home.py",
    "pages/2_Missions.py",
    "pages/3_Progress.py",
    "pages/4_Support.py",
    "pages/9_Admin.py",
]


@pytest.mark.parametrize("relative_path", PAGE_FILES)
def test_pages_load(relative_path):
    base = Path(__file__).resolve().parent.parent
    target = base / relative_path
    spec = importlib.util.spec_from_file_location(target.stem.replace(".", "_"), target)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
