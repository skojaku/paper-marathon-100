"""Little AI-ish characters, one per paper read. Deterministic from the paper's index."""
import html

COLORS = ["#b5402f", "#d98c3f", "#7d8f5c", "#4d6a86", "#8a5a83", "#c96f84", "#9c1a22", "#5f8f8a"]
INK = "#2b2723"


def _pick(i, k, n):
    h = (i * 2654435761 + k * 40503 + 12345) & 0xFFFFFFFF
    return (h >> 8) % n


def character(i, sleeping=False):
    """SVG markup for the i-th character (0-based)."""
    body = COLORS[(i * 3 + _pick(i, 0, 2)) % len(COLORS)]
    top = _pick(i, 1, 4)
    eyes = _pick(i, 2, 4)
    mouth = _pick(i, 3, 3)
    cheeks = _pick(i, 4, 2)
    parts = []
    # top ornament
    if top == 0:
        parts.append(f'<line x1="24" y1="14" x2="24" y2="7" stroke="{body}" stroke-width="2.4" stroke-linecap="round"/>'
                     f'<circle cx="24" cy="6" r="3.2" fill="{body}"/>')
    elif top == 1:
        parts.append(f'<circle cx="12" cy="14" r="4.6" fill="{body}"/><circle cx="36" cy="14" r="4.6" fill="{body}"/>')
    elif top == 2:
        parts.append(f'<path d="M24 14 C24 8 27 5 32 5 C32 10 29 13 24 14 Z" fill="{body}"/>')
    else:
        parts.append(f'<path d="M24 1 L25.8 6.2 L31 8 L25.8 9.8 L24 15 L22.2 9.8 L17 8 L22.2 6.2 Z" fill="{body}"/>')
    # feet and body
    parts.append(f'<rect x="13" y="40" width="7" height="6" rx="3" fill="{body}"/><rect x="28" y="40" width="7" height="6" rx="3" fill="{body}"/>')
    parts.append(f'<rect x="6" y="13" width="36" height="31" rx="14" fill="{body}"/>')
    parts.append('<rect x="10" y="17" width="28" height="23" rx="10" fill="#fdfbf7" opacity=".92"/>')
    # eyes
    if sleeping:
        parts.append(f'<path d="M14 28 Q17.5 31 21 28 M27 28 Q30.5 31 34 28" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    elif eyes == 0:
        parts.append(f'<circle cx="17.5" cy="27" r="2.4" fill="{INK}"/><circle cx="30.5" cy="27" r="2.4" fill="{INK}"/>')
    elif eyes == 1:
        parts.append(f'<path d="M14.5 28 Q17.5 24 20.5 28 M27.5 28 Q30.5 24 33.5 28" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    elif eyes == 2:
        parts.append(f'<ellipse cx="17.5" cy="27" rx="2.2" ry="3.4" fill="{INK}"/><ellipse cx="30.5" cy="27" rx="2.2" ry="3.4" fill="{INK}"/>')
    else:
        parts.append(f'<circle cx="17.5" cy="27" r="3.2" fill="{INK}"/><circle cx="30.5" cy="27" r="3.2" fill="{INK}"/>'
                     '<circle cx="18.5" cy="26" r="1" fill="#fff"/><circle cx="31.5" cy="26" r="1" fill="#fff"/>')
    # mouth
    if mouth == 0:
        parts.append(f'<path d="M20.5 33 Q24 36.5 27.5 33" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    elif mouth == 1:
        parts.append(f'<ellipse cx="24" cy="34" rx="2.2" ry="2.6" fill="{INK}"/>')
    else:
        parts.append(f'<path d="M20 33 Q22 36 24 33 Q26 36 28 33" fill="none" stroke="{INK}" stroke-width="1.8" stroke-linecap="round"/>')
    if cheeks:
        parts.append('<circle cx="12.6" cy="33" r="2.4" fill="#e58a8a" opacity=".5"/><circle cx="35.4" cy="33" r="2.4" fill="#e58a8a" opacity=".5"/>')
    return f'<svg viewBox="0 0 48 48" aria-hidden="true">{"".join(parts)}</svg>'


def crowd(read, root=""):
    """The row of characters. `read` is a list of (paper title, week slug)."""
    n = len(read)
    if n == 0:
        return (f'<div class="crowd waiting" role="img" aria-label="No papers read yet">'
                f'<span class="ghost">{character(0, sleeping=True)}</span>'
                f'<span class="crowd-note">Waiting for the first paper…</span></div>')
    size = 30 if n <= 24 else 24 if n <= 50 else 20
    out = []
    for i, (title, slug) in enumerate(read[:100]):
        cls = ' class="new"' if i == min(n, 100) - 1 else ""
        label = html.escape(f"{i + 1}. {title}")
        out.append(f'<a href="{root}weeks/{slug}.html"{cls} style="--i:{i}" title="{label}">{character(i)}</a>')
    return (f'<div class="crowd" style="--s:{size}px" role="img" aria-label="{min(n, 100)} of 100 papers read">'
            + "".join(out) + "</div>")
