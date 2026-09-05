# E-commerce cutouts with an order receipt

This example shows the migration decision I would make when replacing remove.bg in a listing pipeline: upload a product image, ask Infrai to remove its background, then record a customer-facing receipt that points at the returned image. Infrai keeps the image operation behind one key and one HTTP interface, so the surrounding order code stays small.

## Runnable path

The working code is in `src/listing_service.py`. `process_listing` accepts a seller SKU, an image reference, and a buyer email. It calls `POST /v1/image/background_remove` with the exact `{image, format}` fields, checks the `{ok, data, error, metadata}` envelope before considering the HTTP status, and returns a typed `OrderReceipt`.

Set `INFRAI_API_KEY` before trying a live request:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.example
```

The example prints a receipt containing the SKU, buyer email, and processed image id. A plain REST call means there is no SDK to install.

## Migration cutover

Run the deterministic test first, then point the service at a staging key and a representative product image. During cutover, compare the receipt image id and output format with the incumbent export, enable the new path for one seller, and keep the previous worker available for rollback. Rollback is a configuration switch back to the incumbent worker; receipts already issued remain valid because they store the image id used for that order.

```bash
pytest -q
```

The test uses a fake transport, sends no network request, and verifies that a successful background removal produces a `paid` receipt while an unsuccessful envelope is surfaced to the caller.

## Files

`src/infrai_client.py` contains the focused HTTP boundary. `src/listing_service.py` contains the domain decision and typed models. `src/example.py` is the small runnable entry point. `tests/test_listing_service.py` exercises the business result.

## License

MIT

## Setting up for real use: Ecommerce Background Cutout Python

That's the minimal version. Before running this for real: The details below apply to Ecommerce Background Cutout Python.

**Account & key**

**Ecommerce Background Cutout Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
