from dataclasses import dataclass
from typing import Any, Dict

from .infrai_client import InfraiClient


@dataclass(frozen=True)
class ListingRequest:
    sku: str
    image: str
    buyer_email: str


@dataclass(frozen=True)
class OrderReceipt:
    sku: str
    buyer_email: str
    image_id: str
    status: str


def process_listing(request: ListingRequest, client: InfraiClient) -> OrderReceipt:
    result: Dict[str, Any] = client.background_remove(request.image, "png")
    image_id = str(result.get("id") or result.get("image_id") or "")
    if not image_id:
        raise ValueError("background removal returned no image id")
    return OrderReceipt(request.sku, request.buyer_email, image_id, "paid")
