import json

from src.infrai_client import HttpReply, InfraiClient, InfraiError
from src.listing_service import ListingRequest, process_listing


def test_successful_cutout_creates_paid_receipt():
    def transport(request, timeout):
        assert request.method == "POST"
        payload = json.loads(request.data.decode())
        assert payload == {"image": "img_123", "format": "png"}
        return HttpReply(200, {}, json.dumps({"ok": True, "data": {"id": "cut_9"}, "error": None, "metadata": {}}).encode())

    receipt = process_listing(ListingRequest("SKU-1", "img_123", "buyer@test"), InfraiClient("test-key", transport))
    assert receipt.status == "paid"
    assert receipt.image_id == "cut_9"


def test_rejected_envelope_is_client_error():
    def transport(request, timeout):
        return HttpReply(400, {}, json.dumps({"ok": False, "data": None, "error": {"code": "BAD_REQUEST"}, "metadata": {}}).encode())

    try:
        process_listing(ListingRequest("SKU-1", "bad", "buyer@test"), InfraiClient("test-key", transport))
    except InfraiError as error:
        assert error.status == 400
    else:
        raise AssertionError("expected InfraiError")
