# ERC-20 Transfer Window

`transfer_window.py` captures a bounded, ordered window of real Ethereum `Transfer` events for an ERC-20 without a wallet, key, indexer, transaction, or filesystem input. It uses only the Python standard library and makes read-only JSON-RPC requests with the dedicated User-Agent `Pepeolithic-ERC20-Transfer-Window/2.0 (read-only public data)`.

ZTO (`0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`) is the default token. `--token imd` selects IMD (`0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7`). The result includes the chain head seen at capture, the exact inclusive block range, the on-chain `decimals()` result pinned to the range's final block, and every matching log in block/log-index order. Token quantities are reported both as exact integer base units and rendered decimal units.

## Try it

```sh
python3 line-4/tools/erc20-transfer-window/transfer_window.py --latest-window 12
```

I ran that command against the live default public endpoint. It returned a read-only JSON document for ZTO, including the endpoint, a 12-block inclusive range ending at the observed head, the contract's on-chain decimal count, and the matching transfer log count. The head, range, and events naturally change as Ethereum advances.

For an independently reproducible historical lookup, choose a bounded inclusive range (at most 2,000 blocks):

```sh
python3 line-4/tools/erc20-transfer-window/transfer_window.py --from-block 26124500 --to-block 26124511
```

The tool validates range limits before networking and rejects malformed RPC results rather than quietly guessing. It is a log window reader, not a balance calculator: it does not infer an address's full balance from a partial range. A public endpoint can rate-limit or retain limited historical logs; use `--rpc` to point at another public Ethereum JSON-RPC endpoint when necessary.

## Wall asset

The accompanying finished wall is `artifacts/line-4/wall.png`, a 1254×1254 RGB PNG; `dist/line-4/01.jpg` is its 512×512 RGB JPEG copy. I visually reviewed both after generation. The added ochre, charcoal, and chalk cave figure is Pepe with his broad mouth and heavy-lidded eyes, studying an unlettered stone and nearby unlettered pebbles. The original rock, cracks, warm torchlight, and cave framing remain visible. Both visible hands were reviewed as five-digit hands (four fingers and a thumb). No letters, numbers, captions, signatures, logos, watermarks, artificial borders or frames, photographs, 3D renders, real people, political symbols, or hateful symbols are present. No visual requirements are knowingly unmet.

## Round 22: validated evidence

The gathering's seven Line 4 findings are repaired in this existing tool. Every
returned event must have the selected emitter, the ERC-20 Transfer signature,
exactly three topics, correctly padded hex addresses, exactly 32 bytes of value
data, canonical nonnegative hex indices, valid transaction/block hashes, an
explicit `removed: false`, and a block inside the requested range. Wrong or
malformed events fail the whole capture with exit 2; they are never silently
filtered into a misleading empty result. Events with the same block hash,
transaction hash and log index are counted once; conflicting identities fail.
`raw_logs` retains the original response, including duplicate entries, and
`duplicate_count` explains the difference from `transfer_count`.

Before reading logs the tool requires Ethereum mainnet (`eth_chainId = 1`),
rejects future ranges, and captures both boundary block hashes. It reads
`decimals()` at `to_block` and rechecks the boundary hashes after reading the
logs to detect a reorg during capture. The result adds `schema_version: 2`,
`chain_id`, `decimals_block`, and both boundary anchors while keeping the original
summary fields. The transport restricts RPC methods to the five public reads
used here, requires credential-free HTTPS URLs, checks JSON-RPC version and
request ID, and caps responses at 16 MiB and logs at 20,000. Exceeding a limit
fails instead of truncating. No third-party dependencies are needed.

One command that works **offline**, including in the verification environment:

```sh
python3 -B line-4/tools/erc20-transfer-window/test_transfer_window.py
```

Tried on 2026-10-12: all 15 tests passed. The offline suite uses two real ZTO
logs retained from the gathering's dated dRPC capture in `observed_logs.json`.
It mutates those logs to reproduce the gathering failures and exercises exact
unit formatting, duplicates, conflicting block identities, wrong chains,
malformed responses, empty responses, resource limits, and capture-time reorgs.
Its transport and minimal header responses are explicitly mocked; no RPC is
contacted by the test command.

I also ran the live 12-block command above. PublicNode returned three ZTO
transfers in inclusive blocks **26177298–26177309**, with 18 decimals, at
**2026-10-12T15:32:50Z**. `live-zto.json` retains this capture. Repeating that exact
range through dRPC produced the same three decoded events and both boundary
hashes, retained in `live-zto-crosscheck.json`:

```sh
python3 -B line-4/tools/erc20-transfer-window/transfer_window.py --from-block 26177298 --to-block 26177309 --rpc https://eth.drpc.org
```

These dated captures are public observations, not current balances. Even a
validated empty response is only a provider observation: a provider can omit
logs without announcing it. Boundary checks detect observed changes during
capture, but do not prove finality, verify interior block hashes independently,
or prove log completeness. No balance reconstruction is attempted. If a public
provider rejects a range, retry with a smaller range or another public RPC;
the tool does not hide the failure or automatically mix provider responses.

Round 22's final wall is `artifacts/line-4/wall.png`, with an identical named
output at `artifacts/line-4/wall-v2.png`; `dist/line-4/22.jpg` is the 512-pixel
JPEG. See `line-4/IMAGE-REVIEW.md` and `line-4/image-review.json` for dimensions,
preservation checks, prompt and visual review.
