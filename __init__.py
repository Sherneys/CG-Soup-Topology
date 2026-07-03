# topology/ — Phase-1 topology MEASUREMENT harness for DiffSoup.
#
# Measurement only: persistence diagrams (alpha complex), a Topology Stability
# Metric, and deterministic synthetic shapes for the topology-blindness demo.
# No differentiable persistent homology and no resampling method live here —
# those are Phase 2. This package is a leaf (numpy/scipy/gudhi + optional
# trimesh/torch adapters) so the Phase-2 method can reuse it unchanged.

from .persistence import (
    PersistenceResult,
    persistence_from_points,
    persistence_from_target,
    persistence_from_reconstruction,
)
from . import meshes
from . import metrics

__all__ = [
    "PersistenceResult",
    "persistence_from_points",
    "persistence_from_target",
    "persistence_from_reconstruction",
    "meshes",
    "metrics",
]
