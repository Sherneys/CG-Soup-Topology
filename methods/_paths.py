# methods/_paths.py
# Path bootstrap shared by Phase-2 scripts.
#
# Two quirks this hides (both verified in this checkout):
#   * `import topology` fails here because the package directory is named
#     `CG-Soup-Topology`, not `topology`. We register it under the name
#     `topology` via an importlib spec-load so `topology/` is reused UNCHANGED.
#   * `import diffsoup` / `from utils import ...` need the diffsoup examples dir
#     on sys.path (mirrors src/diffsoup_train.py). DIFFSOUP_ROOT defaults to the
#     known location when the env var is unset.

from __future__ import annotations

import importlib.util
import os
import sys

# CG-Soup-Topology/ (the topology package dir, parent of methods/)
TOPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIFFSOUP_ROOT = os.environ.get("DIFFSOUP_ROOT", r"D:\Project\diffsoup")


def load_topology():
    """Import the Phase-1 `topology` package by path (folder name != 'topology')."""
    if "topology" in sys.modules:
        return sys.modules["topology"]
    init = os.path.join(TOPO_DIR, "__init__.py")
    spec = importlib.util.spec_from_file_location(
        "topology", init, submodule_search_locations=[TOPO_DIR])
    mod = importlib.util.module_from_spec(spec)
    sys.modules["topology"] = mod
    spec.loader.exec_module(mod)
    return mod


def add_diffsoup_path():
    """Put diffsoup's examples dir on sys.path (for `import diffsoup`, `from utils`)."""
    p = os.path.join(DIFFSOUP_ROOT, "examples")
    if p not in sys.path:
        sys.path.insert(0, p)
    return p
