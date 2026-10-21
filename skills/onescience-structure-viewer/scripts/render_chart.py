#!/usr/bin/env python3
"""Wrap raster charts (PNG/JPG/GIF/BMP) into a self-contained HTML.

Why this exists: the OneCode platform file preview only renders **HTML**; a
raw ``.png`` opened in the preview shows base64 gibberish instead of the
picture. Any 2D data chart that must be delivered (MACE training curves,
MD energy/temperature evolution, RDF, …) therefore has to ship as an HTML
wrapper, exactly like ``render_structure.py`` ships ``view.html`` for 3D
structures.

For each input image it writes a **sibling** ``<stem>.html`` that embeds the
image as a base64 data-URI. The result is a single self-contained file: no
external requests, no CDN, immune to CSP. This also satisfies the dft-model-gate
``I12`` hard gate (every ``X.png`` must have a matching ``X.html``).

    python3 render_chart.py mace_training.png md_energy_temp.png \
        --outdir . --title "Cu 3x3 MLMD 曲线" --combine --basename charts

    # or one image, HTML lands next to it automatically
    python3 render_chart.py structures/md_energy_temp.png

Emits:
  <stem>.html          one per input image (self-contained, base64-embedded)
  <basename>.html      combined index (only with --combine)

Exit code: 0 = OK, 2 = input error.
"""
from __future__ import annotations

import argparse
import base64
import html
import os
import sys
from pathlib import Path

# extension -> (data-URI mime, human label)
_MIME = {
    ".png": ("image/png", "PNG"),
    ".jpg": ("image/jpeg", "JPEG"),
    ".jpeg": ("image/jpeg", "JPEG"),
    ".gif": ("image/gif", "GIF"),
    ".bmp": ("image/bmp", "BMP"),
}

_TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  html,body{{margin:0;padding:0;background:#14161f;color:#e6e6f0;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;}}
  header{{padding:14px 22px;border-bottom:1px solid #2a3050;background:#191c28;}}
  header h1{{font-size:16px;margin:0;font-weight:600;}}
  header .sub{{color:#9aa0b5;font-size:12px;margin-top:5px;}}
  .wrap{{padding:22px;}}
  figure{{margin:0 auto 26px;display:inline-block;background:#ffffff;padding:12px;
    border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.35);max-width:100%;}}
  figure img{{max-width:100%;height:auto;display:block;}}
  figcaption{{color:#333;font-size:13px;margin-top:8px;text-align:center;}}
  .grid{{text-align:center;}}
  .note{{color:#7bd88f;font-size:12px;margin:2px 22px 0;}}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class="sub">{subtitle}</div>
</header>
<div class="note">自包含 HTML（图片以 base64 内嵌，无外部依赖）· OneCode 可直接渲染 · 共 {n} 图</div>
<div class="wrap grid">
{figures}
</div>
</body>
</html>
"""


def _data_uri(img_path: Path) -> str:
    ext = img_path.suffix.lower()
    mime, _label = _MIME[ext]
    raw = img_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


def _figure_html(img_path: Path, caption: str = "") -> str:
    cap = caption or img_path.name
    return ('<figure>\n  <img alt="%s" src="%s">\n  <figcaption>%s</figcaption>\n</figure>'
            % (html.escape(cap), _data_uri(img_path), html.escape(cap)))


def _page_html(title: str, subtitle: str, figures: list, n: int) -> str:
    return _TEMPLATE.format(
        title=html.escape(title),
        subtitle=html.escape(subtitle),
        figures="\n".join(figures),
        n=n,
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Wrap PNG/JPG charts into self-contained HTML (OneCode renders HTML only).")
    ap.add_argument("images", nargs="+", help="input raster image(s): .png/.jpg/.jpeg/.gif/.bmp")
    ap.add_argument("--outdir", default=None,
                    help="output dir for the generated HTML (default: alongside each image)")
    ap.add_argument("--title", default="图表可视化", help="HTML page title / header")
    ap.add_argument("--subtitle", default="", help="header subtitle line")
    ap.add_argument("--combine", action="store_true",
                    help="also emit a single combined index HTML with all images")
    ap.add_argument("--basename", default="charts",
                    help="basename for the --combine index HTML (default: charts)")
    args = ap.parse_args()

    imgs = []
    for s in args.images:
        p = Path(s)
        if not p.is_file():
            print("[ERROR] image not found: %s" % p, file=sys.stderr)
            return 2
        if p.suffix.lower() not in _MIME:
            print("[ERROR] unsupported image type: %s (allowed: %s)"
                  % (p, ", ".join(sorted(_MIME))), file=sys.stderr)
            return 2
        imgs.append(p)

    written = []
    for p in imgs:
        outdir = Path(args.outdir) if args.outdir else p.parent
        outdir.mkdir(parents=True, exist_ok=True)
        # per-image sibling HTML: <stem>.html  (satisfies I12: X.png -> X.html)
        page = _page_html(args.title, args.subtitle or p.name,
                          [_figure_html(p)], 1)
        out = outdir / (p.stem + ".html")
        out.write_text(page, encoding="utf-8")
        written.append(out)
        print("[OK] html : %s   (embeds %s, %d bytes)"
              % (out, p.name, p.stat().st_size))

    if args.combine and len(imgs) >= 1:
        outdir = Path(args.outdir) if args.outdir else imgs[0].parent
        outdir.mkdir(parents=True, exist_ok=True)
        figures = [_figure_html(p) for p in imgs]
        page = _page_html(args.title, args.subtitle, figures, len(imgs))
        out = outdir / (args.basename + ".html")
        out.write_text(page, encoding="utf-8")
        written.append(out)
        print("[OK] index: %s   (%d 图合并)" % (out, len(imgs)))

    print("     OneCode 只渲染 HTML；交付时以 .html 为准，裸 PNG 会被 I12 门限拦下。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
