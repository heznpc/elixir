"""
Path-anchored import of experiments/src/screening.py::classify_paper.

Previously each dedup.py did:

    sys.path.insert(0, str(EXP_DIR / "src"))
    from screening import classify_paper

That relies on no other `screening` module being importable on the python
path; the import resolves to the FIRST one found in sys.path order, which
depends on the current working directory and any pre-existing entries.

This helper uses importlib.util.spec_from_file_location to import the
specific file directly, with no sys.path mutation, so the binding is
unambiguous regardless of cwd.
"""

from __future__ import annotations

import importlib.util
import pathlib
from typing import Callable


def get_classify_paper() -> Callable:
    here = pathlib.Path(__file__).resolve().parent
    screening_path = here.parent / "src" / "screening.py"
    if not screening_path.is_file():
        raise ImportError(f"screening.py not found at {screening_path}")
    spec = importlib.util.spec_from_file_location(
        "_elixir_screening", str(screening_path)
    )
    if spec is None or spec.loader is None:
        raise ImportError("could not build module spec for screening.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "classify_paper"):
        raise ImportError("screening.py does not expose classify_paper")
    return module.classify_paper
