# Shared pieces

[`evidence-handoff/`](evidence-handoff/README.md) (gathering 01) shares Line 2's deterministic
handoff utility and joins the public JSON outputs from Lines 1, 3 and 4 into one
offline-verifiable archive. It has no network or third-party dependencies.

```sh
python3 -B shared/evidence-handoff/bundle.py demo
```

[`tx-preflight/`](tx-preflight/README.md) (gathering 02) joins Line 3's offline decoder with Line 1's
read-only RPC validators. It checks an unsigned EIP-1559 transaction against
live state pinned to one block: chain, fees, nonce, ETH for gas, and ERC-20
amount, balance and recipient. Every read is kept as a Line 1 snapshot, so the
same evidence replays offline.

```sh
python3 -B shared/tx-preflight/preflight.py demo
```

The original line folders are unchanged. These are reusable worker tools, not
record viewers.
