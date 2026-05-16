# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Selectors for the schemes app."""

from django.db.models import QuerySet

from .models import ImageScheme


def get_all_image_schemes() -> QuerySet[ImageScheme]:
    """Get a QuerySet of all ImageScheme objects.

    Returns:
        QuerySet[ImageScheme]: All image schemes.
    """
    return ImageScheme.objects.all()
