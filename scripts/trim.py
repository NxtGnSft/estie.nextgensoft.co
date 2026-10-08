#!/usr/bin/env /usr/bin/python3
"""One-time, idempotent: crop product PNGs to their flat grey panel, dropping the white PDF margins
and the baked-in code label (which sits above the panel). Run from repo root: /usr/bin/python3 scripts/trim.py"""
import glob, sys
import pymupdf

PANEL = (137, 137, 137)
LABEL = (63, 70, 53)

def near(c, t, tol=6):
    return all(abs(a - b) <= tol for a, b in zip(c[:3], t))

def panel_bbox(pm):
    w, h = pm.width, pm.height
    def row_ok(y): return sum(near(pm.pixel(x, y), PANEL) for x in range(0, w, 4)) * 4 > w * 0.3
    def col_ok(x): return sum(near(pm.pixel(x, y), PANEL) for y in range(0, h, 4)) * 4 > h * 0.3
    ys = [y for y in range(h) if row_ok(y)]
    xs = [x for x in range(w) if col_ok(x)]
    return (xs[0], ys[0], xs[-1] + 1, ys[-1] + 1) if xs and ys else None

def label_bottom(pm):
    ys = [y for y in range(int(pm.height * 0.25)) for x in range(0, int(pm.width * 0.5), 2) if near(pm.pixel(x, y), LABEL, 3)]
    return max(ys) + 1 if ys else 0

changed = skipped = 0
for f in sorted(glob.glob('src/assets/products/*.png')):
    pm = pymupdf.Pixmap(f)
    white_top = sum(near(pm.pixel(x, 0), (255, 255, 255)) for x in range(0, pm.width, 4)) * 4 > pm.width * 0.8
    white_left = sum(near(pm.pixel(0, y), (255, 255, 255)) for y in range(0, pm.height, 4)) * 4 > pm.height * 0.8
    if not (white_top or white_left):
        continue  # no white PDF margin: already trimmed (keeps the script idempotent)
    box = panel_bbox(pm)
    if not box:
        print('SKIP no panel', f); skipped += 1; continue
    x0, y0, x1, y1 = box
    y0 = max(y0, label_bottom(pm))  # label overlaps the panel top on a few pages
    if (x0, y0, x1, y1) == (0, 0, pm.width, pm.height):
        continue
    if x1 - x0 < pm.width * 0.5 or y1 - y0 < 150:
        print('SKIP odd box', f, box); skipped += 1; continue
    pymupdf.Pixmap(pm, pm.width, pm.height, pymupdf.IRect(x0, y0, x1, y1)).save(f)
    changed += 1
print(f'changed {changed}, skipped {skipped}')
