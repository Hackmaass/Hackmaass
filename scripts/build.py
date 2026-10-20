#!/usr/bin/env python3
"""Builds the profile's poster SVGs into assets/.

All type is shaped with HarfBuzz and converted to outlines, so the images look
identical on every device and need no web fonts (GitHub blocks them in <img>).

Setup:  pip install fonttools uharfbuzz
Run:    python scripts/build.py      (downloads the OFL fonts into .cache/ once)
Edit PROJECTS / TICKER / STACK below to change the content.
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
    "ArchivoBlack-Regular.ttf": f"{GF}/archivoblack/ArchivoBlack-Regular.ttf",
    "IBMPlexSans.ttf": f"{GF}/ibmplexsans/IBMPlexSans%5Bwdth%2Cwght%5D.ttf",
}

# Palette: ultramarine field, chalk paper, ink text, flare for signal, haze for secondary.
BLUE, CHALK, INK, FLARE, HAZE = "#2B3BFF", "#F4F6FF", "#0B1033", "#FF5B2E", "#B9C2FF"

TICKER = ["Graph Hacks", "Monad Blitz Pune V3", "Vortexa 3.0", "MST × Newrro Buildathon",
          "AWS Bharat Builds", "Flytbase", "Virtual Prompt Wars 3"]

# name, event line, description (keep to 3 lines), tags, live (bool), file slug
PROJECTS = [
    ("Chokepoint", "Graph Hacks, Oct 2026",
     "An investigation agent on FalkorDB that finds the few accounts to freeze so no route for stolen money is left.",
     ["Python", "FalkorDB", "Agents"], True, "chokepoint"),
    ("Sublevel", "Monad Blitz Pune V3",
     "A card duel on Monad: both fighters seal a move in secret, and a contract resolves the turn.",
     ["Solidity", "Monad testnet", "ERC-721"], True, "sublevel"),
    ("Sealstone", "Vortexa 3.0, Team Torvalds",
     "Milestone escrow built to resist ambiguous terms, swapped deliverables and malicious contracts.",
     ["TypeScript", "Solidity", "MST testnet"], True, "sealstone"),
    ("TamperSafe", "MST × Newrro 24-hour buildathon",
     "A tamper-evident container that locks at origin, watches itself in transit and settles payment on-chain.",
     ["Solidity", "ESP32", "MST testnet"], True, "tampersafe"),
    ("Diskman", "Open source",
     "A Windows storage visualizer and cache cleaner in native PowerShell and WPF, with no external runtimes.",
     ["PowerShell", "WPF", "36 cleanup targets"], False, "diskman"),
    ("Ada", "TalentGraph AI platform",
     "Evidence-driven hiring: ADA, a multi-agent assistant, reasons over a candidate's real work, not their resume.",
     ["TypeScript", "Python", "Multi-agent"], True, "ada"),
]

STACK = [
    ("Agents and data", "Python, RAG, multi-agent systems, FalkorDB, FastAPI, OpenCV, TensorFlow"),
    ("Chains", "Solidity, Monad, MST Blockchain, ERC-721, testnet deployments"),
    ("Web", "TypeScript, Next.js, React, Tailwind, Node.js, Three.js, Firebase, MongoDB"),
    ("Systems and tools", "C, C++, PowerShell, Bash, Linux, Docker, Git, ESP32, Arduino"),
]


def fetch_fonts():
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, url in FONTS.items():
        if not (CACHE / name).exists():
            urllib.request.urlretrieve(url, CACHE / name)


class Font:
    def __init__(self, fid, path, axes=None):
        tt = TTFont(path)
        if axes:
            tt = instancer.instantiateVariableFont(tt, axes)
        buf = io.BytesIO()
        tt.save(buf)
        data = buf.getvalue()
        self.id = fid
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
        return self.shape(text, tracking)[1] * size / self.upem

    def fit(self, text, max_size, max_width):
        return min(max_size, max_width / (self.shape(text)[1] / self.upem))

    def wrap(self, text, size, max_width):
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if cur and self.width(trial, size) > max_width:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        return lines + [cur]


class Svg:
    def __init__(self, w, h, title, desc, css=""):
        self.w, self.h, self.title, self.desc, self.css = w, h, title, desc, css
        self.defs, self.body = {}, []

    def add(self, markup):
        self.body.append(markup)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=0, rx=0, extra=""):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{extra}/>')

    def text(self, font, s, x, y, size, fill, anchor="start", tracking=0.0):
        glyphs, adv = font.shape(s, tracking)
        scale = size / font.upem
        width = adv * scale
        x -= {"start": 0, "middle": width / 2, "end": width}[anchor]
        uses = []
        for gid, gx, gy in glyphs:
            key = f"{font.id}{gid}"
            if key not in self.defs:
                pen = SVGPathPen(font.gs)
                font.gs[font.order[gid]].draw(pen)
                self.defs[key] = pen.getCommands()
            if self.defs[key]:
                uses.append(f'<use xlink:href="#{key}" x="{gx:g}" y="{gy:g}"/>')
        self.add(f'<g transform="translate({x:.2f} {y:.2f}) scale({scale:.5f} {-scale:.5f})" fill="{fill}">{"".join(uses)}</g>')
        return width

    def save(self, name):
        defs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in self.defs.items() if d)
        style = f"<style>{self.css}</style>" if self.css else ""
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img">'
               f'<title>{esc(self.title)}</title><desc>{esc(self.desc)}</desc>{style}<defs>{defs}</defs>'
               f'{"".join(self.body)}</svg>')
        OUT.mkdir(exist_ok=True)
        (OUT / name).write_text(svg, encoding="utf-8")
        root = ET.fromstring(svg)  # well-formed XML, or this raises
        assert "<text" not in svg, f"{name}: leftover live text"
        assert root.get("width") == str(self.w) and root.get("height") == str(self.h), name


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def hero(display, body):
    W, H, M = 1200, 620, 56
    pitch = (W - 2 * M) * 0.80  # OMKAR spans 80% of the poster width
    size = display.fit("OMKAR", 400, pitch)
    cap = size * 0.70
    y1 = 130 + cap
    y2 = y1 + cap + 30
    ticker_w = sum(display.width(t, 34) + 56 for t in TICKER)
    css = (f".tk{{animation:tk {ticker_w / 55:.0f}s linear infinite}}"
           f"@keyframes tk{{to{{transform:translateX(-{ticker_w:.2f}px)}}}}"
           "@media (prefers-reduced-motion:reduce){.tk{animation:none}}")
    s = Svg(W, H, "Omkar Rane",
            "Omkar Rane builds agents, smart contracts and dev tools at hackathons, then ships them live. "
            "Built at: " + ", ".join(TICKER) + ".", css)
    s.rect(0, 0, W, H, BLUE)
    s.add(f'<circle cx="{M + 8}" cy="68" r="8" fill="{FLARE}"/>')
    s.text(body, "@Hackmaass", M + 28, 76, 26, HAZE)
    s.text(display, "OMKAR", M, y1, size, CHALK)
    s.text(display, "RANE", M, y2, size, CHALK)
    # sticker, top right
    cx, cy = W - 142, 198
    s.add(f'<g transform="rotate(-12 {cx} {cy})"><circle cx="{cx}" cy="{cy}" r="86" fill="{FLARE}"/>')
    s.text(display, "Ships", cx, cy - 4, 46, INK, "middle")
    s.text(display, "live", cx, cy + 44, 46, INK, "middle")
    s.add("</g>")
    # statement beside RANE
    x0 = M + display.width("RANE", size) + 44
    lines = body.wrap("I build agents, smart contracts and dev tools at hackathons, then ship them live.",
                      28, W - M - x0)
    for i, ln in enumerate(lines):
        s.text(body, ln, x0, y2 - (len(lines) - 1 - i) * 38, 28, CHALK)
    # ticker
    ty = H - 84
    s.rect(0, ty, W, 84, CHALK)
    items = []
    x = 0.0
    for t in TICKER:
        items.append((t, x))
        x += display.width(t, 34) + 56
    s.add('<g class="tk">')
    for copy in (0, 1):
        for t, tx in items:
            s.text(display, t, copy * ticker_w + tx + 190, ty + 54, 34, INK)
            s.rect(copy * ticker_w + tx + 190 + display.width(t, 34) + 21, ty + 34, 14, 14, BLUE)
    s.add("</g>")
    s.rect(0, ty, 168, 84, FLARE)
    s.text(display, "Built at", 84, ty + 54, 34, INK, "middle")
    s.save("hero.svg")


def card(display, body, p):
    name, event, desc, tags, live, slug = p
    W, H, LP, PAD = 880, 260, 296, 28
    s = Svg(W, H, name, f"{name}. {event}. {desc} " + ("Live demo available." if live else "Source only."))
    s.rect(0, 0, W, H, CHALK)
    s.rect(0, 0, LP, H, BLUE)
    s.text(display, name, PAD, 98, display.fit(name, 54, LP - 2 * PAD), CHALK)
    for i, ln in enumerate(body.wrap(event, 21, LP - 2 * PAD)):
        s.text(body, ln, PAD, 140 + i * 28, 21, HAZE)
    s.add(f'<circle cx="{PAD + 7}" cy="{H - 46}" r="7" fill="{FLARE if live else "none"}" stroke="{FLARE}" stroke-width="2.5"/>')
    s.text(body, "Live demo" if live else "Source on GitHub", PAD + 24, H - 38, 21, CHALK)
    lines = body.wrap(desc, 27, W - LP - 2 * PAD)
    assert len(lines) <= 3, f"{name}: description needs {len(lines)} lines"
    for i, ln in enumerate(lines):
        s.text(body, ln, LP + PAD, 76 + i * 38, 27, INK)
    x = LP + PAD
    for t in tags:
        w = body.width(t, 20) + 28
        s.rect(x, H - 72, w, 40, "none", BLUE, 2, 20)
        s.text(body, t, x + 14, H - 45, 20, BLUE)
        x += w + 10
    s.rect(1.5, 1.5, W - 3, H - 3, "none", BLUE, 3)
    s.save(f"{slug}.svg")


def stack(display, body):
    W, RH, LP, PAD = 880, 92, 290, 28
    s = Svg(W, RH * len(STACK), "Toolbelt", "; ".join(f"{a}: {b}" for a, b in STACK))
    s.rect(0, 0, W, s.h, CHALK)
    lsize = min(display.fit(label, 30, LP - PAD - 16) for label, _ in STACK)  # one size for every label
    for i, (label, items) in enumerate(STACK):
        y = i * RH
        if i:
            s.rect(PAD, y, W - 2 * PAD, 2, HAZE)
        s.text(display, label, PAD, y + RH / 2 + 12, lsize, BLUE)
        lines = body.wrap(items, 23, W - LP - PAD)
        for j, ln in enumerate(lines):
            s.text(body, ln, LP, y + RH / 2 + 8 - (len(lines) - 1) * 15 + j * 30, 23, INK)
    s.rect(1.5, 1.5, W - 3, s.h - 3, "none", BLUE, 3)
    s.save("stack.svg")


def closer(display, body):
    W, H = 880, 190
    s = Svg(W, H, "Building something?", "Building something? Let's talk.")
    s.rect(0, 0, W, H, BLUE)
    s.text(display, "Building something?", 40, 92, display.fit("Building something?", 64, W - 80), CHALK)
    s.text(display, "Let's talk.", 40, 150, 44, FLARE)
    s.save("closer.svg")


if __name__ == "__main__":
    fetch_fonts()
    display = Font("d", CACHE / "ArchivoBlack-Regular.ttf")
    body = Font("b", CACHE / "IBMPlexSans.ttf", {"wght": 500, "wdth": 100})
    hero(display, body)
    for p in PROJECTS:
        card(display, body, p)
    stack(display, body)
    closer(display, body)
    print("wrote", len(list(OUT.glob("*.svg"))), "svgs to", OUT)
