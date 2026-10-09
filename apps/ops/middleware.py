# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Prometheus middleware for HTTP metrics collection."""

import time
from collections.abc import Callable

from django.http import HttpRequest
from django.http.response import HttpResponseBase

from .constants import EXCLUDED_PATHS, UNMATCHED_ENDPOINT


class PrometheusMiddleware:
    """Middleware to collect HTTP metrics for Prometheus.

    Implements RED methodology:
    - Rate: http_requests_total
    - Errors: http_requests_total with status_code >= 400
    - Duration: http_request_duration_seconds

    Additionally tracks:
    - http_requests_in_progress
    - http_request_size_bytes
    - http_response_size_bytes
    """

    def __init__(
        self, get_response: Callable[[HttpRequest], "HttpResponseBase"]
    ) -> None:
        """Initialize middleware.

        Args:
            get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> "HttpResponseBase":
        """Process the request and collect metrics.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response from the view.
        """
        path = request.path

        if self._should_exclude(path):
            return self.get_response(request)

        return self._process_request_with_metrics(request)

    def _should_exclude(self, path: str) -> bool:  # noqa: PLR6301
        """Check if the path should be excluded from metrics.

        Args:
            path: The request path.

        Returns:
            True if the path should be excluded.
        """
        return any(path.startswith(p) for p in EXCLUDED_PATHS)

    def _endpoint(self, request: HttpRequest) -> str:  # noqa: PLR6301
        """Name the URL route that served the request.

        The label must stay bounded no matter what clients send: vulnerability
        scanners probe thousands of made-up paths, and a series per path once
        grew /metrics/ to tens of thousands of lines, long enough to make the
        scrape time out. Every request no route served shares one label.

        The route comes from ``request.resolver_match``, which Django's handler
        sets once it dispatches the request, rather than from resolving the
        path here: this middleware runs before the rest of the stack, so a
        later middleware that swaps ``request.urlconf``, activates a language
        for ``i18n_patterns`` or serves a fallback page would route the request
        differently from a resolve against the root urlconf.

        Args:
            request: The request, after the view chain has handled it.

        Returns:
            The route pattern, e.g. ``/api/v1/lessons/<uuid:uuid>/``, or
            ``UNMATCHED_ENDPOINT``.
        """
        match = request.resolver_match
        if match is None:
            return UNMATCHED_ENDPOINT
        return f"/{match.route}"

    def _process_request_with_metrics(self, request: HttpRequest) -> "HttpResponseBase":
        """Process request and record metrics.

        ``http_requests_in_progress`` carries no endpoint label: it is raised
        before the request is routed, when the route is not yet known.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response from the view.
        """
        from .metrics import (  # noqa: PLC0415
            http_exceptions_total,
            http_request_duration_seconds,
            http_request_size_bytes,
            http_requests_in_progress,
            http_requests_total,
            http_response_size_bytes,
        )

        method = request.method or "UNKNOWN"
        http_requests_in_progress.labels(method=method).inc()

        start_time = time.perf_counter()
        status_code = 500
        response: HttpResponseBase | None = None
        try:
            response = self.get_response(request)
            status_code = getattr(response, "status_code", 500)
        except Exception as e:
            http_exceptions_total.labels(
                endpoint=self._endpoint(request),
                exception=e.__class__.__name__,
            ).inc()
            raise
        else:
            return response
        finally:
            duration = time.perf_counter() - start_time
            http_requests_in_progress.labels(method=method).dec()

            endpoint = self._endpoint(request)
            http_requests_total.labels(
                method=method, endpoint=endpoint, status_code=str(status_code)
            ).inc()
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint
            ).observe(duration)
            http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(
                self._get_request_size(request)
            )

            if response is not None:
                response_size = self._get_response_size(response)
                http_response_size_bytes.labels(
                    method=method, endpoint=endpoint
                ).observe(response_size)

    def _get_request_size(self, request: HttpRequest) -> int:  # noqa: PLR6301
        """Get the size of the request body in bytes.

        Args:
            request: The HTTP request.

        Returns:
            Size in bytes.
        """
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        return 0

    def _get_response_size(self, response: "HttpResponseBase") -> int:  # noqa: PLR6301
        """Get the size of the response body in bytes.

        Args:
            response: The HTTP response.

        Returns:
            Size in bytes.
        """
        content_length = response.get("Content-Length")
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass

        content = getattr(response, "content", None)
        if content is not None:
            return len(content)
        return 0
