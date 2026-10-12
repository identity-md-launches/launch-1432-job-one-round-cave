# RPC Snapshot

`rpc_snapshot.py` makes one read-only request to a public Ethereum JSON-RPC endpoint and prints the request method, parameters, UTC capture time, endpoint, and response result in portable JSON. It uses only the Python standard library and sends the User-Agent `Pepeolithic-RPC-Snapshot/1.0 (read-only public data)`. The default method is `eth_blockNumber`; pass another method and its JSON parameter array positionally when needed.

## Try it

```sh
python3 line-1/tools/rpc-snapshot/rpc_snapshot.py
```

I ran that command against the live default endpoint. It returned `eth_blockNumber` result `0x18f6c5a` at capture time `2026-10-12T13:10:23Z`. The current result changes as the chain advances.

To read ZTO's live `totalSupply()` using a read-only `eth_call`, run:

```sh
python3 line-1/tools/rpc-snapshot/rpc_snapshot.py eth_call '[{"to":"0xd782bdea4ef02a0bd391eb9089470c8080f0a68e","data":"0x18160ddd"},"latest"]'
```

I also ran this against the real ZTO contract. At `2026-10-12T13:11:02Z`, it returned `0x0000000000000000000000000000000000000000033b2e3c9fd0803ce8000000`.

The wall paired with this tool is `artifacts/line-1/wall.png`: a 1254×1254 RGB PNG, with a 512×512 JPEG copy at `dist/line-1/01.jpg`. It preserves the cave's square size, rock texture and framing. The painting has Pepe's broad mouth and heavy-lidded eyes and shows him holding a veined stone. Both hands show four separated fingers and one opposing thumb each. No visual requirements are knowingly unmet.

## Round 22 repair

The capture command now accepts only the explicit read-only methods in `READ_METHODS`, with checked parameter counts and shapes. Signing, sending, node administration, filter creation and unknown methods are rejected before networking. `eth_call` accepts only `to`, optional `data`, and a block tag. HTTPS endpoints are required; response bodies are limited to 4 MiB. JSON-RPC version, integer request ID and exclusive result/error fields are checked, including null and malformed response objects. A null *result* remains valid for a missing transaction or block.

Live default-head and ZTO supply commands succeeded again on 2026-10-12 at 15:03 UTC. Six offline checks pass via `python3 -B line-1/tools/snapshot-check/test_checks.py`. The new sibling tool can inspect saved snapshots offline. Snapshots are provider observations; they do not prove authenticity or finality, and `latest` is not pinned state.
