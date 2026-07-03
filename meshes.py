# topology/meshes.py
# Deterministic synthetic surface point clouds for Phase-1 topology measurement.
#
# All shapes are emitted as SURFACE SAMPLES (N,3) — not watertight meshes. The
# topology pipeline (topology/persistence.py) feeds point clouds to an alpha
# complex, so composite shapes (a sphere with a handle, two blobs joined by a
# bridge) are built by sampling each analytic part and concatenating. This needs
# no mesh-boolean backend (blender/manifold/openscad), which keeps the whole
# thing dependency-light and bit-for-bit deterministic.
#
# Determinism contract (the user relies on synthetic GT to kill confounds — the
# same rigor applies here):
#   * Every sampler takes a numpy Generator (np.random.default_rng(seed)).
#   * Analytic part geometry is closed-form; only (a) a small surface jitter and
#     (b) area-proportional point allocation draw from the rng.
#   * Same seed -> identical cloud, exactly.
#
# Sampling is area-uniform (Fibonacci lattice for spheres, density-correct
# rejection for tori) so geometric metrics (Chamfer/Hausdorff) computed on these
# clouds are consistent with src/eval_geometry.py conventions.
#
# A small isotropic jitter (default 0.2 x local point spacing) is added to every
# analytic sample. It is far smaller than any feature, so it never changes
# topology, but it perturbs the otherwise perfectly co-spherical / co-circular
# lattices off their degenerate Delaunay configuration — alpha complexes are
# then numerically stable. The jitter is seeded, hence reproducible.

from __future__ import annotations

from typing import Optional

import numpy as np


# ── small helpers ────────────────────────────────────────────────────

def _rng(rng) -> np.random.Generator:
    if rng is None:
        return np.random.default_rng(0)
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)


def _jitter(P: np.ndarray, rng: np.random.Generator, area: float) -> np.ndarray:
    """Isotropic Gaussian jitter at 0.2 x local spacing (spacing = sqrt(area/N))."""
    n = len(P)
    if n == 0:
        return P
    spacing = float(np.sqrt(max(area, 1e-12) / n))
    return P + rng.normal(0.0, 0.2 * spacing, size=P.shape)


def _frames(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-row orthonormal (U,V) spanning the plane perpendicular to unit T."""
    a = np.tile(np.array([1.0, 0.0, 0.0]), (len(T), 1))
    a[np.abs(T[:, 0]) > 0.9] = np.array([0.0, 1.0, 0.0])
    U = np.cross(T, a)
    U /= np.linalg.norm(U, axis=1, keepdims=True) + 1e-12
    V = np.cross(T, U)
    return U, V


# ── primitive surface samples ────────────────────────────────────────

def fibonacci_sphere(n: int, radius: float, center, rng) -> np.ndarray:
    """Near-uniform sphere-surface sample via the golden-angle (Fibonacci)
    lattice. The lattice itself is deterministic; only the stabilizing jitter
    uses the rng."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    i = np.arange(n) + 0.5
    cos_phi = 1.0 - 2.0 * i / n                      # z, uniform in [-1,1]
    phi = np.arccos(np.clip(cos_phi, -1.0, 1.0))
    theta = np.pi * (1.0 + 5.0 ** 0.5) * i           # golden-angle azimuth
    dirs = np.stack([np.sin(phi) * np.cos(theta),
                     np.sin(phi) * np.sin(theta),
                     np.cos(phi)], axis=1)
    P = center + radius * dirs
    return _jitter(P, rng, area=4.0 * np.pi * radius ** 2)


def cap_mask(P: np.ndarray, center, axis, half_angle: float) -> np.ndarray:
    """Boolean mask of points within `half_angle` of the +axis pole (a polar cap)."""
    center = np.asarray(center, dtype=float)
    axis = np.asarray(axis, dtype=float)
    axis = axis / (np.linalg.norm(axis) + 1e-12)
    d = P - center
    cos = (d @ axis) / (np.linalg.norm(d, axis=1) + 1e-12)
    return cos >= np.cos(half_angle)


def torus_points(n: int, R: float, r: float, center, rng) -> np.ndarray:
    """Area-uniform torus surface sample. theta ~ U[0,2pi); phi drawn by
    rejection with density proportional to (R + r cos phi) (the surface
    Jacobian), so points are uniform on the torus, not in parameter space."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    theta = rng.uniform(0.0, 2.0 * np.pi, n)
    phi = np.empty(n)
    filled = 0
    while filled < n:
        m = n - filled
        cand = rng.uniform(0.0, 2.0 * np.pi, m)
        keep = rng.uniform(0.0, 1.0, m) < (R + r * np.cos(cand)) / (R + r)
        k = int(keep.sum())
        phi[filled:filled + k] = cand[keep]
        filled += k
    rho = R + r * np.cos(phi)
    P = np.stack([rho * np.cos(theta), rho * np.sin(theta), r * np.sin(phi)], axis=1)
    return _jitter(P + center, rng, area=4.0 * np.pi ** 2 * R * r)


def bezier_tube_points(n: int, A, C, B, tube_r: float, rng) -> np.ndarray:
    """Tube of radius `tube_r` around a quadratic Bezier centerline A->C->B.
    Used for handles and bridges; the centerline shape is irrelevant to
    topology, only that the tube connects its endpoints."""
    rng = _rng(rng)
    A, C, B = (np.asarray(x, dtype=float) for x in (A, C, B))
    s = rng.uniform(0.0, 1.0, n)
    one = 1.0 - s
    c = (one[:, None] ** 2) * A + 2.0 * (one * s)[:, None] * C + (s[:, None] ** 2) * B
    T = 2.0 * one[:, None] * (C - A) + 2.0 * s[:, None] * (B - C)   # d/ds
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    U, V = _frames(T)
    ang = rng.uniform(0.0, 2.0 * np.pi, n)
    P = c + tube_r * (np.cos(ang)[:, None] * U + np.sin(ang)[:, None] * V)
    L = float(np.linalg.norm(C - A) + np.linalg.norm(B - C))         # polyline len
    return _jitter(P, rng, area=2.0 * np.pi * tube_r * L)


# ── composite clouds (the Phase-1 cases) ─────────────────────────────
#
# Each builder allocates its total point budget across parts in proportion to
# surface area, so point spacing is uniform across the whole shape — fair for
# both the alpha complex and for Chamfer/Hausdorff.

def _alloc(n: int, areas) -> list[int]:
    areas = np.asarray(areas, dtype=float)
    w = areas / areas.sum()
    counts = np.floor(n * w).astype(int)
    counts[-1] = n - counts[:-1].sum()              # exact total
    return counts.tolist()


def sphere_cloud(n: int, radius: float = 0.5, center=(0.0, 0.0, 0.0),
                 rng=None) -> np.ndarray:
    """A closed sphere shell.  Topology: b0=1, b1=0, b2=1."""
    return fibonacci_sphere(n, radius, center, _rng(rng))


def ellipsoid_cloud(n: int, radii=(0.5, 0.35, 0.35), center=(0.0, 0.0, 0.0),
                    rng=None) -> np.ndarray:
    """A closed ellipsoid shell (single component).  b0=1, b1=0, b2=1."""
    rng = _rng(rng)
    P = fibonacci_sphere(n, 1.0, (0.0, 0.0, 0.0), rng)
    return P * np.asarray(radii, dtype=float) + np.asarray(center, dtype=float)


def sphere_with_hole_cloud(n: int, radius: float = 0.5, center=(0.0, 0.0, 0.0),
                           hole_half_angle: float = 0.45, axis=(0.0, 0.0, 1.0),
                           rng=None) -> np.ndarray:
    """A sphere shell with a polar cap removed — an open surface.  The enclosed
    void leaks through the hole, so the H2 (b2=1) feature of the closed sphere
    collapses: b2 -> 0.  Geometrically it differs from the sphere only over the
    small removed cap."""
    rng = _rng(rng)
    # oversample so that, after deleting the cap, ~n points remain at the same
    # density as a full sphere (fair spacing vs the closed-sphere comparand).
    frac = (1.0 + np.cos(hole_half_angle)) / 2.0     # fraction NOT in the cap
    P = fibonacci_sphere(int(round(n / max(frac, 1e-3))), radius, center, rng)
    keep = ~cap_mask(P, center, axis, hole_half_angle)
    return P[keep]


def _hoop_centerline(s, A, B, height):
    """Half-ellipse from A (s=0) to B (s=1) bulging by `height` along +z, with
    its analytic tangent. A standing 'croquet hoop': its opening is a clear,
    persistent 1-cycle (unlike a low arch that hugs the body and pinches shut)."""
    M = 0.5 * (A + B)
    w = A - M                                        # horizontal half-axis
    h = np.array([0.0, 0.0, height])                 # vertical half-axis
    cs, sn = np.cos(np.pi * s)[:, None], np.sin(np.pi * s)[:, None]
    c = M + cs * w + sn * h
    T = -np.sin(np.pi * s)[:, None] * w + np.cos(np.pi * s)[:, None] * h
    norm = np.linalg.norm(T, axis=1, keepdims=True)
    # a flat hoop (height->0) has zero tangent at the feet; fall back to the
    # chord direction there so frames stay finite (no NaNs into the alpha complex)
    bad = norm[:, 0] < 1e-9
    if bad.any():
        T[bad] = (w / (np.linalg.norm(w) + 1e-12))
        norm[bad] = 1.0
    T = T / norm
    return c, T


def sphere_with_handle_cloud(n: int, radius: float = 0.5, center=(0.0, 0.0, 0.0),
                             attach_angle: float = 0.4, height: float = 0.30,
                             tube_r: float = 0.03, rng=None) -> np.ndarray:
    """A sphere with a thin standing handle ('croquet hoop') on top.  Adding one
    handle raises the genus to 1, so b1 jumps 0 -> >=1 (the hoop opening clears
    the significance threshold).  The hoop is thin, so it perturbs
    Chamfer/Hausdorff only slightly."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    sa, ca = np.sin(attach_angle), np.cos(attach_angle)
    A = center + radius * np.array([sa, 0.0, ca])    # two close feet near +z
    B = center + radius * np.array([-sa, 0.0, ca])
    ss = np.linspace(0.0, 1.0, 60)
    cs, _ = _hoop_centerline(ss, A, B, height)
    L = float(np.linalg.norm(np.diff(cs, axis=0), axis=1).sum())
    sphere_area = 4.0 * np.pi * radius ** 2
    handle_area = 2.0 * np.pi * tube_r * L
    n_s, n_h = _alloc(n, [sphere_area, handle_area])
    Ps = fibonacci_sphere(n_s, radius, center, rng)
    s = rng.uniform(0.0, 1.0, n_h)
    c, T = _hoop_centerline(s, A, B, height)
    U, V = _frames(T)
    ang = rng.uniform(0.0, 2.0 * np.pi, n_h)
    Ph = c + tube_r * (np.cos(ang)[:, None] * U + np.sin(ang)[:, None] * V)
    Ph = _jitter(Ph, rng, area=handle_area)
    return np.concatenate([Ps, Ph], axis=0)


def bumped_sphere_cloud(n: int, radius: float = 0.5, center=(0.0, 0.0, 0.0),
                        cap_half_angle: float = 0.5, height: float = 0.0,
                        axis=(0.0, 0.0, 1.0), rng=None) -> np.ndarray:
    """A sphere whose polar cap is smoothly displaced radially by `height`
    (>0 = an outward blister, <0 = an inward dent), with a cosine profile that
    tapers to 0 at the cap edge so the surface stays closed and smooth.

    Topology is UNCHANGED (b0=1, b1=0, b2=1): a blister adds no handle, a dent
    keeps the enclosed void.  This is the topology-CORRECT comparand whose
    geometric damage (Chamfer/Hausdorff) is matched to a topology-BREAKING
    handle (blister vs hoop) or hole (dent vs puncture)."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    axis = np.asarray(axis, dtype=float)
    axis = axis / (np.linalg.norm(axis) + 1e-12)
    P = fibonacci_sphere(n, radius, center, rng)
    d = P - center
    dirs = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-12)
    ang = np.arccos(np.clip(dirs @ axis, -1.0, 1.0))
    in_cap = ang < cap_half_angle
    profile = np.zeros(len(P))
    profile[in_cap] = 0.5 * (1.0 + np.cos(np.pi * ang[in_cap] / cap_half_angle))
    new_r = radius + height * profile
    return center + new_r[:, None] * dirs


def two_spheres_cloud(n: int, radius: float = 0.35, gap: float = 0.5,
                      center=(0.0, 0.0, 0.0), rng=None) -> np.ndarray:
    """Two disjoint sphere shells separated by `gap` (centre-to-centre minus
    diameters).  Two components: b0=2, b2=2, b1=0."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    off = radius + gap / 2.0                       # each centre is `off` from origin
    c1 = center + np.array([off, 0.0, 0.0])
    c2 = center - np.array([off, 0.0, 0.0])
    n1 = n // 2
    P1 = fibonacci_sphere(n1, radius, c1, rng)
    P2 = fibonacci_sphere(n - n1, radius, c2, rng)
    return np.concatenate([P1, P2], axis=0)


def bridged_spheres_cloud(n: int, radius: float = 0.35, gap: float = 0.5,
                          tube_r: float = 0.045, center=(0.0, 0.0, 0.0),
                          break_gap: float = 0.0, rng=None) -> np.ndarray:
    """Two spheres with a thin straight tube between them.

    break_gap=0  : a complete bridge -> ONE component (b0=1), a spurious merge.
    break_gap>0  : the same tube with a hairline middle segment (width
                   `break_gap`, as a fraction of the tube length) removed, so it
                   is two stubs that do NOT touch -> TWO components (b0=2).

    The connected and broken variants differ only by that hairline segment, so
    their Chamfer/Hausdorff to the two-sphere ground truth are nearly identical
    — yet their component count differs.  This is the matched comparand pair for
    the H0 case: geometry cannot tell them apart, topology can."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    off = radius + gap / 2.0
    c1 = center + np.array([off, 0.0, 0.0])
    c2 = center - np.array([off, 0.0, 0.0])
    # endpoints sit just inside each sphere's inner pole so a complete tube
    # genuinely overlaps both shells and connects them.
    A = c1 - np.array([radius * 0.9, 0.0, 0.0])
    B = c2 + np.array([radius * 0.9, 0.0, 0.0])
    sphere_area = 4.0 * np.pi * radius ** 2
    L = float(np.linalg.norm(B - A))
    bridge_area = 2.0 * np.pi * tube_r * L
    n_two, n_b = _alloc(n, [2.0 * sphere_area, bridge_area])
    n1 = n_two // 2
    P1 = fibonacci_sphere(n1, radius, c1, rng)
    P2 = fibonacci_sphere(n_two - n1, radius, c2, rng)
    Pb = bezier_tube_points(n_b, A, center, B, tube_r, rng)
    if break_gap > 0.0:
        # drop the middle segment along the bridge axis (x) -> two stubs
        t = (Pb[:, 0] - B[0]) / (A[0] - B[0])        # 0 at B .. 1 at A
        keep = np.abs(t - 0.5) > (break_gap / 2.0)
        Pb = Pb[keep]
    return np.concatenate([P1, P2, Pb], axis=0)


def torus_cloud(n: int, R: float = 1.0, r: float = 0.3, center=(0.0, 0.0, 0.0),
                rng=None) -> np.ndarray:
    """A torus shell.  Topology: b0=1, b1=2, b2=1."""
    return torus_points(n, R, r, center, _rng(rng))


# ── dimensional-crossover targets (multi-feature, higher-count) ───────
#   These stress LOW-dimensional features at higher counts (and an H2 boundary
#   case) so concentrate-vs-spread resampling priors can be compared per feature
#   dimension. Betti numbers are validated by tests/test_betti.py.

def double_torus_mesh(R: float = 1.0, r: float = 0.30, sep: float = 1.0,
                      grid_h: float = 0.025, margin: float = 0.18):
    """Watertight GENUS-2 surface as a (V,F) mesh.  Topology: b0=1, b1=4, b2=1.

    Boundary of the UNION of two solid tori offset by +-`sep` along x (each in
    the xy-plane, hole along z), extracted with marching cubes from the union SDF
    min(sdf_A, sdf_B). Genus 2 is robust for sep in ~[0.9, 1.15]: the two donut
    holes stay distinct while the inner tubes fuse. DETERMINISTIC (fixed SDF grid;
    no rng). Needs scikit-image (lazy import) so the analytic-cloud shapes above
    stay dependency-light.

    PRIMARY multi-loop-H1 target for the dimensional crossover: its 4 significant
    H1 loops let us test whether a CONCENTRATING resample prior inflates phantom
    handles where a SPREADING one does not."""
    from skimage import measure                        # lazy: only this shape needs it

    def _torus_sdf(P, cx):
        q = np.sqrt((P[..., 0] - cx) ** 2 + P[..., 1] ** 2) - R
        return np.sqrt(q ** 2 + P[..., 2] ** 2) - r

    xmax, ymax, zmax = sep + R + r + margin, R + r + margin, r + margin
    xs = np.arange(-xmax, xmax + grid_h, grid_h)
    ys = np.arange(-ymax, ymax + grid_h, grid_h)
    zs = np.arange(-zmax, zmax + grid_h, grid_h)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    P = np.stack([X, Y, Z], axis=-1)
    vol = np.minimum(_torus_sdf(P, -sep), _torus_sdf(P, sep))
    V, F, _, _ = measure.marching_cubes(vol, level=0.0, spacing=(grid_h, grid_h, grid_h))
    V = V + np.array([xs[0], ys[0], zs[0]])
    return np.ascontiguousarray(V, dtype=float), np.ascontiguousarray(F, dtype=np.int64)


def double_torus_cloud(n: int, R: float = 1.0, r: float = 0.30, sep: float = 1.0,
                       center=(0.0, 0.0, 0.0), rng=None, **mesh_kw) -> np.ndarray:
    """Area-uniform surface sample of the genus-2 double torus.  b0=1, b1=4, b2=1."""
    rng = _rng(rng)
    V, F = double_torus_mesh(R=R, r=r, sep=sep, **mesh_kw)
    return sample_surface(V, F, n, rng) + np.asarray(center, dtype=float)


def three_spheres_cloud(n: int, radius: float = 0.30, gap: float = 0.30,
                        center=(0.0, 0.0, 0.0), rng=None) -> np.ndarray:
    """Three disjoint sphere shells in a row along x.  b0=3, b1=0, b2=3.
    H0 generalization of two_spheres (three components / two gaps)."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    step = 2.0 * radius + gap                          # centre-to-centre
    centers = [center + np.array([k * step, 0.0, 0.0]) for k in (-1, 0, 1)]
    counts = _alloc(n, [1.0, 1.0, 1.0])
    parts = [fibonacci_sphere(c_n, radius, c, rng) for c_n, c in zip(counts, centers)]
    return np.concatenate(parts, axis=0)


def thick_shell_cloud(n: int, r_inner: float = 0.40, r_outer: float = 0.70,
                      center=(0.0, 0.0, 0.0), rng=None) -> np.ndarray:
    """A spherical shell WITH WALL THICKNESS, sampled as a SOLID (the wall volume
    r_inner <= |x| <= r_outer).  As a filled 3-D annulus its alpha complex has one
    enclosed cavity: b0=1, b1=0, b2=1.  (Sampling only the two boundary spheres
    would instead read b0=2, b2=2 — the void here is the thick wall's cavity.)
    H2 boundary check: the void's death scale is set by the wall, not a thin shell."""
    rng = _rng(rng)
    center = np.asarray(center, dtype=float)
    pts = np.empty((0, 3))
    while len(pts) < n:
        m = 3 * (n - len(pts)) + 64
        cand = rng.uniform(-r_outer, r_outer, size=(m, 3))
        rad = np.linalg.norm(cand, axis=1)
        pts = np.concatenate([pts, cand[(rad >= r_inner) & (rad <= r_outer)]], axis=0)
    return pts[:n] + center


def scaled(P: np.ndarray, factor: float, center=None) -> np.ndarray:
    """Uniformly scale a cloud about `center` (default: its own centroid).
    Used to build the topology-CORRECT-but-geometrically-perturbed comparands:
    scaling preserves topology exactly while moving every point by ~factor-1."""
    P = np.asarray(P, dtype=float)
    c = P.mean(axis=0) if center is None else np.asarray(center, dtype=float)
    return c + (P - c) * factor


# ── generic samplers for real meshes / DiffSoup checkpoints ──────────
#   Forward-compat: persistence_from_reconstruction() can take a trained soup
#   checkpoint or an arbitrary mesh. Both reuse the area-weighted barycentric
#   scheme from src/eval_geometry.py (kept self-contained so topology/ stays a
#   leaf module the Phase-2 method can import without pulling in the renderer).

def sample_surface(V: np.ndarray, F: np.ndarray, n: int, rng,
                   weights: Optional[np.ndarray] = None) -> np.ndarray:
    """Area-weighted barycentric surface sampling of a triangle mesh/soup.
    `weights` (per-face, e.g. mean alpha) multiplies triangle area, matching
    src/eval_geometry.soup_pointcloud."""
    rng = _rng(rng)
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int64)
    tri = V[F]                                       # (M,3,3)
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    area = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
    w = area if weights is None else area * np.clip(np.asarray(weights), 0, 1)
    w = w / (w.sum() + 1e-12)
    counts = rng.multinomial(n, w)
    out = []
    for fi in np.nonzero(counts)[0]:
        k = int(counts[fi])
        r1, r2 = rng.random(k), rng.random(k)
        sq = np.sqrt(r1)
        a = 1.0 - sq
        b = sq * (1.0 - r2)
        cc = sq * r2
        out.append(a[:, None] * tri[fi, 0] + b[:, None] * tri[fi, 1] + cc[:, None] * tri[fi, 2])
    return np.concatenate(out, axis=0) if out else np.zeros((0, 3))


def soup_cloud(ckpt: dict, n: int, rng) -> np.ndarray:
    """Sample a DiffSoup checkpoint dict (keys V, F, alpha_acc) weighted by
    (mean alpha) x area — the geometric proxy used in src/eval_geometry.py."""
    V = ckpt["V"]
    F = ckpt["F"]
    V = V.numpy() if hasattr(V, "numpy") else np.asarray(V)
    F = F.numpy() if hasattr(F, "numpy") else np.asarray(F)
    alpha = None
    if "alpha_acc" in ckpt and ckpt["alpha_acc"] is not None:
        a = ckpt["alpha_acc"]
        a = a.numpy() if hasattr(a, "numpy") else np.asarray(a)
        alpha = a.reshape(F.shape[0], -1).mean(1)
    elif "alpha" in ckpt and ckpt["alpha"] is not None:        # trajectory dumps
        a = ckpt["alpha"]
        alpha = (a.numpy() if hasattr(a, "numpy") else np.asarray(a)).reshape(-1)
    return sample_surface(V, F, n, rng, weights=alpha)
