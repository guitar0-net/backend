# SPDX-FileCopyrightText: 2025 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest
from rest_framework.serializers import ValidationError

from apps.schemes.api.serializers import ImageSchemeSerializer
from apps.schemes.tests.factories import ImageSchemeFactory


@pytest.fixture
def valid_image_scheme_data() -> dict[str, str | int]:
    return {
        "code": "beat-1",
        "inscription": "Бой №1",
        "image": "/lesson_schemes/beat1.png",
    }


@pytest.fixture
def invalid_directory_image_scheme_data() -> dict[str, str | int]:
    return {
        "code": "beat-1",
        "inscription": "Бой №1",
        "image": "/some_directory/beat1.png",
    }


@pytest.fixture
def invalid_not_enough_data_image_scheme() -> dict[str, str | int]:
    return {
        "inscription": "Бой №1",
        "image": "/lesson_schemes/beat1.png",
    }


@pytest.mark.django_db
def test_image_scheme_serializer_valid(
    valid_image_scheme_data: dict[str, str | int],
) -> None:
    serializer = ImageSchemeSerializer(data=valid_image_scheme_data)
    serializer.is_valid()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data",
    (
        invalid_directory_image_scheme_data,
        invalid_not_enough_data_image_scheme,
    ),
)
def test_image_scheme_serializer_invalid(
    data: dict[str, str | int],
) -> None:
    serializer = ImageSchemeSerializer(data=data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_output_data(image_scheme_factory: type[ImageSchemeFactory]) -> None:
    scheme = image_scheme_factory.create(
        code="beat-1",
        inscription="Beat #1",
        height=100,
        width=200,
        image="/lesson_schemes/beat1.png",
    )
    serializer = ImageSchemeSerializer(scheme)
    data = serializer.data

    assert "pk" in data
    assert "code" not in data
    assert data["inscription"] == "Beat #1"
    assert data["height"] == 100
    assert data["width"] == 200
    assert "lesson_schemes/beat1.png" in data["image"]
