# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Services for the schemes app."""

from PIL import Image as PilImage

from .models import ImageScheme
from .selectors import get_all_image_schemes


class ImageSchemeService:
    """Business logic for the ImageScheme entity."""

    @staticmethod
    def bulk_recalculate_dimensions() -> int:
        """Read every image file from disk and update width/height in the DB.

        Returns:
            int: Number of updated records.
        """
        schemes = list(get_all_image_schemes())
        for scheme in schemes:
            with PilImage.open(scheme.image.path) as img:
                scheme.width, scheme.height = img.size
        ImageScheme.objects.bulk_update(schemes, ["width", "height"])
        return len(schemes)
