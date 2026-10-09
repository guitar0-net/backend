# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the Prometheus middleware."""

from secrets import token_hex

import pytest
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.test import RequestFactory
from django.urls import ResolverMatch

from apps.ops.middleware import PrometheusMiddleware


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


def _view(request: HttpRequest) -> HttpResponse:
    return HttpResponse()


def _routed_to(route: str) -> PrometheusMiddleware:
    """Middleware in front of a stub handler that dispatched to ``route``."""

    def get_response(request: HttpRequest) -> HttpResponse:
        request.resolver_match = ResolverMatch(_view, (), {}, route=route)
        return HttpResponse("OK", status=200)

    return PrometheusMiddleware(get_response)


def _random_method() -> str:
    return f"PROBE{token_hex(4).upper()}"


@pytest.fixture
def middleware() -> PrometheusMiddleware:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK", status=200)

    return PrometheusMiddleware(get_response)


def test_middleware_returns_response(
    middleware: PrometheusMiddleware, request_factory: RequestFactory
) -> None:
    request = request_factory.get("/api/test/")
    response = middleware(request)
    assert response.status_code == 200


def test_middleware_excludes_metrics_path(
    middleware: PrometheusMiddleware, request_factory: RequestFactory
) -> None:
    request = request_factory.get("/metrics/")
    response = middleware(request)
    assert response.status_code == 200


def test_middleware_labels_a_request_with_the_route_the_handler_dispatched_to(
    request_factory: RequestFactory,
) -> None:
    from apps.ops.metrics import http_requests_total

    route = f"гитара-{token_hex(4)}/<int:pk>/"
    method = _random_method()
    _routed_to(route)(request_factory.generic(method, f"/{token_hex(4)}/скан/"))

    assert (
        http_requests_total.labels(
            method=method, endpoint=f"/{route}", status_code="200"
        )._value.get()
        == 1
    )


def test_middleware_labels_every_request_no_route_served_alike(
    middleware: PrometheusMiddleware, request_factory: RequestFactory
) -> None:
    from apps.ops.metrics import http_requests_total

    method = _random_method()
    for _ in range(5):
        middleware(
            request_factory.generic(method, f"/wp-admin/{token_hex(4)}-гитара.php")
        )

    assert (
        http_requests_total.labels(
            method=method, endpoint="<unmatched>", status_code="200"
        )._value.get()
        == 5
    )


def test_metrics_recording_records_duration(request_factory: RequestFactory) -> None:
    from apps.ops.metrics import http_request_duration_seconds

    route = f"курсы-{token_hex(4)}/<uuid:uuid>/"
    method = _random_method()
    _routed_to(route)(request_factory.generic(method, f"/{token_hex(4)}/"))

    assert (
        http_request_duration_seconds.labels(
            method=method, endpoint=f"/{route}"
        )._sum.get()
        > 0
    )


def test_metrics_recording_tracks_in_progress_requests(
    middleware: PrometheusMiddleware, request_factory: RequestFactory
) -> None:
    from apps.ops.metrics import http_requests_in_progress

    method = _random_method()
    middleware(request_factory.generic(method, f"/{token_hex(4)}-урок/"))

    assert http_requests_in_progress.labels(method=method)._value.get() == 0


def test_request_size_records_from_header(request_factory: RequestFactory) -> None:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    middleware = PrometheusMiddleware(get_response)
    request = request_factory.post(
        "/api/data/",
        data="test data",
        content_type="text/plain",
    )
    request.META["CONTENT_LENGTH"] = "100"

    size = middleware._get_request_size(request)
    assert size == 100


def test_request_size_returns_zero_for_missing_content_length(
    request_factory: RequestFactory,
) -> None:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    middleware = PrometheusMiddleware(get_response)
    request = request_factory.get("/api/data/")
    if "CONTENT_LENGTH" in request.META:
        del request.META["CONTENT_LENGTH"]

    size = middleware._get_request_size(request)
    assert size == 0


def test_request_size_returns_zero_for_invalid_content_length(
    request_factory: RequestFactory,
) -> None:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    middleware = PrometheusMiddleware(get_response)
    request = request_factory.post("/api/data/", content_type="text/plain")
    request.META["CONTENT_LENGTH"] = "invalid"

    size = middleware._get_request_size(request)
    assert size == 0


def test_response_size_records_from_content() -> None:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("Hello World")

    middleware = PrometheusMiddleware(get_response)
    response = HttpResponse("Hello World")

    size = middleware._get_response_size(response)
    assert size == len(b"Hello World")


def test_response_size_records_from_header() -> None:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    middleware = PrometheusMiddleware(get_response)
    response = HttpResponse("x" * 1000)
    response["Content-Length"] = "500"

    size = middleware._get_response_size(response)
    assert size == 500


def test_response_size_returns_zero_for_invalid_content_length_header() -> None:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    middleware = PrometheusMiddleware(get_response)
    response = StreamingHttpResponse(iter([b"chunk"]))
    response["Content-Length"] = "invalid"

    size = middleware._get_response_size(response)
    assert size == 0


def test_response_size_returns_zero_for_response_without_content() -> None:
    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    middleware = PrometheusMiddleware(get_response)
    response = StreamingHttpResponse(iter([b"chunk"]))

    size = middleware._get_response_size(response)
    assert size == 0


def test_exception_handling_records_exception_metric(
    request_factory: RequestFactory,
) -> None:
    from apps.ops.metrics import http_exceptions_total

    class CustomError(Exception):
        pass

    route = f"аккорды-{token_hex(4)}/<int:pk>/"

    def get_response(request: HttpRequest) -> HttpResponse:
        request.resolver_match = ResolverMatch(_view, (), {}, route=route)
        raise CustomError

    with pytest.raises(CustomError):
        PrometheusMiddleware(get_response)(request_factory.get(f"/{token_hex(4)}/"))

    assert (
        http_exceptions_total.labels(
            endpoint=f"/{route}", exception="CustomError"
        )._value.get()
        == 1
    )
