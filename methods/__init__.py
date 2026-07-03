# methods/ — Phase-2 topology-aware adaptive resampling for DiffSoup.
#
# Two leaf modules, kept separate so the training loop imports only what it needs:
#   topo_importance.py  — OFFLINE: build a deterministic spatial topological
#                         importance field from a target (needs gudhi/topology).
#   topo_resampling.py  — IN-LOOP: a budget-neutral resampling policy that biases
#                         DiffSoup's existing prune/respawn by a precomputed field
#                         (needs only torch + diffsoup; NO gudhi at train time).
#
# Phase-2 scope: topology is a precomputed sampling bias only. No differentiable
# persistent homology, no gradient through persistence (that is Phase 3).
