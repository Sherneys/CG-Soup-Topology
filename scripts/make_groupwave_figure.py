# scripts/make_groupwave_figure.py
# Round-5 group-wave render strip (advisor's "diversity" instinct made
# visible): GT / C0 / C2 / C1 rows for the four NEW external meshes —
# rocker-arm, eight, armadillo, horse — same machinery, material, badge
# convention and seed-0-final-params policy as the front-page matrix
# (imports the primitives from make_matrix_figure.py; no re-runs).
# Badge sources (audited): topo3/report/results.json nsig_final —
#   rocker-arm H1 true 1 (the measurable loop): C0 1 / C2 1 / C1 1
#     -> every badge BLUE: the no-headroom null, visualized;
#   eight H1 true 4 (bundle at M=8192): C0 2 / C2 2 / C1 seed-0 4
#     (per-seed 4/3/4 — caption states it; seed 0 is the rendered run);
#   armadillo / horse H2 true 1: C0 1 / C2 0 / C1 1.
#
#   D:\...\.venv\Scripts\python.exe scripts\make_groupwave_figure.py
# Output: paper2/figures/groupwave_matrix.png (+ cells in
# paper2/figures/groupwave_cells/)

import os
import sys

import numpy as np
from PIL import Image, ImageDraw

_TOPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_TOPO, "scripts"))
import make_matrix_figure as mm  # noqa: E402  (render primitives)

OUT_PNG = os.path.join(mm.OUT_DIR, "groupwave_matrix.png")
CELL_DIR = os.path.join(mm.OUT_DIR, "groupwave_cells")

ROWS = [
    # (key, GT file, run prefix, eye_dir, label, up)
    # armadillo's native frame is y-up (Stanford convention) — every
    # other mesh here is z-up; per-row up keeps each subject upright.
    ("rockerarm", "rockerarm_src.ply", "rockerarm", (1.0, -0.9, 0.60),
     "rocker-arm (H1)", (0, 0, 1)),
    ("eight",     "eight_src.ply",     "eight",     (0.55, -0.75, 1.00),
     "eight (H1)", (0, 0, 1)),
    ("armadillo", "armadillo_src.ply", "armadillo", (0.9, 0.45, 1.0),
     "armadillo (H2)", (0, 1, 0)),
    ("horse",     "horse_src.ply",     "horse",     (1.0, -0.55, 0.35),
     "horse (H2)", (0, 0, 1)),
]
CONDS = [("C0", "{s}_C0_s0"), ("C2", "{s}_C2_r0.1_s0"), ("C1", "{s}_C1_r0.1_s0")]

# src: topo3/report/results.json nsig_final (rockerarm [1,1,1] all arms;
# eight C0 [2,2,2] C2 [2,2,2] C1 [4,3,4] -> seed 0 = 4; armadillo/horse
# C0 [1,1,1] C2 [0,0,0] C1 [1,1,1])
BADGES = {
    "rockerarm": {"dim": 1, "true": 1, "C0": 1, "C2": 1, "C1": 1},
    "eight":     {"dim": 1, "true": 4, "C0": 2, "C2": 2, "C1": 4},
    "armadillo": {"dim": 2, "true": 1, "C0": 1, "C2": 0, "C1": 1},
    "horse":     {"dim": 2, "true": 1, "C0": 1, "C2": 0, "C1": 1},
}


def assemble(cells):
    col_heads = ["ground truth", "baseline C0", "control C2", "ours C1"]
    pad, head_h = 8, 84
    imgs = {}
    for key, *_ in ROWS:
        row_imgs = [Image.open(cells[(key, j)]) for j in range(4)]
        lo_x = lo_y = 10**9
        hi_x = hi_y = -1
        for im in row_imgs:
            a = np.asarray(im.convert("L"))
            ys, xs = np.where(a < 250)
            if len(xs):
                lo_x, hi_x = min(lo_x, xs.min()), max(hi_x, xs.max())
                lo_y, hi_y = min(lo_y, ys.min()), max(hi_y, ys.max())
        mx = int(0.03 * mm.CELL_W)
        box = (max(0, lo_x - mx), max(0, lo_y - mx),
               min(mm.CELL_W, hi_x + mx), min(mm.CELL_H, hi_y + mx))
        imgs[key] = [im.crop(box) for im in row_imgs]

    out_w = 860
    rows_sized = {}
    for key, *_ in ROWS:
        w0, h0 = imgs[key][0].size
        h1 = int(round(h0 * out_w / w0))
        rows_sized[key] = ([im.resize((out_w, h1), Image.LANCZOS)
                            for im in imgs[key]], h1)

    W = 4 * out_w + 5 * pad
    H = head_h + sum(h for _, h in rows_sized.values()) + len(ROWS) * pad
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    f_head = mm.label_font(52)
    f_row = mm.label_font(40)
    f_badge = mm.label_font(38)
    for j, htxt in enumerate(col_heads):
        x = pad + j * (out_w + pad)
        bbox = draw.textbbox((0, 0), htxt, font=f_head)
        draw.text((x + (out_w - (bbox[2] - bbox[0])) / 2, (head_h - 58) / 2),
                  htxt, fill=(20, 20, 20), font=f_head)
    y = head_h
    for key, _gt, _pre, _eye, label, _up in ROWS:
        row_imgs, row_h = rows_sized[key]
        b = BADGES[key]
        for j in range(4):
            x = pad + j * (out_w + pad)
            canvas.paste(row_imgs[j], (x, y))
            x_right = x + out_w
            if j == 0:
                mm.draw_badge(draw, x_right, y + 8,
                              f"true #sig H{b['dim']} = {b['true']}",
                              True, f_badge)
            else:
                cond = ["C0", "C2", "C1"][j - 1]
                got = b[cond]
                mm.draw_badge(draw, x_right, y + 8, f"reads {got}",
                              got == b["true"], f_badge)
        draw.multiline_text((pad + 10, y + 8), label,
                            fill=(20, 20, 20), font=f_row, spacing=6)
        y += row_h + pad
    canvas.save(OUT_PNG)
    print("wrote", OUT_PNG, canvas.size)


def main():
    os.makedirs(CELL_DIR, exist_ok=True)
    if "--assemble-only" in sys.argv:
        cells = {}
        for key, *_ in ROWS:
            cells[(key, 0)] = os.path.join(CELL_DIR, f"{key}_gt.png")
            for j, (cond, _) in enumerate(CONDS, start=1):
                cells[(key, j)] = os.path.join(CELL_DIR, f"{key}_{cond}.png")
        assert all(os.path.exists(p) for p in cells.values())
        assemble(cells)
        return
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    cells = {}
    for key, gt_file, prefix, eye_dir, _label, up_v in ROWS:
        if only and key != only:
            continue
        up = np.asarray(up_v, dtype=float)
        Vg, Fg, Ng = mm.load_gt(gt_file)
        soups = {}
        for cond, pat in CONDS:
            Vs, Fs = mm.load_soup(pat.format(s=prefix))
            soups[cond] = (Vs, Fs)
        V0 = soups["C0"][0]
        ext_g = Vg.max(0) - Vg.min(0)
        ext_s = V0.max(0) - V0.min(0)
        s = float(np.mean(ext_s / ext_g))
        if abs(s - 1.0) > 0.05:
            cg = 0.5 * (Vg.min(0) + Vg.max(0))
            cs = 0.5 * (V0.min(0) + V0.max(0))
            Vg = (Vg - cg) * s + cs
            print(f"  GT normalized into scene frame (scale {s:.3f})")
        print(f"{key}: GT {len(Vg)}v/{len(Fg)}t")
        used = Vg[np.unique(Fg)]
        center = 0.5 * (used.min(0) + used.max(0))
        corners = used[np.random.default_rng(0).choice(
            len(used), min(len(used), 4000), replace=False)]
        eye = mm.frame_eye(corners, center, eye_dir, up)
        cells[(key, 0)] = mm.render_cell(
            Vg, Fg, Ng, os.path.join(CELL_DIR, f"{key}_gt.png"),
            eye, center, up)
        for j, (cond, _) in enumerate(CONDS, start=1):
            Vs, Fs = soups[cond]
            cells[(key, j)] = mm.render_cell(
                Vs, Fs, None, os.path.join(CELL_DIR, f"{key}_{cond}.png"),
                eye, center, up)
    if only:
        for key, *_ in ROWS:
            cells.setdefault((key, 0), os.path.join(CELL_DIR, f"{key}_gt.png"))
            for j, (cond, _) in enumerate(CONDS, start=1):
                cells.setdefault((key, j),
                                 os.path.join(CELL_DIR, f"{key}_{cond}.png"))
    assemble(cells)


if __name__ == "__main__":
    main()
