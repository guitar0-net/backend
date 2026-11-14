# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Management command that fills Song.chord_text from a conversion file."""

import json
import uuid
from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.songs.services import (
    ChordTextImport,
    ChordTextImportReport,
    import_chord_texts,
)


class Command(BaseCommand):
    """Import inline-chord song texts produced by `scripts/convert-chords.mjs`.

    The file maps song UUIDs to `{"source_sha256": ..., "chord_text": ...}`,
    where `source_sha256` is the hex SHA-256 of the UTF-8 `Song.text` the
    conversion was made from. A malformed file is rejected before anything
    is written.
    """

    help = "Fill Song.chord_text from a JSON file keyed by song UUID."

    def add_arguments(self, parser: ArgumentParser) -> None:  # noqa: PLR6301
        """Declare the file path and the --overwrite / --dry-run flags."""
        parser.add_argument("path", type=Path, help="JSON file from the converter.")
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace a chord_text that is already filled.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing.",
        )

    def handle(self, *args: object, **options: object) -> None:
        """Read the file, import it, and print what happened to each song."""
        path = options["path"]
        if not isinstance(path, Path):
            msg = f"Expected a file path, got {path!r}."
            raise CommandError(msg)
        dry_run = options["dry_run"] is True
        report = import_chord_texts(
            _read_imports(path),
            overwrite=options["overwrite"] is True,
            dry_run=dry_run,
        )
        self._print_report(report, dry_run=dry_run)

    def _print_report(self, report: ChordTextImportReport, *, dry_run: bool) -> None:
        for title, uuids in (
            ("Skipped as stale (text changed after the snapshot)", report.stale),
            ("Skipped as unknown UUID", report.unknown),
            ("Skipped as already filled (use --overwrite)", report.already_filled),
        ):
            for song_uuid in uuids:
                self.stdout.write(f"{title}: {song_uuid}")
        for song_uuid, errors in report.invalid.items():
            self.stdout.write(f"Skipped as malformed: {song_uuid}: {'; '.join(errors)}")
        for song_uuid, chords in report.unknown_chords.items():
            names = ", ".join(sorted(chords))
            self.stdout.write(f"Chords missing from the song: {song_uuid}: {names}")

        updated = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{updated}: {len(report.updated)}, "
                f"stale: {len(report.stale)}, "
                f"unknown: {len(report.unknown)}, "
                f"already filled: {len(report.already_filled)}, "
                f"malformed: {len(report.invalid)}."
            )
        )


def _read_imports(path: Path) -> list[ChordTextImport]:
    try:
        data: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        msg = f"Cannot read {path}: {error}"
        raise CommandError(msg) from error
    if not isinstance(data, dict):
        msg = "Expected a JSON object keyed by song UUID."
        raise CommandError(msg)

    imports: list[ChordTextImport] = []
    for key, entry in data.items():
        try:
            song_uuid = uuid.UUID(key)
        except ValueError as error:
            msg = f"Not a UUID: {key!r}."
            raise CommandError(msg) from error
        if not isinstance(entry, dict):
            msg = f"{key}: expected an object."
            raise CommandError(msg)
        source_sha256 = entry.get("source_sha256")
        chord_text = entry.get("chord_text")
        if not isinstance(source_sha256, str) or not isinstance(chord_text, str):
            msg = f"{key}: `source_sha256` and `chord_text` must be strings."
            raise CommandError(msg)
        imports.append(ChordTextImport(song_uuid, source_sha256, chord_text))
    return imports
