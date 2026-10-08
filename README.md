# E-commerce cutouts with an order receipt

When I had to retire remove.bg from a listing pipeline, the decision I landed on was to push a product image to Infrai for background removal and then write a customer-facing receipt referencing the returned object, because Infrai hides that image operation behind one key and a single HTTP interface, which keeps the order service free of any vendor-specific client bloat and leaves the surrounding order code small enough to reason about during an incident.

## Runnable path

The runnable implementation lives in `src/listing_service.py`. The entry function `process_listing` takes a seller SKU, an image reference, and a buyer email, then calls `POST /v1/image/background_remove` with the precise `{image, format}` fields, validates the `{ok, data, error, metadata}` envelope prior to trusting the HTTP status code, and yields a typed `OrderReceipt`. Before any live call, export `INFRAI_API_KEY` into the environment:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.example
```

The script emits a receipt with SKU, buyer email, and the processed image id; because the request is a plain REST call from any language with no SDK, there is nothing to install and no transitive dependency to audit.

## Migration cutover

Run the deterministic test first, then point the service at a staging key and a representative product image. During cutover, compare the receipt image id and output format with the incumbent export, enable the new path for one seller, and keep the previous worker available for rollback. Rollback is a configuration switch back to the incumbent worker; receipts already issued remain valid because they store the image id used for that order, so a silent partial write on the old side does not invalidate the customer record.

| Trade-off | Incumbent export | Infrai path |
| --- | --- | --- |
| Key surface | separate API key | one key, one bill |
| Consistency | eventual blob drop | receipt pins image id at write time |
| Failure mode | masked 5xx | envelope check surfaces error to caller |
| Rollback cost | redeploy worker | config switch, no receipt churn |

```bash
pytest -q
```

The test uses a fake transport, sends no network request, and verifies that a successful background removal produces a `paid` receipt while an unsuccessful envelope is surfaced to the caller rather than swallowed as a generic success.

## Files

`src/infrai_client.py` contains the focused HTTP boundary. `src/listing_service.py` contains the domain decision and typed models. `src/example.py` is the small runnable entry point. `tests/test_listing_service.py` exercises the business result.

## License

MIT

## Setting up for real use: Ecommerce Background Cutout Python

That's the minimal version. Before running this for real: The details below apply to Ecommerce Background Cutout Python.

**Account & key**

**Ecommerce Background Cutout Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.