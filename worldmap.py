"""The stage at the top of every page: a side-scrolling, pixel-art level. One coin per paper,
a block every ten, pipes and pits to jump, a flag and a castle at the end. The runner collects
a coin for every paper read. Geometry is computed here; assets/map.js moves the runner."""
import html
import json
import math

W, H = 960, 176
G = 140            # ground line (the runner's feet)
PX = 3             # one runner pixel in stage units
INK = "#1c1c1c"
X0, X1 = 56, 852   # stop 0 and stop 100
RES = 4            # points per stop in the runner's path (smooth jumps)

PIPES = [(185, 32), (470, 48), (745, 32)]   # centre x, height
PITS = [330, 610]                           # centre x (44 wide)

PALETTE = {"K": INK, "W": "#f5f5f5", "D": "#4a4a4a"}
BODY = ["...KK..KK...", "..KKKKKKKK..", ".KKKKKKKKKK.", ".KKWWWWWWKK.", ".KWWWWWWWWK.", ".KWKKWWKKWK.",
        ".KWWWWWWWWK.", "..KWWWWWWK..", "..KDDDDDDK..", ".KDDWDDWDDK.", ".KDDDDDDDDK.", "..KDDDDDDK.."]
LEGS_A = ["..KK....KK..", ".KWK....KWK."]
LEGS_B = ["...KKKKKK...", "..KWK..KWK.."]

COIN = ["..KK..", ".KYYK.", "KYYWYK", "KYWYYK", "KYWYYK", "KYYYYK", ".KYYK.", "..KK.."]
COIN_COLORS = {"K": "#2b2b2b", "Y": "#c9c9c9", "W": "#ffffff"}
CLOUD = ["...XXXX......", "..XXXXXXX.XX.", ".XXXXXXXXXXXX", "XXXXXXXXXXXXX", ".XXXXXXXXXXX."]


def _rects(rows, colors, unit, ox=0, oy=0):
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                out.append(f'<rect x="{ox + x * unit}" y="{oy + y * unit}" width="{unit}" height="{unit}" fill="{colors[ch]}"/>')
    return "".join(out)


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


def _hill(cx, rx, ry, body, rim, eyes=True):
    out = []
    for x in range(int(cx - rx), int(cx + rx), 4):
        t = 1 - ((x + 2 - cx) / rx) ** 2
        if t <= 0:
            continue
        h = int(ry * math.sqrt(t) / 4) * 4
        if h <= 0:
            continue
        out.append(f'<rect x="{x}" y="{G - h}" width="4" height="{h}" fill="{body}"/>'
                   f'<rect x="{x}" y="{G - h}" width="4" height="4" fill="{rim}"/>')
    if eyes:
        ey = G - ry * 0.62
        out.append(f'<rect x="{cx - 10:.0f}" y="{ey:.0f}" width="4" height="10" fill="{rim}"/>'
                   f'<rect x="{cx + 6:.0f}" y="{ey:.0f}" width="4" height="10" fill="{rim}"/>')
    return "".join(out)


def _scene():
    s = ['<rect width="960" height="176" fill="#ececec"/>']
    for cx, cy, sc in [(96, 46, 4), (292, 58, 3), (560, 40, 4), (820, 56, 3)]:
        s.append(_rects(CLOUD, {"X": "#fdfbf7"}, sc, cx, cy))
    for cx, rx, ry in [(110, 70, 48), (420, 92, 60), (690, 62, 40)]:
        s.append(_hill(cx, rx, ry, "#c4c4c4", "#8a8a8a"))
    for cx, rx, ry in [(250, 30, 16), (560, 34, 18), (835, 28, 14)]:
        s.append(_hill(cx, rx, ry, "#d6d6d6", "#a3a3a3", eyes=False))
    # ground with pits
    edges = [0] + [v for p in PITS for v in (p - 22, p + 22)] + [960]
    for a, b in zip(edges[::2], edges[1::2]):
        s.append(f'<rect x="{a}" y="{G}" width="{b - a}" height="{H - G}" fill="url(#brick)"/>'
                 f'<rect x="{a}" y="{G}" width="{b - a}" height="3" fill="#e2e2e2"/>')
    # pipes
    for xc, h in PIPES:
        s.append(f'<rect x="{xc - 14}" y="{G - h}" width="28" height="{h}" fill="#8f8f8f" stroke="{INK}" stroke-width="1.6"/>'
                 f'<rect x="{xc - 18}" y="{G - h}" width="36" height="12" fill="#a9a9a9" stroke="{INK}" stroke-width="1.6"/>'
                 f'<rect x="{xc - 10}" y="{G - h + 14}" width="4" height="{h - 16}" fill="#d8d8d8"/>')
    # flag pole and castle
    px = 898
    s.append(f'<rect x="{px}" y="58" width="3" height="{G - 58}" fill="#6b6b6b"/><rect x="{px - 2}" y="54" width="7" height="7" fill="#f5f5f5" stroke="{INK}" stroke-width="1"/>'
             f'<g class="flag"><path d="M{px},64 l-24,8 l24,8 Z" fill="#2b2b2b" stroke="{INK}" stroke-width="1.2"/></g>')
    cx = 926
    s.append(f'<rect x="{cx}" y="{G - 34}" width="34" height="34" fill="#a0a0a0" stroke="{INK}" stroke-width="1.5"/>'
             f'<path d="M{cx},{G - 34} v-6 h6 v6 h6 v-6 h6 v6 h6 v-6 h4 v6" fill="#a0a0a0" stroke="{INK}" stroke-width="1.5"/>'
             f'<path d="M{cx + 12},{G} v-13 a5,5 0 0 1 10,0 v13 Z" fill="{INK}"/>')
    return "".join(s)


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
        use = f'<use href="#coin" class="coin{got}" data-i="{i}" x="{x - 4.5:.1f}" y="{cy - 6:.1f}"/>'
        if i <= len(read):
            tip = html.escape(f"{i}. {read[i - 1][0]}")
            out.append(f'<a href="{root}weeks/{read[i - 1][1]}.html"><title>{tip}</title>{use}</a>')
        else:
            out.append(use)
        if i % 10 == 0 and i < 100:
            used = " used" if i <= n else ""
            out.append(f'<g class="block{used}" data-i="{i}"><rect x="{x - 10:.1f}" y="14" width="20" height="20" rx="2"/>'
                       f'<text x="{x:.1f}" y="28.5" text-anchor="middle">{i}</text></g>')
    runner = (f'<g class="runner" aria-hidden="true"><ellipse cx="{6 * PX}" cy="{14 * PX}" rx="{5 * PX}" ry="{1.5 * PX}" fill="{INK}" opacity=".18"/>'
              f'<g class="fa">{_rects(BODY + LEGS_A, PALETTE, PX)}</g><g class="fb" style="display:none">{_rects(BODY + LEGS_B, PALETTE, PX)}</g></g>')
    data = html.escape(json.dumps(pts, separators=(",", ":")))
    defs = ('<defs><pattern id="brick" width="16" height="16" patternUnits="userSpaceOnUse">'
            '<rect width="16" height="16" fill="#8c8c8c"/><path d="M0 8H16M0 0H16M8 0V8M0 8V16M16 8V16" stroke="#555" stroke-width="1.2" fill="none"/></pattern>'
            f'<symbol id="coin" viewBox="0 0 9 12" width="9" height="12">{_rects(COIN, COIN_COLORS, 1.5)}</symbol>'
            '<clipPath id="stage"><rect width="960" height="176" rx="8"/></clipPath></defs>')
    return (f'<div class="world" data-n="{n}" data-res="{RES}" data-points="{data}" role="img" aria-label="{n} of 100 papers read">'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{defs}'
            f'<g clip-path="url(#stage)">{_scene()}{"".join(out)}{runner}</g>'
            f'<rect width="960" height="176" rx="8" fill="none" stroke="{INK}" stroke-width="1.6"/></svg></div>')
