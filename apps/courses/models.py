# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Models for the courses app."""

from __future__ import annotations

import uuid
from typing import ClassVar

from django.db import models

from apps.lessons.models import Lesson


class Course(models.Model):
    """Educational course containing lessons."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    is_published = models.BooleanField(
        "Опубликован", default=True, help_text="Доступен ли курс пользователям"
    )
    lessons: models.ManyToManyField[Lesson, CourseLesson] = models.ManyToManyField(
        Lesson,
        verbose_name="Уроки",
        through="CourseLesson",
        related_name="courses",
        blank=True,
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self) -> str:
        return self.title


class CourseLesson(models.Model):
    """Lesson position inside a course."""

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_lessons"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="lesson_courses"
    )
    order = models.PositiveIntegerField("Порядок урока в курсе")

    class Meta:
        verbose_name = "Урок курса"
        verbose_name_plural = "Уроки курса"
        ordering = ("order",)
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("course", "lesson"),
                name="unique_course_lesson",
            ),
            models.UniqueConstraint(
                fields=("course", "order"),
                name="unique_course_order",
            ),
        ]

    def __str__(self) -> str:
        return f"Lesson # {self.order} {self.lesson.title} in {self.course}"
