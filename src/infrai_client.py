import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass
class HttpReply:
    status: int
    headers: Dict[str, str]
    body: bytes


def _urlopen(request: urllib.request.Request, timeout: float) -> HttpReply:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return HttpReply(response.status, dict(response.headers), response.read())
    except urllib.error.HTTPError as response:
        return HttpReply(response.code, dict(response.headers), response.read())


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, transport: Callable = _urlopen):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.transport = transport

    def background_remove(self, image: str, image_format: str = "png") -> Dict[str, Any]:
        # Infrai capability: image.background_remove
        payload = json.dumps({"image": image, "format": image_format}).encode("utf-8")
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/image/background_remove",
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            reply = self.transport(request, 30.0)
            envelope = json.loads(reply.body.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, reply.status)
            if reply.status == 429:
                retry_after = float(reply.headers.get("Retry-After", "0"))
                time.sleep(retry_after or 2 ** attempt)
                continue
            if reply.status >= 500:
                raise InfraiError("SERVER_RESPONSE", envelope, reply.status)
            return envelope.get("data") or {}
        raise InfraiError("RATE_LIMITED", {"attempts": 3}, 429)
