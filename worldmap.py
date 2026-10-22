"""The hand-drawn map at the top of every page: a winding road with 100 stops, a pixel-art
runner who advances one stop per paper read. Geometry is computed here; map.js animates."""
import html
import json
import math
import random

W, H = 960, 200
INK = "#4a4034"
PX = 3  # one sprite pixel in map units

# the road, as control points (Catmull-Rom through them)
ROAD = [(62, 150), (132, 112), (215, 72), (310, 54), (400, 90), (470, 140), (560, 152),
        (650, 114), (725, 68), (800, 52), (862, 80), (900, 112)]

PALETTE = {"K": "#2b2723", "W": "#fdfbf7", "R": "#b5402f", "B": "#4d6a86"}
BODY = [
    ".....RR.....",
    ".....KK.....",
    "..KKKKKKKK..",
    ".KRRRRRRRRK.",
    ".KWKWWWWKWK.",
    ".KWKWWWWKWK.",
    ".KWWWWWWWWK.",
    ".KWWKKKKWWK.",
    "..KKKKKKKK..",
    "..KBBBBBBK..",
    ".KBBBBBBBBK.",
    "..KBBBBBBK..",
]
LEGS_A = ["..KK....KK..", ".KK......KK."]
LEGS_B = ["...KKKKKK...", "...KK..KK..."]


def _bezier_points(pts, closed=False, steps=40):
    n = len(pts)
    P = (lambda i: pts[i % n]) if closed else (lambda i: pts[max(0, min(n - 1, i))])
    segs = n if closed else n - 1
    d, samples = [], []
    for i in range(segs):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if i == 0:
            d.append(f"M{p1[0]:.1f},{p1[1]:.1f}")
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
        for s in range(steps):
            t = s / steps
            u = 1 - t
            samples.append((u**3 * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p2[0],
                            u**3 * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p2[1]))
    samples.append(P(segs))
    return " ".join(d) + (" Z" if closed else ""), samples


def _stops(samples, count=101):
    """Points at equal arc length along the road: index 0 = start, 100 = goal."""
    cum = [0.0]
    for a, b in zip(samples, samples[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    total, out, j = cum[-1], [], 0
    for k in range(count):
        target = total * k / (count - 1)
        while j < len(cum) - 2 and cum[j + 1] < target:
            j += 1
        seg = cum[j + 1] - cum[j] or 1
        f = (target - cum[j]) / seg
        out.append((samples[j][0] + f * (samples[j + 1][0] - samples[j][0]),
                    samples[j][1] + f * (samples[j + 1][1] - samples[j][1])))
    return out


def _sprite(rows):
    rects = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                rects.append(f'<rect x="{x * PX}" y="{y * PX}" width="{PX}" height="{PX}" fill="{PALETTE[ch]}"/>')
    return "".join(rects)


def _land():
    rng = random.Random(7)
    pts = []
    for k in range(22):
        a = 2 * math.pi * k / 22
        wob = 1 + 0.07 * math.sin(3 * a + 1) + 0.05 * math.sin(5 * a) + rng.uniform(-0.03, 0.03)
        pts.append((480 + 452 * wob * math.cos(a), 104 + 84 * wob * math.sin(a)))
    return _bezier_points(pts, closed=True, steps=8)


def _scenery(road_samples):
    rng = random.Random(64)
    land_d, _ = _land()
    items = [f'<path d="{land_d}" fill="none" stroke="#a9c4c4" stroke-width="9" opacity=".45"/>',
             f'<path d="{land_d}" fill="#e7e0c8" fill-opacity=".72" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>']
    placed = []

    def free(x, y, r):
        if ((x - 480) / 410) ** 2 + ((y - 104) / 70) ** 2 > 1:
            return False
        if any(math.dist((x, y), s) < r + 8 for s in road_samples[::6]):
            return False
        return all(math.dist((x, y), q) > r for q, r in placed)

    def spot(r, tries=200):
        for _ in range(tries):
            x, y = rng.uniform(70, 890), rng.uniform(40, 170)
            if free(x, y, r):
                placed.append(((x, y), r))
                return x, y
        return None

    s = spot(34)
    if s:  # lake
        x, y = s
        items.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="26" ry="11" fill="#cfe0e0" stroke="#6f8a8f" stroke-width="1.4"/>'
                     f'<path d="M{x - 12:.0f},{y:.0f} q4,-3 8,0 t8,0 M{x - 6:.0f},{y + 4:.0f} q4,-3 8,0 t8,0" fill="none" stroke="#6f8a8f" stroke-width="1"/>')
    for _ in range(5):  # mountains
        s = spot(26)
        if s:
            x, y = s
            items.append(f'<path d="M{x - 20:.0f},{y + 12:.0f} L{x:.0f},{y - 16:.0f} L{x + 20:.0f},{y + 12:.0f} Z" fill="#d6cdb0" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>'
                         f'<path d="M{x - 7:.0f},{y - 2:.0f} L{x:.0f},{y - 16:.0f} L{x + 7:.0f},{y - 2:.0f} L{x + 2:.0f},{y + 1:.0f} L{x - 2:.0f},{y - 3:.0f} Z" fill="#fdfbf7" stroke="{INK}" stroke-width="1"/>')
    for _ in range(16):  # trees
        s = spot(15)
        if s:
            x, y = s
            items.append(f'<line x1="{x:.0f}" y1="{y + 3:.0f}" x2="{x:.0f}" y2="{y + 10:.0f}" stroke="{INK}" stroke-width="1.6"/>'
                         f'<circle cx="{x:.0f}" cy="{y - 2:.0f}" r="7.5" fill="#a9bd86" stroke="{INK}" stroke-width="1.3"/>')
    return "".join(items)


def _flags(start, goal):
    sx, sy = start
    gx, gy = goal
    s = (f'<g stroke="{INK}" stroke-width="1.6" stroke-linecap="round"><line x1="{sx - 14}" y1="{sy + 4}" x2="{sx - 14}" y2="{sy - 26}"/></g>'
         f'<path d="M{sx - 14},{sy - 26} l18,5 l-18,6 Z" fill="#b5402f" stroke="{INK}" stroke-width="1.2"/>'
         f'<text x="{sx - 14}" y="{sy + 17}" text-anchor="middle" class="label">START</text>')
    g = (f'<rect x="{gx + 6}" y="{gy - 26}" width="30" height="30" fill="#d6cdb0" stroke="{INK}" stroke-width="1.5"/>'
         f'<path d="M{gx + 6},{gy - 26} v-6 h6 v6 h6 v-6 h6 v6 h6 v-6 h6 v6" fill="#d6cdb0" stroke="{INK}" stroke-width="1.5"/>'
         f'<path d="M{gx + 16},{gy + 4} v-12 a5,5 0 0 1 10,0 v12 Z" fill="{INK}"/>'
         f'<line x1="{gx + 21}" y1="{gy - 38}" x2="{gx + 21}" y2="{gy - 54}" stroke="{INK}" stroke-width="1.6"/>'
         f'<path d="M{gx + 21},{gy - 54} l14,4 l-14,5 Z" fill="#b5402f" stroke="{INK}" stroke-width="1.2"/>'
         f'<text x="{gx + 21}" y="{gy + 17}" text-anchor="middle" class="label">GOAL</text>')
    return s + g


def render(read, root=""):
    """`read`: list of (paper title, week slug), in reading order."""
    n = min(len(read), 100)
    road_d, samples = _bezier_points(ROAD)
    stops = _stops(samples)
    dots = []
    for i in range(1, 101):
        x, y = stops[i]
        major = i % 10 == 0
        cls = "dot" + (" read" if i <= n else "") + (" major" if major else "")
        r = 5 if major else 2.4
        tip = html.escape(f"{i}. {read[i - 1][0]}") if i <= len(read) else f"{i}"
        circle = f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" data-i="{i}"><title>{tip}</title></circle>'
        if i <= len(read):
            circle = f'<a href="{root}weeks/{read[i - 1][1]}.html">{circle}</a>'
        dots.append(circle)
        if major and i < 100:
            dots.append(f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" class="label mile">{i}</text>')
    start = stops[0]
    runner = (f'<g class="runner" aria-hidden="true"><ellipse cx="{6 * PX}" cy="{14 * PX}" rx="{5 * PX}" ry="{1.5 * PX}" fill="#2b2723" opacity=".18"/>'
              f'<g class="inner"><g class="fa">{_sprite(BODY + LEGS_A)}</g><g class="fb" style="display:none">{_sprite(BODY + LEGS_B)}</g></g></g>')
    data = html.escape(json.dumps([[round(x, 1), round(y, 1)] for x, y in stops]))
    return (f'<div class="world" data-n="{n}" data-points="{data}" role="img" aria-label="{n} of 100 papers read">'
            f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            '<defs><filter id="rough" x="-2%" y="-2%" width="104%" height="104%">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3" result="n"/>'
            '<feDisplacementMap in="SourceGraphic" in2="n" scale="4"/></filter></defs>'
            f'<g filter="url(#rough)">{_scenery(samples)}{_flags(stops[0], stops[100])}</g>'
            f'<path class="road" d="{road_d}" fill="none"/>'
            f'<path class="trail" d="{road_d}" fill="none" pathLength="100" stroke-dasharray="{n} 200"/>'
            f'{"".join(dots)}{runner}</svg></div>')
