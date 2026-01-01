# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serializers for the schemes app."""

from rest_framework import serializers

from apps.schemes.models import ImageScheme


class ImageSchemeSerializer(serializers.ModelSerializer[ImageScheme]):
    """Output  serializer for an image scheme."""

    class Meta:
        model = ImageScheme
        fields = ("pk", "inscription", "image", "height", "width")
