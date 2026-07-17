# scripts/make_matrix_figure.py
# Paper-2 round-4 figure (advisor request 2026-07-17, "Qualitative
# Comparison Matrix" merged with the teaser concept): GT / C0 baseline /
# C2 control / C1 ours, one row per external mesh of the generality wave
# (bob: H1 loop story; fandisk: largest effect; tom-yum pot: showcase,
# cutaway so the flue chamber = the H2 void is visible).
# Rows use seed 0 of the committed runs (final_params.pt); no re-runs.
# Rendering: CPU RaycastingScene (same machinery as make_kinkin_figure.py;
# Filament offscreen needs EGL, unavailable on Windows). Neutral light-gray
# material + studio-ish two-light shading per the advisor's teaser spec;
# soups shade with FLAT face normals (the representation is a soup --
# faceting is honest), GT meshes with smooth vertex normals.
#
#   D:\...\CG-Soup-for-Digital-Dentistry\.venv\Scripts\python.exe `
#       scripts\make_matrix_figure.py
#
# Output: paper2/figures/matrix.png (+ per-cell PNGs in
# paper2/figures/matrix_cells/ for inspection).

import os

import numpy as np
import open3d as o3d
import torch
from PIL import Image, ImageDraw, ImageFont

_TOPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENTISTRY = os.environ.get("CGSOUP_ROOT", r"D:\Project\CG-Soup-for-Digital-Dentistry")
MESHES = os.path.join(DENTISTRY, "output", "synth", "_meshes")
TRAIN = os.path.join(DENTISTRY, "output", "synth", "topo3", "_train")
OUT_DIR = os.path.join(_TOPO, "paper2", "figures")
CELL_DIR = os.path.join(OUT_DIR, "matrix_cells")

CELL_W, CELL_H = 900, 700
SS = 2
FOV_DEG = 30.0
ALBEDO = np.array([0.80, 0.81, 0.83])   # plain light gray (advisor spec)

ROWS = [
    # (shape key, GT file, run prefix, eye_dir, cutaway?)
    ("bob",     "bob_src.ply",    "bob",     (1.0, -0.9, 0.55), False),
    ("fandisk", "fandisk.obj",    "fandisk", (1.0, -1.0, 0.65), False),
    ("kinkin",  "kinkin_src.ply", "kinkin",  (1.0, -1.35, 0.72), True),
]
CONDS = [("C0", "{s}_C0_s0"), ("C2", "{s}_C2_r0.1_s0"), ("C1", "{s}_C1_r0.1_s0")]


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def load_gt(fname):
    mesh = o3d.io.read_triangle_mesh(os.path.join(MESHES, fname))
    assert mesh.has_triangles(), fname
    mesh.compute_vertex_normals()
    return (np.asarray(mesh.vertices), np.asarray(mesh.triangles),
            np.asarray(mesh.vertex_normals))


def load_soup(tag):
    d = torch.load(os.path.join(TRAIN, tag, "final_params.pt"),
                   map_location="cpu", weights_only=False)
    V = d["V"].numpy().astype(np.float64)
    F = d["F"].numpy().astype(np.int64)
    return V, F


def cutaway(V, F, plane_axis=1, keep_ge=0.0):
    keep = V[F].mean(axis=1)[:, plane_axis] >= keep_ge
    return V, F[keep]


def rays_for(eye, center, up, w, h):
    fwd = _unit(center - eye)
    right = _unit(np.cross(fwd, up))
    upv = np.cross(right, fwd)
    tanf = np.tan(np.radians(FOV_DEG) / 2)
    xs = (np.arange(w) + 0.5) / w * 2 - 1
    ys = 1 - (np.arange(h) + 0.5) / h * 2
    gx, gy = np.meshgrid(xs * tanf * (w / h), ys * tanf)
    return _unit(fwd + gx[..., None] * right + gy[..., None] * upv)


def frame_eye(Vb, center, eye_dir, up, margin=0.78):
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


LIGHTS = [((0.5, -0.7, 0.65), 0.85), ((-0.75, 0.35, 0.45), 0.35),
          ((0.1, 0.9, -0.2), 0.18)]
AMBIENT = 0.30


def shade(n, view):
    ndv = np.sum(n * view, -1)
    n = n.copy()
    n[ndv < 0] *= -1.0            # two-sided (soups + cutaway interiors)
    c = np.full(n.shape, AMBIENT)
    for axis, gain in LIGHTS:
        l = _unit(np.asarray(axis, float))
        c += gain * np.clip(n @ l, 0, 1)[:, None]
    col = ALBEDO * c
    col = col / (1 + 0.25 * col)
    return np.clip(col, 0, 1) ** (1 / 2.2)


def render_cell(V, F, N_vert, out_png, eye, center, up):
    """N_vert=None -> flat face normals (soup); else smooth vertex normals."""
    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(o3d.core.Tensor(V.astype(np.float32)),
                        o3d.core.Tensor(F.astype(np.uint32)))
    w, h = CELL_W * SS, CELL_H * SS
    dirs = rays_for(eye, center, up, w, h)
    origins = np.broadcast_to(eye, dirs.shape)
    rays = o3d.core.Tensor(
        np.concatenate([origins, dirs], -1).reshape(-1, 6).astype(np.float32))
    ans = scene.cast_rays(rays)
    t = ans["t_hit"].numpy().reshape(h, w)
    prim = ans["primitive_ids"].numpy().reshape(h, w)
    uv = ans["primitive_uvs"].numpy().reshape(h, w, 2)
    hit = np.isfinite(t)

    img = np.ones((h, w, 3), np.float64)
    if hit.any():
        f = F[prim[hit]]
        if N_vert is None:
            e1 = V[f[:, 1]] - V[f[:, 0]]
            e2 = V[f[:, 2]] - V[f[:, 0]]
            n = _unit(np.cross(e1, e2))
        else:
            u, vv = uv[hit, 0], uv[hit, 1]
            n = _unit(N_vert[f[:, 0]] * (1 - u - vv)[:, None]
                      + N_vert[f[:, 1]] * u[:, None]
                      + N_vert[f[:, 2]] * vv[:, None])
        img[hit] = shade(n, -dirs[hit])
    img = img.reshape(CELL_H, SS, CELL_W, SS, 3).mean((1, 3))
    Image.fromarray((np.clip(img, 0, 1) * 255).round().astype(np.uint8)).save(out_png)
    print("  wrote", os.path.basename(out_png))
    return out_png


def label_font(size):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


# Measured significant-feature count per cell (seed 0 = the rendered run;
# identical across seeds for every entry shown — see % src below).
# src: topo3/report/results.json nsig_final (bob/fandisk, all seeds) +
#      topo3/quicklook.json nsig_H2 (kinkin, all seeds).
# bob true #sig H1 = 2: C0 2 / C2 1 / C1 2.
# fandisk true #sig H2 = 1: C0 1 / C2 0 / C1 1.
# kinkin (tom-yum pot) true #sig H2 = 1: C0 1 / C2 0 / C1 1.
BADGES = {
    "bob":     {"dim": 1, "true": 2, "C0": 2, "C2": 1, "C1": 2},
    "fandisk": {"dim": 2, "true": 1, "C0": 1, "C2": 0, "C1": 1},
    "kinkin":  {"dim": 2, "true": 1, "C0": 1, "C2": 0, "C1": 1},
}
# Okabe-Ito colour-blind-safe: blue = correct reading, vermillion = wrong.
OK_COL = (0, 114, 178)
BAD_COL = (213, 94, 0)


def draw_badge(draw, x_right, y, text, ok, font):
    """Correct reading: white badge, blue outline+text. Wrong reading:
    FILLED vermillion badge, white text — distinct in grayscale print
    too (colour-blind-safe Okabe-Ito pair)."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 18, 12
    w, h = tw + 2 * pad_x, th + 2 * pad_y
    x0 = x_right - w - 14
    if ok:
        draw.rounded_rectangle([x0, y, x0 + w, y + h], radius=14,
                               fill=(255, 255, 255), outline=OK_COL, width=5)
        draw.text((x0 + pad_x, y + pad_y - bbox[1]), text, fill=OK_COL, font=font)
    else:
        draw.rounded_rectangle([x0, y, x0 + w, y + h], radius=14,
                               fill=BAD_COL, outline=BAD_COL, width=5)
        draw.text((x0 + pad_x, y + pad_y - bbox[1]), text,
                  fill=(255, 255, 255), font=font)


def assemble(cells, out_png, rows=None):
    """cells: dict[(row, col)] -> path; grid with header row + row labels
    + per-cell measured-count badges (the topology verdict is a diagram
    READING — geometry renders alone cannot carry it, so each cell states
    its measured significant-feature count against the true one).
    `rows` selects/orders a subset of ROWS by shape key (default: all) —
    the main teaser uses fandisk+kinkin (page budget; the advisor's own
    lead pair), the bob strip becomes a supplementary figure."""
    all_labels = {r[0]: lbl for r, lbl in zip(
        ROWS, ["bob (H1)", "fandisk (H2)", "tom-yum pot\n(H2, cutaway)"])}
    sel = [r for r in ROWS if rows is None or r[0] in rows]
    col_heads = ["ground truth", "baseline C0", "control C2", "ours C1"]
    row_labels = {s: all_labels[s] for s, *_ in sel}
    pad, head_h = 8, 84

    # Per-row auto-crop: shared tight bbox over the row's 4 cells (same
    # crop for all so alignment/scale stays comparable), 3% margin.
    imgs, boxes = {}, {}
    for shape, *_ in sel:
        row_imgs = [Image.open(cells[(shape, j)]) for j in range(4)]
        lo_x = lo_y = 10**9
        hi_x = hi_y = -1
        for im in row_imgs:
            a = np.asarray(im.convert("L"))
            ys, xs = np.where(a < 250)
            if len(xs):
                lo_x, hi_x = min(lo_x, xs.min()), max(hi_x, xs.max())
                lo_y, hi_y = min(lo_y, ys.min()), max(hi_y, ys.max())
        mx = int(0.03 * CELL_W)
        box = (max(0, lo_x - mx), max(0, lo_y - mx),
               min(CELL_W, hi_x + mx), min(CELL_H, hi_y + mx))
        boxes[shape] = box
        imgs[shape] = [im.crop(box) for im in row_imgs]

    # uniform cell size: scale every cropped row to a common width
    out_w = 860
    rows_sized = {}
    for shape, *_ in sel:
        w0, h0 = imgs[shape][0].size
        h1 = int(round(h0 * out_w / w0))
        rows_sized[shape] = ([im.resize((out_w, h1), Image.LANCZOS)
                              for im in imgs[shape]], h1)

    W = 4 * out_w + 5 * pad
    H = head_h + sum(h for _, h in rows_sized.values()) + len(sel) * pad
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    f_head = label_font(52)
    f_row = label_font(40)
    f_badge = label_font(38)
    for j, htxt in enumerate(col_heads):
        x = pad + j * (out_w + pad)
        bbox = draw.textbbox((0, 0), htxt, font=f_head)
        draw.text((x + (out_w - (bbox[2] - bbox[0])) / 2, (head_h - 58) / 2),
                  htxt, fill=(20, 20, 20), font=f_head)
    y = head_h
    for shape, *_rest in sel:
        row_imgs, row_h = rows_sized[shape]
        b = BADGES[shape]
        for j in range(4):
            x = pad + j * (out_w + pad)
            canvas.paste(row_imgs[j], (x, y))
            x_right = x + out_w
            if j == 0:
                draw_badge(draw, x_right, y + 8,
                           f"true #sig H{b['dim']} = {b['true']}", True, f_badge)
            else:
                cond = ["C0", "C2", "C1"][j - 1]
                got = b[cond]
                draw_badge(draw, x_right, y + 8,
                           f"reads {got}", got == b["true"], f_badge)
        draw.multiline_text((pad + 10, y + 8), row_labels[shape],
                            fill=(20, 20, 20), font=f_row, spacing=6)
        y += row_h + pad
    canvas.save(out_png)
    print("wrote", out_png, canvas.size)


def main():
    import sys
    os.makedirs(CELL_DIR, exist_ok=True)
    if "--assemble-only" in sys.argv:
        cells = {}
        for shape, _, _, _, _ in ROWS:
            cells[(shape, 0)] = os.path.join(CELL_DIR, f"{shape}_gt.png")
            for j, (cond, _) in enumerate(CONDS, start=1):
                cells[(shape, j)] = os.path.join(CELL_DIR, f"{shape}_{cond}.png")
        assert all(os.path.exists(p) for p in cells.values())
        assemble(cells, os.path.join(OUT_DIR, "matrix.png"),
                 rows=("fandisk", "kinkin"))
        assemble(cells, os.path.join(OUT_DIR, "matrix_bob.png"),
                 rows=("bob",))
        return
    cells = {}
    up = np.array([0.0, 0.0, 1.0])
    for shape, gt_file, prefix, eye_dir, cut in ROWS:
        Vg, Fg, Ng = load_gt(gt_file)
        soups = {}
        for cond, pat in CONDS:
            Vs, Fs = load_soup(pat.format(s=prefix))
            soups[cond] = (Vs, Fs)
            print(f"  {cond}: {len(Vs)}v/{len(Fs)}t bbox "
                  f"{np.round(Vs.min(0), 2)}..{np.round(Vs.max(0), 2)}")
        # Scene builds may normalize the source mesh (fandisk.obj is in raw
        # CAD coordinates); align the GT to the training frame by matching
        # the C0 soup's bbox (uniform scale + translation — extents ratios
        # are axis-consistent, no rotation).
        V0 = soups["C0"][0]
        ext_g = Vg.max(0) - Vg.min(0)
        ext_s = V0.max(0) - V0.min(0)
        s = float(np.mean(ext_s / ext_g))
        if abs(s - 1.0) > 0.05:
            cg = 0.5 * (Vg.min(0) + Vg.max(0))
            cs = 0.5 * (V0.min(0) + V0.max(0))
            Vg = (Vg - cg) * s + cs
            print(f"  GT normalized into scene frame (scale {s:.3f})")
        print(f"{shape}: GT {len(Vg)}v/{len(Fg)}t bbox "
              f"{np.round(Vg.min(0), 2)}..{np.round(Vg.max(0), 2)}")
        # one shared camera per row, framed on the GT
        used = Vg[np.unique(Fg)]
        center = 0.5 * (used.min(0) + used.max(0))
        corners = used[np.random.default_rng(0).choice(
            len(used), min(len(used), 4000), replace=False)]
        eye = frame_eye(corners, center, eye_dir, up)

        Vc, Fc = (cutaway(Vg, Fg) if cut else (Vg, Fg))
        cells[(shape, 0)] = render_cell(
            Vc, Fc, Ng, os.path.join(CELL_DIR, f"{shape}_gt.png"),
            eye, center, up)
        for j, (cond, _) in enumerate(CONDS, start=1):
            Vs, Fs = soups[cond]
            if cut:
                Vs, Fs = cutaway(Vs, Fs)
            cells[(shape, j)] = render_cell(
                Vs, Fs, None,
                os.path.join(CELL_DIR, f"{shape}_{cond}.png"), eye, center, up)
    assemble(cells, os.path.join(OUT_DIR, "matrix.png"),
             rows=("fandisk", "kinkin"))
    assemble(cells, os.path.join(OUT_DIR, "matrix_bob.png"), rows=("bob",))


if __name__ == "__main__":
    main()
