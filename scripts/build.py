#!/usr/bin/env python3
"""Builds the README banner (light and dark) into assets/.

The name is shaped with HarfBuzz and converted to outlines, so it renders the
same everywhere without web fonts (GitHub blocks them inside <img>). The
background is transparent so it sits cleanly on every GitHub theme.

Setup:  pip install fonttools uharfbuzz
Run:    python scripts/build.py      (downloads the OFL fonts into .cache/ once)
"""
import io
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
CACHE = ROOT / ".cache" / "fonts"
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl"
FONTS = {
    "ArchivoBlack.ttf": f"{GF}/archivoblack/ArchivoBlack-Regular.ttf",
    "Geist.ttf": f"{GF}/geist/Geist%5Bwght%5D.ttf",
}

NAME, HANDLE = "OMKAR RANE", "@Hackmaass"
THEMES = {  # GitHub's own palette so the banner matches the page it sits on
    "light": {"fg": "#1F2328", "muted": "#59636E", "accent": "#0969DA"},
    "dark": {"fg": "#E6EDF3", "muted": "#8B949E", "accent": "#4493F8"},
}


class Font:
    def __init__(self, tag, path, axes=None):
        tt = TTFont(path)
        if axes:
            tt = instancer.instantiateVariableFont(tt, axes)
        buf = io.BytesIO()
        tt.save(buf)
        data = buf.getvalue()
        self.tag = tag
        self.tt = TTFont(io.BytesIO(data))
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(data))

    def shape(self, text, tracking=0.0):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        glyphs, x = [], 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            glyphs.append((info.codepoint, x + pos.x_offset, pos.y_offset))
            x += pos.x_advance + tracking * self.upem
        return glyphs, x

    def width(self, text, size, tracking=0.0):
        glyphs, adv = self.shape(text, tracking)
        return (adv - tracking * self.upem) * size / self.upem


def banner(name, display, ui, theme):
    W, H, SIZE = 1200, 190, 128
    defs, body = {}, []

    def text(font, s, x, y, size, fill, tracking=0.0):
        glyphs, _ = font.shape(s, tracking)
        scale = size / font.upem
        uses = []
        for gid, gx, gy in glyphs:
            key = f"{font.tag}{gid}"
            if key not in defs:
                pen = SVGPathPen(font.gs)
                font.gs[font.order[gid]].draw(pen)
                defs[key] = pen.getCommands()
            if defs[key]:
                uses.append(f'<use xlink:href="#{key}" x="{gx:g}" y="{gy:g}"/>')
        body.append(f'<g transform="translate({x:.2f} {y:.2f}) scale({scale:.5f} {-scale:.5f})" fill="{fill}">{"".join(uses)}</g>')

    c = THEMES[theme]
    base = 158
    body.append(f'<rect x="0" y="20" width="56" height="6" fill="{c["accent"]}"/>')
    text(display, name, -4, base, SIZE, c["fg"], tracking=-0.01)
    text(ui, HANDLE, W - ui.width(HANDLE, 30), base, 30, c["muted"])
    d = "".join(f'<path id="{k}" d="{v}"/>' for k, v in defs.items() if v)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"><title>Omkar Rane</title>'
           f'<defs>{d}</defs>{"".join(body)}</svg>')
    OUT.mkdir(exist_ok=True)
    (OUT / f"banner-{theme}.svg").write_text(svg, encoding="utf-8")
    root = ET.fromstring(svg)  # well-formed XML, or this raises
    assert "<text" not in svg and root.get("width") == str(W) and root.get("height") == str(H)
    assert display.width(name, SIZE, -0.01) < W - ui.width(HANDLE, 30) - 40, "name collides with handle"


if __name__ == "__main__":
    CACHE.mkdir(parents=True, exist_ok=True)
    for fname, url in FONTS.items():
        if not (CACHE / fname).exists():
            urllib.request.urlretrieve(url, CACHE / fname)
    display = Font("d", CACHE / "ArchivoBlack.ttf")
    ui = Font("u", CACHE / "Geist.ttf", {"wght": 500})
    for theme in THEMES:
        banner(NAME, display, ui, theme)
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
