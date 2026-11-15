# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views for the reports API v1."""

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.models.user import User
from apps.reports.constants import (
    REASONS_BY_TARGET_TYPE,
    REASONS_REQUIRING_MESSAGE,
    REPORT_CREATE_THROTTLE_SCOPE,
)
from apps.reports.services import (
    ReportSubmission,
    UnknownReportTargetError,
    submit_report,
)
from apps.reports.throttling import ReportDeviceRateThrottle

from .serializers.report_create_request_serializer import (
    ReportCreateRequestSerializer,
)
from .serializers.report_reasons_serializer import (
    TargetReasonsPayload,
    TargetReasonsSerializer,
)
from .serializers.report_serializer import ReportSerializer

logger = logging.getLogger("reports")


@extend_schema(
    request=ReportCreateRequestSerializer,
    responses={
        status.HTTP_201_CREATED: ReportSerializer,
        status.HTTP_200_OK: OpenApiResponse(
            ReportSerializer, description="A report with this id already exists."
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description="Invalid payload, or the reported item does not exist."
        ),
    },
)
class ReportCreateView(APIView):
    """Submit a report about a content item, an app bug, or a feature idea.

    Unauthenticated, because signing in is optional; a signed-in caller is
    recorded as the report's user. Idempotent on the client-generated `id`,
    so an offline queue can safely resend.
    """

    permission_classes = (AllowAny,)
    throttle_classes = (ReportDeviceRateThrottle, ScopedRateThrottle)
    throttle_scope = REPORT_CREATE_THROTTLE_SCOPE

    def post(self, request: Request) -> Response:  # noqa: PLR6301
        """Validate the report and record it."""
        serializer = ReportCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User | None = None
        if request.user.is_authenticated:
            assert isinstance(request.user, User)
            user = request.user

        try:
            report, created = submit_report(
                ReportSubmission(**serializer.validated_data), user=user
            )
        except UnknownReportTargetError as exc:
            logger.info("Rejected report: %s", exc)
            return Response(
                {"target_id": ["No such item."]}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema(responses=TargetReasonsSerializer(many=True))
class ReportReasonsView(APIView):
    """List the reasons a client may offer for each target type.

    Lets a reason be added or reordered without an app release.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:  # noqa: PLR6301
        """Return reasons grouped by target type."""
        payload: list[TargetReasonsPayload] = [
            {
                "target_type": target_type,
                "reasons": [
                    {
                        "code": reason.value,
                        "title": str(reason.label),
                        "requires_message": reason in REASONS_REQUIRING_MESSAGE,
                    }
                    for reason in reasons
                ],
            }
            for target_type, reasons in REASONS_BY_TARGET_TYPE.items()
        ]
        return Response([TargetReasonsSerializer(item).data for item in payload])
