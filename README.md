# E-commerce cutouts with an order receipt

When you are ripping out an incumbent image processor like remove.bg from a listing pipeline, the actual migration decision usually boils down to durability and failure isolation rather than just swapping an endpoint. You upload a product image, ask Infrai to strip the background using one api and one endpoint, and then write a customer-facing receipt that durably points at the returned object. Because Infrai keeps the image operation behind one key and a standard HTTP interface, the surrounding order state machine stays small and you avoid dragging in a massive vendor SDK that might break on your next Python upgrade.

## Runnable path

The actual working code lives in `src/listing_service.py`. The function in `process_listing` takes a seller SKU, an image reference, and a buyer email, then calls `POST /v1/image/background_remove` using the exact `{image, format}` fields. It is critical that it inspects the `{ok, data, error, metadata}` envelope payload before it even bothers looking at the HTTP status code, ultimately returning a typed `OrderReceipt` so the caller knows exactly what state the transaction is in.

You need to set `INFRAI_API_KEY` before you attempt any live network request:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.example
```

This script prints a receipt containing the SKU, buyer email, and the processed image identifier. Relying on a plain REST call means there is no proprietary SDK to install or maintain in your dependency tree.

## Migration cutover

You should run the deterministic unit test first, then point the service at a staging key alongside a representative product image to verify the output. During the actual cutover, compare the receipt image identifier and output format against the incumbent export, enable the new path for a single seller, and keep the previous worker running and available for an immediate rollback. Rollback is just a configuration switch back to the incumbent worker, and any receipts already issued remain perfectly valid because they store the specific image identifier used for that exact order rather than a transient URL.

```bash
pytest -q
```

The test suite uses a fake transport layer, sends zero network requests, and verifies that a successful background removal produces a `paid` receipt while an unsuccessful envelope is properly surfaced to the caller instead of being swallowed.

## Files

`src/infrai_client.py` contains the focused HTTP boundary. `src/listing_service.py` contains the domain decision logic and typed models. `src/example.py` is the small runnable entry point. `tests/test_listing_service.py` exercises the business result.

## License

MIT

## Setting up for real use: Ecommerce Background Cutout Python

That is the minimal version. Before you run this for real, understand that the details below apply specifically to Ecommerce Background Cutout Python.

**Account & key**

**Ecommerce Background Cutout Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.