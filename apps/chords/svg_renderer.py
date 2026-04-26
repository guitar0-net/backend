# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SVG renderer for chord diagrams."""

from apps.chords.models import Chord, ChordPosition

_STRINGS = 6
_FRETS = 4

_FINGER_FILL = {1: "#ffb3c1", 2: "#fff0a0", 3: "#b3f0b3", 4: "#b3d9ff"}
_FINGER_STROKE = {1: "#cc0033", 2: "#cc6600", 3: "#006600", 4: "#0033cc"}

_ROMAN = ("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII")
_BARRE_THICKNESS = 6  # thin radius of the barre ellipse in both orientations


def render_chord_svg(chord: Chord) -> tuple[str, str]:
    """Render horizontal and vertical SVG diagrams for a chord.

    Args:
        chord: Chord instance with related positions prefetched or accessible.

    Returns:
        Tuple of (svg_horizontal, svg_vertical) as SVG strings.
    """
    positions: list[ChordPosition] = list(chord.positions.all())
    return _render_horizontal(chord, positions), _render_vertical(chord, positions)


def _roman(n: int) -> str:
    return _ROMAN[n] if 0 < n < len(_ROMAN) else str(n)


def _tonic_string(title: str) -> int:
    """Derive the tonic string number from the chord title."""
    root = title[0].upper() if title else ""
    if root in {"G", "E"}:
        return 6
    if root == "D":
        return 4
    return 5


def _aria_label(chord: Chord, positions: list[ChordPosition]) -> str:
    parts = [chord.title]
    if chord.has_barre:
        barre_pos = next((p for p in positions if p.finger == 1 and p.fret > 0), None)
        if barre_pos:
            parts.append(f"barre on fret {barre_pos.fret}")
    for pos in sorted(positions, key=lambda p: p.string_number):
        if pos.fret == -1:
            parts.append(f"string {pos.string_number} muted")
        elif pos.fret == 0:
            parts.append(f"string {pos.string_number} open")
        else:
            parts.append(
                f"string {pos.string_number} fret {pos.fret} finger {pos.finger}"
            )
    return ", ".join(parts)


def _string_sw(s_idx: int) -> float:
    """Stroke width for string at index s_idx (0 = thickest/6th string)."""
    return round(max(0.5, 1.1 - s_idx * 0.2), 1)


# ── Horizontal (nut on the RIGHT, frets increase going LEFT) ─────────────────
# Strings are horizontal lines; frets are vertical lines.


def _render_horizontal(chord: Chord, positions: list[ChordPosition]) -> str:  # noqa: PLR0914
    fret_w = 45  # px per fret column
    string_h = 12  # px between string lines
    circle_r = 5

    ml = 15  # left margin — T marker
    mt = 22  # top margin  — roman numeral labels
    mr = 22  # right margin — open/muted markers
    mb = 6  # bottom margin

    gw = _FRETS * fret_w
    gh = (_STRINGS - 1) * string_h
    gr = ml + gw  # nut x (grid right)
    gb = mt + gh  # grid bottom

    width = ml + gw + mr
    height = mt + gh + mb

    overhang = 0 if chord.start_fret == 1 else 3
    elements: list[str] = []

    # String lines: string 6 (thickest) at top, string 1 at bottom
    for i in range(_STRINGS):
        sy = mt + i * string_h
        elements.append(
            f'<line x1="{ml}" y1="{sy}" x2="{gr + overhang}" y2="{sy}" '
            f'stroke="currentColor" stroke-width="{_string_sw(i)}"/>'
        )

    # Fret lines: nut on right, thick when start_fret == 1
    for fi in range(_FRETS + 1):
        fx = ml + fi * fret_w
        nut_sw = 4 if (fi == _FRETS and chord.start_fret == 1) else 1
        elements.append(
            f'<line x1="{fx}" y1="{mt - 7}" x2="{fx}" y2="{gb + 0.3}" '
            f'stroke="currentColor" stroke-width="{nut_sw}"/>'
        )

    # Roman numeral labels between fret lines, above the grid
    for f in range(1, _FRETS + 1):
        cx = ml + (_FRETS - f) * fret_w + fret_w // 2
        rn = _roman(chord.start_fret + f - 1)
        elements.append(
            f'<text x="{cx}" y="{mt - 9}" text-anchor="middle" '
            f'font-size="9" fill="currentColor">{rn}</text>'
        )

    # Tonic marker on the LEFT (away from open/muted markers on the right)
    tonic_sy = mt + (_STRINGS - _tonic_string(chord.title)) * string_h
    elements.append(
        f'<text x="{ml - 5}" y="{tonic_sy + 3}" text-anchor="end" '
        f'font-size="7" font-weight="bold" fill="currentColor">T</text>'
    )

    pos_map: dict[int, ChordPosition] = {p.string_number: p for p in positions}

    for s in range(1, _STRINGS + 1):
        sy = mt + (_STRINGS - s) * string_h
        pos = pos_map.get(s)
        if pos is None:
            continue
        if pos.fret == -1:
            elements.append(
                f'<text x="{gr + 5}" y="{sy + 3}" text-anchor="start" '
                f'font-size="11" fill="currentColor">×</text>'
            )
        elif pos.fret == 0 and not chord.has_barre:
            elements.append(
                f'<text x="{gr + 5}" y="{sy + 3}" text-anchor="start" '
                f'font-size="11" fill="currentColor">○</text>'
            )
        else:
            fi = pos.fret - chord.start_fret + 1
            if 1 <= fi <= _FRETS:
                cx = ml + (_FRETS - fi) * fret_w + fret_w // 2
                if chord.has_barre and pos.finger == 1:
                    by = mt + gh // 2
                    elements.append(
                        f'<ellipse cx="{cx}" cy="{by}" rx="{_BARRE_THICKNESS}" '
                        f'ry="{gh // 2 + circle_r}" fill="{_FINGER_FILL[1]}"'
                        f' stroke="{_FINGER_STROKE[1]}" stroke-width="0.5"/>'
                    )
                    elements.append(
                        f'<text x="{cx}" y="{by + 4}" text-anchor="middle" '
                        f'font-size="9" fill="{_FINGER_STROKE[1]}">1</text>'
                    )
                else:
                    fill = _FINGER_FILL.get(pos.finger, "#cccccc")
                    stroke = _FINGER_STROKE.get(pos.finger, "#666666")
                    elements.append(
                        f'<circle cx="{cx}" cy="{sy}" r="{circle_r}" '
                        f'fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>'
                    )
                    if pos.finger > 0:
                        elements.append(
                            f'<text x="{cx}" y="{sy + 3}" text-anchor="middle" '
                            f'font-size="9" fill="{stroke}">{pos.finger}</text>'
                        )

    label = _aria_label(chord, positions)
    body = "\n  ".join(elements)
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'aria-label="{label}">\n  {body}\n</svg>'
    )


# ── Vertical (classic chord box, nut at TOP) ─────────────────────────────────
# Strings are vertical lines; frets are horizontal lines.


def _render_vertical(chord: Chord, positions: list[ChordPosition]) -> str:  # noqa: PLR0914, PLR0915
    string_w = 12  # px between string lines (mirrors horizontal string_h)
    fret_h = 45  # px per fret row (mirrors horizontal fret_w)
    circle_r = 5

    ml = 25  # left margin — roman numeral labels (mirrors horizontal mt)
    mt = 19  # top margin — open/muted markers (mirrors horizontal mr)
    mr = 6  # right margin (mirrors horizontal mb)
    mb = 15  # bottom margin — T marker (mirrors horizontal ml)

    gw = (_STRINGS - 1) * string_w
    gh = _FRETS * fret_h

    str_start = ml  # x of string 6 (leftmost)
    fl_x1 = (
        str_start - 7
    )  # fret lines extend 7 px left of string 6 (mirrors horizontal's mt-7)
    fl_x2 = str_start + gw  # fret lines end at string 1
    gb = mt + gh

    width = ml + gw + mr
    height = mt + gh + mb

    overhang = 0 if chord.start_fret == 1 else 3
    elements: list[str] = []

    # String lines: string 6 at left, string 1 at right
    for i in range(_STRINGS):
        sx = str_start + i * string_w
        elements.append(
            f'<line x1="{sx}" y1="{mt - overhang}" x2="{sx}" y2="{gb}" '
            f'stroke="currentColor" stroke-width="{_string_sw(i)}"/>'
        )

    # Fret lines: nut at top, thick when start_fret == 1
    for fi in range(_FRETS + 1):
        fy = mt + fi * fret_h
        nut_sw = 4 if (fi == 0 and chord.start_fret == 1) else 1
        elements.append(
            f'<line x1="{fl_x1}" y1="{fy}" x2="{fl_x2 + 0.3}" y2="{fy}" '
            f'stroke="currentColor" stroke-width="{nut_sw}"/>'
        )

    # Roman numeral labels to the left, centred in each fret row
    for f in range(1, _FRETS + 1):
        ry = mt + (f - 1) * fret_h + fret_h // 2 + 3
        rn = _roman(chord.start_fret + f - 1)
        elements.append(
            f'<text x="{fl_x1 - 2}" y="{ry}" text-anchor="end" '
            f'font-size="9" fill="currentColor">{rn}</text>'
        )

    # Open/muted markers above the nut
    pos_map: dict[int, ChordPosition] = {p.string_number: p for p in positions}

    for s in range(1, _STRINGS + 1):
        sx = str_start + (_STRINGS - s) * string_w
        pos = pos_map.get(s)
        if pos is None:
            continue
        if pos.fret == -1:
            elements.append(
                f'<text x="{sx}" y="{mt - 5}" text-anchor="middle" '
                f'font-size="11" fill="currentColor">×</text>'
            )
        elif pos.fret == 0 and not chord.has_barre:
            elements.append(
                f'<text x="{sx}" y="{mt - 5}" text-anchor="middle" '
                f'font-size="11" fill="currentColor">○</text>'
            )
        else:
            fi = pos.fret - chord.start_fret + 1
            if 1 <= fi <= _FRETS:
                cy = mt + (fi - 1) * fret_h + fret_h // 2
                if chord.has_barre and pos.finger == 1:
                    bx = str_start + gw // 2
                    elements.append(
                        f'<ellipse cx="{bx}" cy="{cy}" rx="{gw // 2 + circle_r}" '
                        f'ry="{_BARRE_THICKNESS}" fill="{_FINGER_FILL[1]}"'
                        f' stroke="{_FINGER_STROKE[1]}" stroke-width="0.5"/>'
                    )
                    elements.append(
                        f'<text x="{bx}" y="{cy + 4}" text-anchor="middle" '
                        f'font-size="9" fill="{_FINGER_STROKE[1]}">1</text>'
                    )
                else:
                    fill = _FINGER_FILL.get(pos.finger, "#cccccc")
                    stroke = _FINGER_STROKE.get(pos.finger, "#666666")
                    elements.append(
                        f'<circle cx="{sx}" cy="{cy}" r="{circle_r}" '
                        f'fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>'
                    )
                    if pos.finger > 0:
                        elements.append(
                            f'<text x="{sx}" y="{cy + 3}" text-anchor="middle" '
                            f'font-size="9" fill="{stroke}">{pos.finger}</text>'
                        )

    # Tonic marker below the grid
    tonic_sx = str_start + (_STRINGS - _tonic_string(chord.title)) * string_w
    elements.append(
        f'<text x="{tonic_sx}" y="{gb + 11}" text-anchor="middle" '
        f'font-size="7" font-weight="bold" fill="currentColor">T</text>'
    )

    label = _aria_label(chord, positions)
    body = "\n  ".join(elements)
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'aria-label="{label}">\n  {body}\n</svg>'
    )
