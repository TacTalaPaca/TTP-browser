#!/usr/bin/env python3
# Patch product brand inside browser/omni.ja.
# Usage: patch-omni-branding.py ROOT BUILD
import base64
import io
from pathlib import Path

from PIL import Image

from omnijar import extract, replace, require_paths

ROOT, BUILD = require_paths()
MASTER = ROOT / "assets/icons" / "firegila-2048.png"
OMNI = BUILD / "browser" / "omni.ja"
WORK = BUILD / "omni-work"

BRAND_DIR = Path("chrome/browser/content/branding")

BRAND_FTL = """-brand-shorter-name = Firegila
-brand-short-name = Firegila
-brand-shortcut-name = Firegila
-brand-full-name = Firegila
-brand-product-name = Firegila
-vendor-short-name = Firegila
trademarkInfo = Firegila is based on Firefox ESR.
"""

BRAND_PROPERTIES = """brandShorterName=Firegila
brandShortName=Firegila
brandFullName=Firegila
vendorShortName=Firegila
"""

WORDMARK_SVG = """<!-- This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at http://mozilla.org/MPL/2.0/. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 359 80">
  <text x="179.5" y="57" text-anchor="middle" font-family="sans-serif" font-size="52" font-weight="bold" fill="context-fill">Firegila</text>
</svg>
"""


def png_bytes(img, size):
    buf = io.BytesIO()
    img.resize((size, size), Image.LANCZOS).save(buf, "PNG", optimize=True)
    return buf.getvalue()


def main():
    extract(OMNI, WORK, "omni")
    if not (WORK / "localization/en-US/branding/brand.ftl").exists():
        raise SystemExit("omni: extract failed")

    (WORK / "localization/en-US/branding/brand.ftl").write_text(BRAND_FTL)
    (WORK / "chrome/en-US/locale/branding/brand.properties").write_text(BRAND_PROPERTIES)

    master = Image.open(MASTER).convert("RGBA")
    bdir = WORK / BRAND_DIR
    for s in (16, 32, 48, 64, 128):
        (bdir / f"icon{s}.png").write_bytes(png_bytes(master, s))
    (bdir / "about-logo.png").write_bytes(png_bytes(master, 192))
    (bdir / "about-logo@2x.png").write_bytes(png_bytes(master, 384))
    (bdir / "about-logo-private.png").write_bytes(png_bytes(master, 192))
    (bdir / "about-logo-private@2x.png").write_bytes(png_bytes(master, 384))

    raw512 = png_bytes(master, 512)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">'
        '<image width="512" height="512" href="data:image/png;base64,'
        + base64.b64encode(raw512).decode()
        + '"/></svg>'
    )
    (bdir / "about-logo.svg").write_text(svg)
    (bdir / "about-wordmark.svg").write_text(WORDMARK_SVG)
    (bdir / "firefox-wordmark.svg").write_text(WORDMARK_SVG)
    master.resize((256, 256), Image.LANCZOS).save(
        bdir / "document.ico", sizes=[(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]
    )

    replace(OMNI, WORK)
    print("omni: brand patched")


main()
