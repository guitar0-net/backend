# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Checks for the inline chord markup of `Song.chord_text`.

A chord is written in square brackets right before the syllable it belongs
to: `Мы не [G (2)]знали`. Anything after the chord name inside the brackets
(a space or an opening parenthesis onwards) is a performance note such as a
strum count, so only the leading name is compared with the song's chords.
"""

import html
import re
from collections.abc import Iterable

from markdownx.utils import markdownify  # type: ignore[import-untyped]

_CHORD_PATTERN = re.compile(r"\[([^\[\]]*)\]")
_CHORD_NAME_END = re.compile(r"[\s(]")
_PLACEHOLDER = re.compile(r"\ue000(\d+)\ue001")
_WORD_WITH_PLACEHOLDER = re.compile(r"[^\s<>]*\ue000[^\s<>]*")


def find_chord_text_errors(chord_text: str) -> list[str]:
    """Return a description of every malformed chord bracket, by line number.

    Clients cut the chords out before rendering markdown, so a stray bracket
    would swallow lyrics or leak into the rendered text.
    """
    errors: list[str] = []
    for number, line in enumerate(chord_text.splitlines(), start=1):
        is_open = False
        for char in line:
            if char == "[" and is_open:
                errors.append(f"Строка {number}: вложенная «[».")
            elif char == "]" and not is_open:
                errors.append(f"Строка {number}: «]» без открывающей «[».")
            if char in "[]":
                is_open = char == "["
        if is_open:
            errors.append(f"Строка {number}: «[» не закрыта.")
        if any(not chord.strip() for chord in _CHORD_PATTERN.findall(line)):
            errors.append(f"Строка {number}: пустые скобки «[]».")
    return errors


def find_unknown_chords(chord_text: str, known_titles: Iterable[str]) -> set[str]:
    """Return chord names used in the text that are not among `known_titles`."""
    known = set(known_titles)
    names = {
        _CHORD_NAME_END.split(chord.strip(), maxsplit=1)[0]
        for chord in _CHORD_PATTERN.findall(chord_text)
    }
    return {name for name in names if name and name not in known}


def render_chord_text_html(chord_text: str) -> str:
    """Render `chord_text` markdown to HTML with every chord above its syllable.

    Each chord becomes a `chord-pair` stacking the chord over the text that
    follows it up to the next chord or space, and every word holding a chord
    is wrapped in a `chord-word` so it is never split by a line wrap. The
    chords are swapped for private-use placeholders while markdown runs,
    because markdown would read the brackets as links.
    """
    chords: list[str] = []

    def to_placeholder(match: re.Match[str]) -> str:
        chords.append(match.group(1).strip())
        return f"\ue000{len(chords) - 1}\ue001"

    rendered: str = markdownify(_CHORD_PATTERN.sub(to_placeholder, chord_text))

    def to_chord_word(match: re.Match[str]) -> str:
        prefix, *parts = _PLACEHOLDER.split(match.group(0))
        pairs = "".join(
            _render_chord_pair(chords[int(index)], syllable)
            for index, syllable in zip(parts[::2], parts[1::2], strict=True)
        )
        return f'<span class="chord-word">{prefix}{pairs}</span>'

    return _WORD_WITH_PLACEHOLDER.sub(to_chord_word, rendered)


def _render_chord_pair(chord: str, syllable: str) -> str:
    name = _CHORD_NAME_END.split(chord, maxsplit=1)[0]
    note = chord[len(name) :].strip()
    label = f'<b class="chord-symbol">{html.escape(name)}</b>'
    if note:
        label += f'<span class="chord-note">{html.escape(note)}</span>'
    return (
        f'<span class="chord-pair"><span class="chord">{label}</span>'
        f'<span class="chord-syllable">{syllable or "&nbsp;"}</span></span>'
    )
