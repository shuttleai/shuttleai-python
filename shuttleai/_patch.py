import types
from typing import Any

import httpx
import orjson
from httpx._content import ByteStream


def _patch_httpx() -> None:
    original_encode_json = httpx._content.encode_json

    def new_encode_json(json: Any) -> tuple[dict[str, str], ByteStream]:
        if not isinstance(json, bytes):
            return original_encode_json(json)
        return {
            "Content-Type": "application/json",
            "Content-Length": str(len(json)),
        }, ByteStream(json)

    httpx._content.encode_json = new_encode_json

    original_json = httpx._models.Response.json

    def new_json(self: httpx._models.Response, **kwargs: Any) -> Any:
        try:
            return orjson.loads(self.content, **kwargs)
        except orjson.JSONDecodeError:
            return original_json(self, **kwargs)

    setattr(
        httpx._models.Response,
        "json",
        types.MethodType(new_json, httpx._models.Response)
    )
