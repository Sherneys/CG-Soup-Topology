# scripts/make_kinkin_figure.py
# Paper-2 figure: the certified kinkin shell rendered as aluminium
# (advisor request, 2026-07-11). Two panels:
#   paper2/figures/kinkin_alu.png      - exterior, 3/4 view
#   paper2/figures/kinkin_alu_cut.png  - cutaway (y<=0 half): the flue
#                                        interior = the on-axis H2 void
# Open3D's Filament OffscreenRenderer needs EGL-headless (unsupported on
# Windows), so this renders with the CPU RaycastingScene (the same machinery
# make_kinkin_asset.py used for its distance field) + a small metal shader:
# pure-specular Schlick fresnel at aluminium F0 against a procedural studio
# environment, smooth vertex normals, 2x supersampling. No GL, no GPU.
#
#   D:\...\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_kinkin_figure.py

import os

import numpy as np
import open3d as o3d
from PIL import Image

_TOPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
SRC = os.path.join(DENTISTRY, "output", "synth", "_meshes", "kinkin_src.ply")
OUT_DIR = os.path.join(_TOPO, "paper2", "figures")

OUT_W, OUT_H = 1400, 1400   # final panel size; rendered at 2x and downsampled
SS = 2
FOV_DEG = 30.0

F0 = np.array([0.913, 0.921, 0.925])   # aluminium base reflectivity
ROUGHNESS = 0.32


def load_shell():
    mesh = o3d.io.read_triangle_mesh(SRC)
    assert mesh.has_triangles(), f"could not read {SRC}"
    mesh.compute_vertex_normals()
    V = np.asarray(mesh.vertices)
    F = np.asarray(mesh.triangles)
    N = np.asarray(mesh.vertex_normals)
    return V, F, N


def half(V, F, N):
    """Dollhouse section: drop the half nearest the exterior-view camera
    (y<0), so the same 3/4 view looks into the sliced pot."""
    keep = V[F].mean(axis=1)[:, 1] >= 0.0   # cut plane y=0 through the axis
    return V, F[keep], N


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def _smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def env_color(d):
    """Procedural studio for metal: mid-gray zenith, near-black ground, a
    narrow bright band above the horizon, two softbox lobes. The strong
    vertical contrast is what makes aluminium read as aluminium."""
    up = np.clip(d[..., 2], -1.0, 1.0)
    zen = np.array([0.46, 0.50, 0.56])
    hor = np.array([0.95, 0.94, 0.90])
    gnd = np.array([0.12, 0.12, 0.135])
    t_up = _smooth(up, 0.0, 0.55)[..., None]
    t_dn = _smooth(-up, 0.0, 0.35)[..., None]
    col = (hor * (1 - t_up) * (1 - t_dn) + zen * t_up + gnd * t_dn)
    col = col + np.array([1.0, 1.0, 1.0]) \
        * (0.9 * np.exp(-((up - 0.12) / 0.16) ** 2))[..., None]
    for axis, power, gain, tint in (
            ((0.45, -0.65, 0.61), 300.0, 2.4, (1.0, 1.0, 1.0)),
            ((-0.72, 0.28, 0.52), 130.0, 1.0, (1.0, 0.98, 0.95))):
        a = np.clip(np.tensordot(d, _unit(np.array(axis, float)), axes=([-1], [0])), 0, 1)
        col = col + np.asarray(tint) * (gain * a ** power)[..., None]
    return col


def rays_for(eye, center, up, w, h):
    fwd = _unit(center - eye)
    right = _unit(np.cross(fwd, up))
    upv = np.cross(right, fwd)
    tanf = np.tan(np.radians(FOV_DEG) / 2)
    xs = (np.arange(w) + 0.5) / w * 2 - 1
    ys = 1 - (np.arange(h) + 0.5) / h * 2
    gx, gy = np.meshgrid(xs * tanf * (w / h), ys * tanf)
    dirs = _unit(fwd + gx[..., None] * right + gy[..., None] * upv)
    return dirs


def frame_eye(Vb, center, eye_dir, up, margin=0.80):
    """Place the eye so the bbox corners fill `margin` of the frame."""
    eye_dir = _unit(np.asarray(eye_dir, float))
    radius = np.linalg.norm(Vb - center, axis=1).max()
    d = 3.5 * radius
    tanf = np.tan(np.radians(FOV_DEG) / 2)
    for _ in range(3):
        eye = center + eye_dir * d
        fwd = _unit(center - eye)
        right = _unit(np.cross(fwd, up))
        upv = np.cross(right, fwd)
        rel = Vb - eye
        z = rel @ fwd
        x = np.abs(rel @ right) / (z * tanf)
        y = np.abs(rel @ upv) / (z * tanf)
        d *= max(x.max(), y.max()) / margin
    return center + eye_dir * d


def render(V, F, N, out_png, eye_dir, up=(0, 0, 1.0), frame_pts=None):
    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(
        o3d.core.Tensor(V.astype(np.float32)),
        o3d.core.Tensor(F.astype(np.uint32)))

    used = V[np.unique(F)] if frame_pts is None else frame_pts
    center = 0.5 * (used.min(0) + used.max(0))
    corners = used[np.random.default_rng(0).choice(len(used), min(len(used), 4000),
                                                   replace=False)]
    up = np.asarray(up, float)
    eye = frame_eye(corners, center, eye_dir, up)

    w, h = OUT_W * SS, OUT_H * SS
    dirs = rays_for(eye, center, up, w, h)
    origins = np.broadcast_to(eye, dirs.shape)
    rays = o3d.core.Tensor(
        np.concatenate([origins, dirs], -1).reshape(-1, 6).astype(np.float32))
    ans = scene.cast_rays(rays)
    t = ans["t_hit"].numpy().reshape(h, w)
    prim = ans["primitive_ids"].numpy().reshape(h, w)
    uv = ans["primitive_uvs"].numpy().reshape(h, w, 2)
    hit = np.isfinite(t)

    img = np.ones((h, w, 3), np.float64)          # white background
    if hit.any():
        f = F[prim[hit]]
        u, vv = uv[hit, 0], uv[hit, 1]
        n = (N[f[:, 0]] * (1 - u - vv)[:, None]
             + N[f[:, 1]] * u[:, None] + N[f[:, 2]] * vv[:, None])
        n = _unit(n)
        view = -dirs[hit]
        ndv = np.sum(n * view, -1)
        n[ndv < 0] *= -1.0                        # two-sided (cutaway interior)
        ndv = np.abs(ndv)
        refl = _unit(2 * ndv[:, None] * n - view)
        refl = _unit(refl * (1 - ROUGHNESS**2 * 0.9) + n * (ROUGHNESS**2 * 0.9))
        fres = F0 + (1 - F0) * (1 - ndv[:, None]) ** 5

        # one-bounce self-reflection: where the mirror ray re-hits the shell,
        # the metal reflects (dim) metal, not sky --- this darkens the flue
        # interior into the "hidden chamber" the caption talks about
        p = origins[hit] + t[hit][:, None] * dirs[hit] + n * 1e-4
        sec = scene.cast_rays(o3d.core.Tensor(
            np.concatenate([p, refl], -1).astype(np.float32)))
        blocked = np.isfinite(sec["t_hit"].numpy())
        env = env_color(refl)
        env[blocked] = env[blocked] * 0.35 + 0.05

        col = env * fres + F0 * 0.02
        col = col / (1 + col)                     # Reinhard
        img[hit] = np.clip(col, 0, 1) ** (1 / 2.2)
    img = np.clip(img, 0, 1)

    img = img.reshape(OUT_H, SS, OUT_W, SS, 3).mean((1, 3))
    Image.fromarray((img * 255).round().astype(np.uint8)).save(out_png)
    print("wrote", out_png)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    V, F, N = load_shell()
    ext = V.max(0) - V.min(0)
    print(f"shell: {len(V)} verts / {len(F)} tris, extent {np.round(ext, 3)}")

    render(V, F, N, os.path.join(OUT_DIR, "kinkin_alu.png"),
           eye_dir=(1.0, -1.35, 0.72))
    # same pose, near half removed -> section view at identical scale
    render(*half(V, F, N), os.path.join(OUT_DIR, "kinkin_alu_cut.png"),
           eye_dir=(1.0, -1.35, 0.72), frame_pts=V)


if __name__ == "__main__":
    main()
