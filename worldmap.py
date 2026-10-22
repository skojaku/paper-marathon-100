"""The stage at the top of every page: a side-scrolling level drawn like a pen sketch on the
paper (nothing is filled, so the washi shows through). One coin per paper, a block every ten,
pipes and pits to jump, a flag and a castle at the end; a stick-figure runner collects a coin
for every paper read. Geometry is computed here; assets/map.js moves the runner."""
import html
import json
import math
import random

W, H = 960, 176
G = 140            # ground line (the runner's feet)
INK = "#26231f"
X0, X1 = 56, 852   # stop 0 and stop 100
RES = 4            # points per stop in the runner's path (smooth jumps)

PIPES = [(185, 32), (470, 48), (745, 32)]   # centre x, height
PITS = [330, 610]                           # centre x (44 wide)
PEN = f'fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
THIN = f'fill="none" stroke="{INK}" stroke-width="1.4" stroke-linecap="round"'


def stop_x(s):
    return X0 + (X1 - X0) * s / 100


def feet_y(x):
    """Height of the runner's feet at x: on the ground, or an arc over a pipe or a pit."""
    lift = 0.0
    for xc, h in PIPES:
        if abs(x - xc) < 44:
            lift = max(lift, (h + 6) / 0.8 * math.sin(math.pi * (x - xc + 44) / 88))
    for xc in PITS:
        if abs(x - xc) < 42:
            lift = max(lift, 26 * math.sin(math.pi * (x - xc + 42) / 84))
    return G - lift


def _cloud(x, y, s):
    return (f'<path transform="translate({x},{y}) scale({s})" {PEN} d="M0,14 a7,7 0 0 1 4,-12 a9,9 0 0 1 16,-3 '
            f'a8,8 0 0 1 14,5 a6,6 0 0 1 2,10 Z"/>')


def _hill(cx, rx, ry, eyes=True):
    out = f'<path {PEN} d="M{cx - rx},{G} A{rx},{ry} 0 0 1 {cx + rx},{G}"/>'
    if eyes:
        ey = G - ry * 0.55
        out += f'<path {PEN} d="M{cx - 8},{ey:.0f} v8 M{cx + 6},{ey:.0f} v8"/>'
    return out


def _scene():
    rng = random.Random(64)
    s = []
    for x, y, sc in [(62, 52, 1.2), (236, 48, 1.0), (380, 52, 1.0), (520, 44, 1.0), (655, 50, 1.0), (800, 50, 1.2)]:
        s.append(_cloud(x, y, sc))
    for cx, rx, ry in [(80, 52, 40), (262, 40, 30), (540, 36, 44), (680, 40, 34), (822, 34, 26)]:
        s.append(_hill(cx, rx, ry, eyes=rx > 36))
    # ground line with pits, hatched earth under it
    edges = [0] + [v for p in PITS for v in (p - 22, p + 22)] + [960]
    for a, b in zip(edges[::2], edges[1::2]):
        s.append(f'<path {PEN} d="M{a},{G} L{b},{G}"/>')
        for row, y in enumerate((G + 11, G + 24)):
            x = a + 6 + row * 7
            while x < b - 6:
                s.append(f'<path d="M{x:.0f},{y + rng.uniform(-1, 1):.0f} l5,-6" {THIN} opacity=".65"/>')
                x += rng.uniform(13, 18)
    for p in PITS:
        for sx in (p - 22, p + 22):
            s.append(f'<path {PEN} d="M{sx},{G} L{sx},{H - 4}"/>')
    # pipes
    for xc, h in PIPES:
        s.append(f'<path {PEN} d="M{xc - 14},{G} V{G - h + 12} M{xc + 14},{G} V{G - h + 12}"/>'
                 f'<rect {PEN} x="{xc - 18}" y="{G - h}" width="36" height="12" rx="2"/>'
                 f'<path d="M{xc - 8},{G - h + 18} v{h - 24}" {THIN} opacity=".6"/>')
    # flag pole and castle
    px = 898
    s.append(f'<path {PEN} d="M{px},{G} V58"/><circle {PEN} cx="{px}" cy="53" r="3.5"/>'
             f'<g class="flag"><path {PEN} fill="{INK}" d="M{px},64 l-24,8 l24,8 Z"/></g>')
    cx = 926
    s.append(f'<path {PEN} d="M{cx},{G} V{G - 34} h5 v-6 h5 v6 h4 v-6 h5 v6 h4 v-6 h5 v6 h6 V{G}"/>'
             f'<path {PEN} d="M{cx + 12},{G} v-12 a5,5 0 0 1 10,0 v12"/>')
    return "".join(s)


def _runner(frame):
    """A stick figure, feet at (0, 0), facing right. a: stride, b: legs together (also the jump)."""
    if frame == "a":
        legs, arms = "M0,-14 L-6,-7 L-10,0 M0,-14 L7,-8 L4,0", "M1,-25 L-6,-19 L-9,-22 M1,-25 L8,-21 L12,-24"
        hide = ""
    else:
        legs, arms = "M0,-14 L-2,-7 L-2,0 M0,-14 L3,-8 L2,0", "M1,-25 L-5,-27 L-8,-31 M1,-25 L7,-26 L10,-30"
        hide = ' style="display:none"'
    return (f'<g class="f{frame}"{hide}>'
            f'<circle {PEN} cx="3" cy="-34" r="5.5"/>'
            f'<path {PEN} d="M1,-28.5 L0,-14 {legs} {arms}"/>'
            f'<path {PEN} stroke-width="1.6" d="M-3,-36 L-10,-35 M-3,-33.5 L-9,-31"/>'   # headband tails
            f'<circle cx="5.2" cy="-35" r="1" fill="{INK}"/></g>')


def render(read, root=""):
    """`read`: list of (paper title, week slug), in reading order."""
    n = min(len(read), 100)
    pts = []
    for k in range(100 * RES + 1):
        x = stop_x(k / RES)
        pts.append([round(x, 1), round(feet_y(x), 1)])
    out = []
    for i in range(1, 101):
        x = stop_x(i)
        cy = max(40, feet_y(x) - 58)
        got = " got" if i <= n else ""
        use = f'<use href="#coin" class="coin{got}" data-i="{i}" x="{x - 3.5:.1f}" y="{cy - 5:.1f}"/>'
        if i <= len(read):
            tip = html.escape(f"{i}. {read[i - 1][0]}")
            out.append(f'<a href="{root}weeks/{read[i - 1][1]}.html"><title>{tip}</title>{use}</a>')
        else:
            out.append(use)
        if i % 10 == 0 and i < 100:
            used = " used" if i <= n else ""
            out.append(f'<g class="block{used}" data-i="{i}"><rect x="{x - 11:.1f}" y="12" width="22" height="22" rx="2"/>'
                       f'<path class="hatch" d="M{x - 8:.1f},31 l16,-16 M{x - 8:.1f},25 l10,-10 M{x - 2:.1f},31 l10,-10"/>'
                       f'<text x="{x:.1f}" y="28.5" text-anchor="middle">{i}</text></g>')
    runner = f'<g class="runner" aria-hidden="true">{_runner("a")}{_runner("b")}</g>'
    data = html.escape(json.dumps(pts, separators=(",", ":")))
    defs = ('<defs><filter id="rough" x="-2%" y="-5%" width="104%" height="110%">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="5" result="n"/>'
            '<feDisplacementMap in="SourceGraphic" in2="n" scale="3"/></filter>'
            f'<symbol id="coin" viewBox="0 0 7 10" width="7" height="10"><ellipse cx="3.5" cy="5" rx="2.7" ry="4.1" {PEN} stroke-width="1.2"/>'
            f'<path d="M3.5,2.6 v4.8" fill="none" stroke="{INK}" stroke-width="1" stroke-linecap="round"/></symbol></defs>')
    return (f'<div class="world" data-n="{n}" data-res="{RES}" data-points="{data}" role="img" aria-label="{n} of 100 papers read">'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{defs}'
            f'<g filter="url(#rough)">{_scene()}{"".join(out)}{runner}</g></svg></div>')
