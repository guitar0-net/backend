# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for songs management commands."""

import hashlib
import json
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.songs.models import Song
from apps.songs.tests.factories import SongFactory


def _write_conversion(directory: Path, song: Song, chord_text: str) -> Path:
    path = directory / "chord-texts.json"
    digest = hashlib.sha256(song.text.encode()).hexdigest()
    path.write_text(
        json.dumps({
            str(song.uuid): {"source_sha256": digest, "chord_text": chord_text}
        }),
        encoding="utf-8",
    )
    return path


@pytest.mark.django_db
def test_import_chord_texts_fills_chord_text_from_file(tmp_path: Path) -> None:
    song = SongFactory.create(text="Холодный ветер с дождём")
    path = _write_conversion(tmp_path, song, "[Am]Холодный [G]ветер с дождём")

    call_command("import_chord_texts", str(path), stdout=StringIO())

    song.refresh_from_db()
    assert song.chord_text == "[Am]Холодный [G]ветер с дождём"


@pytest.mark.django_db
def test_import_chord_texts_dry_run_leaves_song_unchanged(tmp_path: Path) -> None:
    song = SongFactory.create(text="Усилился втрое")
    path = _write_conversion(tmp_path, song, "[E]Усилился втрое")

    call_command("import_chord_texts", str(path), "--dry-run", stdout=StringIO())

    song.refresh_from_db()
    assert not song.chord_text


@pytest.mark.django_db
def test_import_chord_texts_overwrite_replaces_filled_chord_text(
    tmp_path: Path,
) -> None:
    song = SongFactory.create(text="Всё говорит о том", chord_text="[Dm]Старое")
    path = _write_conversion(tmp_path, song, "Всё [C]говорит о том")

    call_command("import_chord_texts", str(path), "--overwrite", stdout=StringIO())

    song.refresh_from_db()
    assert song.chord_text == "Всё [C]говорит о том"


def test_import_chord_texts_rejects_file_that_is_not_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{не json", encoding="utf-8")

    with pytest.raises(CommandError):
        call_command("import_chord_texts", str(path))


def test_import_chord_texts_rejects_json_that_is_not_an_object(tmp_path: Path) -> None:
    path = tmp_path / "list.json"
    path.write_text('["Кино"]', encoding="utf-8")

    with pytest.raises(CommandError):
        call_command("import_chord_texts", str(path))


def test_import_chord_texts_rejects_key_that_is_not_uuid(tmp_path: Path) -> None:
    path = tmp_path / "bad-key.json"
    path.write_text(
        json.dumps({"песня": {"source_sha256": "ab", "chord_text": "[Am]"}}),
        encoding="utf-8",
    )

    with pytest.raises(CommandError):
        call_command("import_chord_texts", str(path))


def test_import_chord_texts_rejects_entry_that_is_not_an_object(
    tmp_path: Path,
) -> None:
    path = tmp_path / "bad-entry.json"
    path.write_text(
        json.dumps({"000b5927-2fb1-4a28-b636-6e7c2234d2d7": "[Am]Звезда"}),
        encoding="utf-8",
    )

    with pytest.raises(CommandError):
        call_command("import_chord_texts", str(path))


def test_import_chord_texts_rejects_entry_without_chord_text(tmp_path: Path) -> None:
    path = tmp_path / "no-chord-text.json"
    path.write_text(
        json.dumps({"6f1c1b0e-1d2e-4c35-9a77-5b1e0f3a9c41": {"source_sha256": "ab"}}),
        encoding="utf-8",
    )

    with pytest.raises(CommandError):
        call_command("import_chord_texts", str(path))


def test_import_chord_texts_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(CommandError):
        call_command("import_chord_texts", str(tmp_path / "нет-такого.json"))


@pytest.mark.django_db
def test_import_chord_texts_prints_chords_missing_from_song(tmp_path: Path) -> None:
    song = SongFactory.create(text="Восьмиклассница")
    path = _write_conversion(tmp_path, song, "[Fm#(8)]Восьмиклассница")
    stdout = StringIO()

    call_command("import_chord_texts", str(path), stdout=stdout)

    assert "Fm#" in stdout.getvalue()


@pytest.mark.django_db
def test_import_chord_texts_prints_malformed_song(tmp_path: Path) -> None:
    song = SongFactory.create(text="Пачка сигарет")
    path = _write_conversion(tmp_path, song, "[Am Пачка сигарет")
    stdout = StringIO()

    call_command("import_chord_texts", str(path), stdout=stdout)

    assert str(song.uuid) in stdout.getvalue()
