# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import uuid
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def populate_uuids(apps: Apps, _schema_editor: BaseDatabaseSchemaEditor) -> None:
    Song = apps.get_model("songs", "Song")
    batch = []
    for song in Song.objects.filter(uuid__isnull=True).iterator(chunk_size=500):
        song.uuid = uuid.uuid4()
        batch.append(song)
        if len(batch) >= 500:
            Song.objects.bulk_update(batch, ["uuid"])
            batch.clear()
    if batch:
        Song.objects.bulk_update(batch, ["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("songs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="song",
            name="uuid",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="song",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
