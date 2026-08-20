#!/usr/bin/env python3
"""Genere dark_mode.svg et light_mode.svg pour le profil GitHub eRom.

L'art en blocs est rendu en <rect> (run-length encode) et non en texte :
alignement garanti quelle que soit la police du visiteur.
Le panneau droit est en ASCII pur, police mono a fallback.

Palette : design system eRom perso (OKLCH -> hex), dark-first, brand amber.
"""
import json
import math
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
ART = ROOT / "assets" / "ascii-art.txt"

# ---------------------------------------------------------------- couleurs

def oklch(L, C, H, alpha=1.0):
    """OKLCH -> hex sRGB (#rrggbb ou #rrggbbaa)."""
    h = math.radians(H)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )
    out = "#"
    for u in rgb:
        u = min(1.0, max(0.0, u))
        srgb = 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055
        out += f"{round(srgb * 255):02x}"
    if alpha < 1.0:
        out += f"{round(alpha * 255):02x}"
    return out


DARK = {
    "bg":       oklch(0.239, 0.002, 114),
    "border":   oklch(0.2805, 0.0056, 56.158),
    "fg":       oklch(0.97, 0.0017, 67.802),
    "muted":    oklch(0.7249, 0.0081, 56.28),
    "dots":     oklch(0.7249, 0.0081, 56.28, 0.35),
    "brand":    oklch(0.817, 0.1705, 77.689),
    "ok":       oklch(0.7227, 0.192, 149.579),
    "art":      oklch(0.817, 0.1705, 77.689),
}
LIGHT = {
    "bg":       oklch(1, 0, 0),
    "border":   oklch(0.9094, 0.0053, 67.757),
    "fg":       oklch(0.2161, 0.0062, 56.036),
    "muted":    oklch(0.5289, 0.0105, 56.16),
    "dots":     oklch(0.5289, 0.0105, 56.16, 0.35),
    "brand":    oklch(0.706, 0.1685, 50.8),
    "ok":       oklch(0.596, 0.145, 163.225),
    "art":      oklch(0.2161, 0.0062, 56.036),
}

# ---------------------------------------------------------------- geometrie

CELL_W, CELL_H = 5.5, 11.0          # une cellule de l'art
PAD = 26                            # marge interieure de la carte
GUTTER = 44                         # espace art <-> panneau
FS = 13                             # font-size du panneau
LH = 20                             # interligne du panneau
CH = FS * 0.60                      # largeur d'un caractere mono (Menlo/SF Mono)
COLS = 55                           # largeur du panneau en caracteres
ART_BOX_W, ART_BOX_H = 400, 470     # boite cible de l'art

LEVELS = {"░": 0.18, "▒": 0.45, "▓": 0.78, "█": 1.0}

# ---------------------------------------------------------------- donnees

STATS = {
    "repos": "59",
    "contrib": "110",
    "commits": "3 257",
    "since": "30 octobre 2009",
}
JOINED = date(2009, 10, 30)


def uptime(start, today=None):
    today = today or date.today()
    y = today.year - start.year
    m = today.month - start.month
    d = today.day - start.day
    if d < 0:
        m -= 1
        prev = (today.replace(day=1) - date.resolution)
        d += prev.day
    if m < 0:
        y -= 1
        m += 12
    return f"{y} ans, {m} mois, {d} jours"


def rows():
    """(kind, *args) : title | sub | section | kv | gap."""
    return [
        ("title", "romain@erom"),
        ("sub", "Passeur du Numérique et Architecte du Simple"),
        ("gap",),
        ("section", "Système"),
        ("kv", "OS", "macOS (Darwin 25.5)", "fg", None),
        ("kv", "Uptime", uptime(JOINED), "fg", "uptime_data"),
        ("kv", "Host", "Nantes, France", "fg", None),
        ("kv", "Shell", "zsh + Claude Code", "fg", None),
        ("kv", "Statut", "Disponible", "ok", None),
        ("gap",),
        ("section", "Langages"),
        ("kv", "Programmation", "TypeScript, Python, Rust", "fg", None),
        ("kv", "Runtimes", "bun, uv", "fg", None),
        ("kv", "Humaines", "Français, Anglais", "fg", None),
        ("gap",),
        ("section", "Contact"),
        ("kv", "Web", "romain-ecarnot.com", "fg", None),
        ("kv", "Email", "romain.ecarnot@gmail.com", "fg", None),
        ("kv", "GitHub", "@eRom", "fg", None),
        ("gap",),
        ("section", "Stats"),
        ("kv", "Dépôts publics", STATS["repos"] + "  { contribués : " + STATS["contrib"] + " }", "fg", "repo_data"),
        ("kv", "Commits (12 mois)", STATS["commits"], "fg", "commit_data"),
        ("kv", "Membre depuis", STATS["since"], "fg", None),
    ]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- rendu

def art_style(style, palette):
    """Couleur par niveau de bloc : (fill, opacity_multiplier)."""
    if style == "amber":
        return {c: (palette["art"], o) for c, o in LEVELS.items()}
    if style == "neutre":
        return {c: (palette["fg"], o) for c, o in LEVELS.items()}
    # mixte : le fond reste neutre, le sujet emerge en amber
    return {
        "░": (palette["muted"], 0.22),
        "▒": (palette["muted"], 0.55),
        "▓": (palette["art"], 0.72),
        "█": (palette["art"], 1.0),
    }


def art_rects(lines, color, cw, cellh):
    """Run-length encode horizontal -> <rect> par run de meme niveau."""
    out = []
    for y, line in enumerate(lines):
        x = 0
        while x < len(line):
            ch = line[x]
            if ch not in LEVELS:
                x += 1
                continue
            run = 1
            while x + run < len(line) and line[x + run] == ch:
                run += 1
            fill, op = color[ch]
            out.append(
                '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" opacity="%s"/>'
                % (
                    fmt(x * cw), fmt(y * cellh),
                    fmt(run * cw), fmt(cellh),
                    fill, op,
                )
            )
            x += run
    return out


def fmt(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def crop(lines):
    """Retire les lignes et colonnes entierement vides autour de l'art."""
    keep = [i for i, l in enumerate(lines) if l.strip()]
    lines = lines[keep[0]:keep[-1] + 1]
    width = max(len(l) for l in lines)
    lines = [l.ljust(width) for l in lines]
    cols = [c for c in range(width) if any(l[c] != " " for l in lines)]
    lo, hi = cols[0], cols[-1] + 1
    return [l[lo:hi] for l in lines]


def build(theme, palette, style="amber", suffix=""):
    lines = crop(ART.read_text(encoding="utf-8").rstrip("\n").split("\n"))
    art_cols, art_rows = max(len(l) for l in lines), len(lines)
    # echelle : l'art remplit la boite cible sans deformer le ratio 1:2 des cellules
    k = min(ART_BOX_W / (art_cols * CELL_W), ART_BOX_H / (art_rows * CELL_H))
    cw, chh = CELL_W * k, CELL_H * k
    art_w = art_cols * cw
    art_h = art_rows * chh

    body = rows()
    panel_w = COLS * CH
    panel_h = sum(LH for r in body if r[0] != "gap") + sum(LH * 0.5 for r in body if r[0] == "gap") + LH * 0.6

    width = PAD * 2 + art_w + GUTTER + panel_w
    height = PAD * 2 + max(art_h, panel_h)

    px = PAD + art_w + GUTTER
    art_y = PAD + (height - PAD * 2 - art_h) / 2

    svg = []
    svg.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%spx" height="%spx" '
        'viewBox="0 0 %s %s" font-family="\'JetBrains Mono\',\'SFMono-Regular\','
        'Menlo,Consolas,\'Liberation Mono\',monospace" font-size="%spx">'
        % (fmt(width), fmt(height), fmt(width), fmt(height), FS)
    )
    svg.append(
        "<style>text,tspan{white-space:pre}"
        ".k{fill:%s}.v{fill:%s}.d{fill:%s}.m{fill:%s}.s{fill:%s}.ok{fill:%s}</style>"
        % (palette["brand"], palette["fg"], palette["dots"], palette["muted"],
           palette["brand"], palette["ok"])
    )
    svg.append(
        '<rect width="%s" height="%s" rx="14" fill="%s" stroke="%s"/>'
        % (fmt(width), fmt(height), palette["bg"], palette["border"])
    )

    svg.append('<g transform="translate(%s,%s)">' % (fmt(PAD), fmt(art_y)))
    svg.extend(art_rects(lines, art_style(style, palette), cw, chh))
    svg.append("</g>")

    y = PAD + LH * 0.9
    for row in body:
        kind = row[0]
        if kind == "gap":
            y += LH * 0.5
            continue
        if kind == "title":
            svg.append(
                '<text x="%s" y="%s" class="s" font-size="%spx" font-weight="700">%s</text>'
                % (fmt(px), fmt(y), fmt(FS * 1.35), esc(row[1]))
            )
            y += LH
            continue
        if kind == "sub":
            svg.append(
                '<text x="%s" y="%s" class="m" font-size="%spx">%s</text>'
                % (fmt(px), fmt(y), fmt(FS * 0.92), esc(row[1]))
            )
            y += LH
            continue
        if kind == "section":
            label = esc(row[1])
            svg.append(
                '<text x="%s" y="%s" class="s" font-size="%spx" font-weight="700" '
                'letter-spacing="1.2">%s</text>' % (fmt(px), fmt(y), fmt(FS * 0.8), label.upper())
            )
            lx = px + (len(label) + 1) * (CH * 0.82) + 8
            svg.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
                % (fmt(lx), fmt(y - FS * 0.28), fmt(px + panel_w), fmt(y - FS * 0.28), palette["border"])
            )
            y += LH
            continue
        _, key, val, tone, ident = row
        fill = int(COLS - len(key) - len(val) - 4)
        dots = "." * max(fill, 2)
        idattr = ' id="%s"' % ident if ident else ""
        svg.append(
            '<text x="%s" y="%s"><tspan class="k">%s</tspan>'
            '<tspan class="d"> %s </tspan>'
            '<tspan class="%s"%s>%s</tspan></text>'
            % (fmt(px), fmt(y), esc(key) + " :", dots,
               "v" if tone == "fg" else "ok", idattr, esc(val))
        )
        y += LH

    svg.append("</svg>")
    out = ROOT / ("%s%s.svg" % (theme, suffix))
    out.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print("%s  %sx%s  %d rects" % (out.name, fmt(width), fmt(height),
                                   sum(1 for s in svg if s.startswith("<rect x="))))


import sys
STYLE = sys.argv[1] if len(sys.argv) > 1 else "neutre"
SUFFIX = sys.argv[2] if len(sys.argv) > 2 else ""
# un seul rendu : l'art est concu pour un fond sombre, la carte reste un terminal
# dans les deux themes GitHub.
build("profile", DARK, STYLE, SUFFIX)
