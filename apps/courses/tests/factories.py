# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Factory for generating test Course instances."""

import factory
from factory import Faker, Sequence, SubFactory  # type: ignore[attr-defined]
from factory.django import DjangoModelFactory

from apps.courses.models import Course, CourseLesson
from apps.lessons.models import Lesson
from apps.lessons.tests.factories import LessonFactory


class CourseFactory(DjangoModelFactory[Course]):
    """Factory for creating Course instances."""

    title = Faker("sentence", nb_words=3)
    description = Faker("paragraph", nb_sentences=2)
    is_published = True

    @factory.post_generation  # type: ignore[misc, attr-defined]
    def lessons(
        self,
        create: bool,
        extracted: int | list[Lesson] | None,
    ) -> None:
        """Create lessons for course via CourseLesson through model.

        Usage:
        - CourseFactory(lessons=[lesson1, lesson2])
        - CourseFactory(lessons=3)
        """
        if not create:
            return

        if extracted is None:
            return

        if isinstance(extracted, int):
            lessons = LessonFactory.create_batch(extracted)
        else:
            lessons = extracted

        for order, lesson in enumerate(lessons, start=1):
            CourseLessonFactory.create(course=self, lesson=lesson, order=order)

    class Meta:
        model = Course
        skip_postgeneration_save = True


class CourseLessonFactory(DjangoModelFactory[CourseLesson]):
    """Factory for creating CourseLesson instances."""

    course = SubFactory(CourseFactory)
    lesson = SubFactory(LessonFactory)
    order = Sequence(lambda n: n + 1)

    class Meta:
        model = CourseLesson
