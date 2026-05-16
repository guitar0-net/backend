# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for schemes management commands."""

import pytest
from django.core.management import call_command

from apps.schemes.models import ImageScheme
from apps.schemes.tests.factories import ImageSchemeFactory


@pytest.mark.django_db
def test_recalculate_image_dimensions_restores_width(image_scheme: ImageScheme) -> None:
    ImageScheme.objects.filter(pk=image_scheme.pk).update(width=0)

    call_command("recalculate_image_dimensions")

    image_scheme.refresh_from_db()
    assert image_scheme.width == 800


@pytest.mark.django_db
def test_recalculate_image_dimensions_restores_height(
    image_scheme: ImageScheme,
) -> None:
    ImageScheme.objects.filter(pk=image_scheme.pk).update(height=0)

    call_command("recalculate_image_dimensions")

    image_scheme.refresh_from_db()
    assert image_scheme.height == 600


@pytest.mark.django_db
def test_recalculate_image_dimensions_updates_all_schemes() -> None:
    ImageSchemeFactory.create_batch(3)
    ImageScheme.objects.all().update(width=0, height=0)

    call_command("recalculate_image_dimensions")

    assert ImageScheme.objects.filter(width__gt=0, height__gt=0).count() == 3
