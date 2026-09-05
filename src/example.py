import os

from .infrai_client import InfraiClient
from .listing_service import ListingRequest, process_listing


def main() -> None:
    client = InfraiClient(os.environ.get("INFRAI_API_KEY"))
    receipt = process_listing(
        ListingRequest(
            "SKU-RED-MUG",
            {
                "base64": (
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
                    "YAAAAAYAAjCB0C8AAAAASUVORK5CYII="
                )
            },
            "buyer@example.test",
        ),
        client,
    )
    print(receipt)


if __name__ == "__main__":
    main()
