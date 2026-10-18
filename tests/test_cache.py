"""Unit tests for the cache key builder (no app, no infra)."""

import pytest
from starlette.requests import Request

from necktie.cache.lifespan import request_key_builder


def _request(query_string: bytes = b"") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/doctor",
        "query_string": query_string,
        "headers": [],
    }
    return Request(scope)


class TestRequestKeyBuilder:
    def test_path_only(self) -> None:
        key = request_key_builder(object, "necktie", request=_request(), response=None)
        assert key == "necktie:/doctor?"

    def test_sorted_query_params(self) -> None:
        key = request_key_builder(
            object, "necktie", request=_request(b"b=2&a=1"), response=None
        )
        assert key == "necktie:/doctor?a=1&b=2"

    def test_repeated_params_preserved(self) -> None:
        key = request_key_builder(
            object, "necktie", request=_request(b"lang=en&lang=zh"), response=None
        )
        assert "lang=en" in key and "lang=zh" in key

    def test_missing_request_raises(self) -> None:
        with pytest.raises(ValueError, match="request is required"):
            request_key_builder(object, "necktie", request=None, response=None)
