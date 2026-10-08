#!/usr/bin/env /usr/bin/python3
"""One-time extraction of products, crops and site images from the catalog PDF.

Run from repo root:  /usr/bin/python3 scripts/extract.py
Outputs are committed; the script is not part of the Astro build.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "public" / "ESTIE-KUSUMA-catalog.pdf"
OUT_JSON = ROOT / "src" / "data" / "products.json"
PRODUCT_DIR = ROOT / "src" / "assets" / "products"
SITE_DIR = ROOT / "src" / "assets" / "site"
REVIEW = ROOT / "scripts" / "review.html"

EXPECTED_COUNT = 291
PRODUCT_DPI = 300
SITE_DPI = 200
PRODUCT_PAGES = range(3, 50)  # 0-based page indexes 3..49 (PDF pages 4..50)

CATEGORY_ORDER = [
    "dining-chairs", "dining-tables", "bar-stools", "lounge-chairs", "sofas",
    "benches", "coffee-tables", "nightstands", "sideboards-tv-cabinets",
]
CATEGORY_BY_PREFIX = {
    "DC": "dining-chairs", "DT": "dining-tables", "BT": "bar-stools",
    "LC": "lounge-chairs", "SF": "sofas", "BC": "benches", "CT": "coffee-tables",
    "NS": "nightstands", "SB": "sideboards-tv-cabinets", "TC": "sideboards-tv-cabinets",
}
CODE_RE = re.compile(r"^([A-Z]{2})-(\d{2})$")
KEY_RE = re.compile(r"^(Material|Dimension|Finish|Fabric|Leather)\s*:?\s*(.*)$", re.I)
SMALL_WORDS = {"&", "TV", "SC", "DE"}

# Page index -> {output name: clip rect in PDF points}. Tune after looking at review.html.
SITE_CLIPS = {
    1: {  # OUR PROJECT
        "project-01": (56, 118, 292, 318), "project-02": (298, 118, 539, 318),
        "project-03": (56, 354, 292, 559), "project-04": (298, 354, 539, 559),
        "project-05": (56, 593, 292, 816), "project-06": (298, 593, 539, 816),
    },
    2: {  # PRODUCTION PROCESS, photo area below each label chip
        "process-01": (49, 251, 205, 342), "process-02": (218, 251, 374, 342), "process-03": (388, 251, 544, 342),
        "process-04": (49, 427, 205, 518), "process-05": (218, 427, 374, 518), "process-06": (388, 427, 544, 518),
        "process-07": (49, 605, 205, 698), "process-08": (218, 605, 374, 698),
    },
    50: {  # MATERIAL SAMPLE
        "swatch-finish": (49, 136, 295, 436), "swatch-rattan": (302, 136, 550, 436),
        "swatch-fabric": (49, 467, 295, 764), "swatch-webbing": (302, 467, 550, 764),
    },
    51: {"logo": (67, 236, 241, 410)},
}
PROCESS_LABELS = ["Raw Material", "Kiln Dry / Oven", "Craftsman Process", "Over Process",
                  "Sanding Process", "QC Process", "Packing Process", "Loading Process"]


def num(s: str) -> float | int:
    v = float(s.replace(",", "."))
    return int(v) if v.is_integer() else v


def parse_dimensions(raw: str) -> dict:
    raw = raw.strip()
    nums = re.findall(r"\d+(?:[.,]\d+)?", raw)
    letters = re.sub(r"[\d.,\s]|cm|x|X|\*", "", raw)
    if len(nums) == 3 and letters in ("", "WDH"):
        w, d, h = (num(n) for n in nums)
        return {"raw": raw, "w": w, "d": d, "h": h}
    return {"raw": raw}


def title_case(s: str) -> str:
    out = []
    for w in s.split():
        out.append(w if w in SMALL_WORDS else w.capitalize())
    return " ".join(out)


def parse_specs(rows: list[str]) -> dict:
    """rows: text rows under one product box, top to bottom. First row is the name."""
    spec: dict[str, str | None] = {"material": None, "dimension": None, "finish": None,
                                   "fabric": None, "leather": None}
    name = rows[0] if rows else ""
    last_key = None
    for row in rows[1:]:
        m = KEY_RE.match(row)
        if m:
            last_key = m.group(1).lower()
            spec[last_key] = m.group(2).strip() or None
        elif last_key:
            spec[last_key] = ((spec[last_key] or "") + " " + row).strip()
    for k, v in spec.items():
        if v:
            spec[k] = re.sub(r"^:\s*", "", v).strip()
    return {
        "name": title_case(name),
        "material": spec["material"],
        "dimensions": parse_dimensions(spec["dimension"] or ""),
        "finish": spec["finish"],
        "fabric": spec["fabric"],
        "leather": spec["leather"],
    }


def spans(page) -> list[dict]:
    out = []
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for s in line["spans"]:
                t = s["text"].strip()
                if t:
                    out.append({"text": t, "rect": pymupdf.Rect(s["bbox"])})
    return out


def candidate_boxes(page) -> list[pymupdf.Rect]:
    boxes = [pymupdf.Rect(i["bbox"]) for i in page.get_image_info() if i["bbox"][2] - i["bbox"][0] > 100]
    for d in page.get_drawings():
        f = d.get("fill")
        if f and all(abs(c - 0.54) < 0.03 for c in f[:3]):
            boxes.append(pymupdf.Rect(d["rect"]))
    return boxes


def find_products(page) -> list[tuple[str, pymupdf.Rect]]:
    """Return [(code, box_rect)] for every code label on the page."""
    boxes = candidate_boxes(page)
    found = []
    for s in spans(page):
        if not CODE_RE.match(s["text"]):
            continue
        # The box must contain the whole label; product photos placed inside the box start
        # below the label, so they never qualify.
        containing = [b for b in boxes if b.contains(s["rect"])]
        if containing:
            box = min(containing, key=lambda b: b.width * b.height)
        else:  # fallback: 3-column layout geometry
            box = pymupdf.Rect(s["rect"].x0 - 10, s["rect"].y0 - 4, s["rect"].x0 + 142, s["rect"].y0 + 140)
        found.append((s["text"], box))
    return found


def rows_under(page, box: pymupdf.Rect, y_limit: float) -> list[str]:
    # The 100pt tolerance on the lower bound is safe because the minimum box height across
    # all 291 products is 132.05pt, which exceeds 100pt: box.y1 - 100 can never drop below
    # box.y0 (the box's own top edge), so this can never reach up into the preceding
    # product's row above the box.
    items = [s for s in spans(page)
             if box.x0 - 15 <= s["rect"].x0 < box.x1 and box.y1 - 100 < s["rect"].y0 < y_limit
             and not CODE_RE.match(s["text"])]
    items.sort(key=lambda s: (s["rect"].y0, s["rect"].x0))
    rows: list[list[dict]] = []
    for s in items:
        if rows and abs(s["rect"].y0 - rows[-1][0]["rect"].y0) <= 4:
            rows[-1].append(s)
        else:
            rows.append([s])
    out = []
    for r in rows:
        r.sort(key=lambda s: s["rect"].x0)
        out.append(re.sub(r"\s+", " ", " ".join(s["text"] for s in r)).strip())
    return out


def extract_products(doc) -> list[dict]:
    products = []
    PRODUCT_DIR.mkdir(parents=True, exist_ok=True)
    for pno in PRODUCT_PAGES:
        page = doc[pno]
        found = find_products(page)
        for code, box in found:
            below = [b for c, b in found if b.y0 > box.y1 and b.x0 < box.x1 and b.x1 > box.x0]
            y_limit = min((b.y0 for b in below), default=page.rect.height)
            rows = rows_under(page, box, y_limit)
            slug = code.lower()
            page.get_pixmap(dpi=PRODUCT_DPI, clip=box).save(PRODUCT_DIR / f"{slug}.png")
            products.append({
                "code": code, "slug": slug, "category": CATEGORY_BY_PREFIX[code[:2]],
                **parse_specs(rows),
                "image": f"../assets/products/{slug}.png", "page": pno + 1,
            })
    products.sort(key=lambda p: (CATEGORY_ORDER.index(p["category"]), p["code"]))
    return products


def extract_site_images(doc) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    hero = max(doc[0].get_images(full=True), key=lambda i: i[2] * i[3])
    img = doc.extract_image(hero[0])
    ext = "jpg" if img["ext"] in ("jpg", "jpeg") else img["ext"]
    (SITE_DIR / f"hero.{ext}").write_bytes(img["image"])
    for pno, clips in SITE_CLIPS.items():
        for name, rect in clips.items():
            doc[pno].get_pixmap(dpi=SITE_DPI, clip=pymupdf.Rect(rect)).save(SITE_DIR / f"{name}.png")


def write_review(products: list[dict]) -> None:
    cells = []
    for p in products:
        cells.append(
            f'<div class="c"><img src="../src/assets/products/{p["slug"]}.png">'
            f'<pre>{html.escape(json.dumps({k: v for k, v in p.items() if k != "image"}, indent=1))}</pre></div>'
        )
    site = "".join(f'<figure><img src="../src/assets/site/{f.name}"><figcaption>{f.name}</figcaption></figure>'
                   for f in sorted(SITE_DIR.iterdir()))
    REVIEW.write_text(
        "<!doctype html><meta charset=utf-8><style>body{font:12px monospace;background:#eee}"
        ".c{display:inline-block;width:260px;vertical-align:top;margin:6px;background:#fff;padding:6px}"
        ".c img{width:100%;background:#8c8c8c}pre{white-space:pre-wrap}figure{display:inline-block;width:300px}"
        "figure img{width:100%}</style>"
        f"<h1>{len(products)} products</h1>{''.join(cells)}<h1>site images</h1>{site}"
    )


def main() -> int:
    doc = pymupdf.open(PDF)
    products = extract_products(doc)
    extract_site_images(doc)
    write_review(products)
    codes = [p["code"] for p in products]
    problems = [p["code"] for p in products if not p["name"] or not p["dimensions"]["raw"] or not p["material"]]
    print(f"found {len(codes)} products, {len(set(codes))} unique; {len(problems)} incomplete: {problems}")
    if len(set(codes)) != EXPECTED_COUNT or len(codes) != len(set(codes)):
        print(f"expected {EXPECTED_COUNT} unique codes; NOT writing {OUT_JSON}")
        return 1
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(products, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_JSON} and {REVIEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
