# tests/test_betti.py
# Verification gate #1: the alpha-complex persistence pipeline must recover the
# textbook Betti numbers of known closed surfaces (counting significant features,
# i.e. the persistence-based reading of homology):
#
#     sphere     -> b0=1, b1=0, b2=1
#     torus      -> b0=1, b1=2, b2=1
#     2 spheres  -> b0=2
#
# Runs under pytest, OR standalone:  .venv\Scripts\python.exe tests\test_betti.py
# Fully deterministic: every sample is driven by an explicit seed.

from __future__ import annotations

import os
import sys

import numpy as np

# This checkout's package dir is named "CG-Soup-Topology", not "topology", so a
# plain `import topology` fails. Register it under the name `topology` via the
# shared shim (methods/_paths.load_topology) — the same mechanism methods/ uses.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root (for methods/)
from methods._paths import load_topology
load_topology()

from topology import meshes
from topology.persistence import (
    persistence_from_points,
    persistence_from_reconstruction,
    persistence_from_target,
)

SEED = 0


def _betti(P):
    return persistence_from_points(P).betti_numbers()


def test_sphere_betti():
    P = meshes.sphere_cloud(12_000, radius=0.5, rng=np.random.default_rng(SEED))
    assert _betti(P) == (1, 0, 1), _betti(P)


def test_torus_betti():
    P = meshes.torus_cloud(16_000, R=1.0, r=0.3, rng=np.random.default_rng(SEED + 1))
    assert _betti(P) == (1, 2, 1), _betti(P)


def test_two_spheres_b0():
    P = meshes.two_spheres_cloud(12_000, radius=0.35, gap=0.5,
                                 rng=np.random.default_rng(SEED + 2))
    b = _betti(P)
    assert b[0] == 2, b                              # the requested gate: b0 = 2
    assert b == (2, 0, 2), b                         # and each shell keeps its void


def test_determinism():
    """Same seed -> identical cloud -> identical diagram (bit-for-bit)."""
    a = meshes.sphere_cloud(8_000, rng=np.random.default_rng(7))
    b = meshes.sphere_cloud(8_000, rng=np.random.default_rng(7))
    assert np.array_equal(a, b)
    da = persistence_from_points(a).diagram(2)
    db = persistence_from_points(b).diagram(2)
    assert np.array_equal(da, db)


def test_betti_stable_across_threshold():
    """The reading must not hinge on a knife-edge threshold: any k in [4,8] gives
    the same Betti numbers for the (high-SNR) synthetic shapes."""
    P = meshes.torus_cloud(16_000, R=1.0, r=0.3, rng=np.random.default_rng(3))
    res = persistence_from_points(P)
    for k in (4, 5, 6, 7, 8):
        assert res.betti_numbers(k=k) == (1, 2, 1), (k, res.betti_numbers(k=k))


def test_entry_points_agree_and_target_api_frozen():
    """persistence_from_target (the future-guidance path, UNUSED by Phase-1
    metrics) and persistence_from_reconstruction must be defined and correct.
    Exercised here only to freeze the API — not wired into the demo/metric."""
    sphere = lambda n, rng: meshes.sphere_cloud(n, radius=0.5, rng=rng)
    rt = persistence_from_target(sphere, n_samples=12_000, seed=SEED)
    rr = persistence_from_reconstruction(sphere, n_samples=12_000, seed=SEED)
    assert rt.betti_numbers() == (1, 0, 1), rt.betti_numbers()
    assert rr.betti_numbers() == (1, 0, 1), rr.betti_numbers()


def test_double_torus_betti():
    """Genus-2 surface (dimensional-crossover primary): 4 independent loops, one void."""
    P = meshes.double_torus_cloud(24_000, rng=np.random.default_rng(SEED + 3))
    assert _betti(P) == (1, 4, 1), _betti(P)


def test_three_spheres_b0():
    P = meshes.three_spheres_cloud(15_000, rng=np.random.default_rng(SEED + 4))
    b = _betti(P)
    assert b[0] == 3, b                              # H0 gate: three components
    assert b == (3, 0, 3), b


def test_thick_shell_betti():
    """A thick (solid-wall) shell encloses exactly one cavity: b0=1, b1=0, b2=1."""
    P = meshes.thick_shell_cloud(22_000, rng=np.random.default_rng(SEED + 5))
    assert _betti(P) == (1, 0, 1), _betti(P)


def _main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
