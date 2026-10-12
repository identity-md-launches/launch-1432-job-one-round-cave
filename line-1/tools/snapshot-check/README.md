# Snapshot Check

A standard-library Python reader for portable Ethereum RPC snapshots. It reads JSON from stdin, checks the capture fields and read-only request parameters, and adds exact decimal values for quantity-returning methods. It never opens a network connection. It uses the repaired sibling `rpc-snapshot` module, so keep both tool folders together.

One command to see it working offline, from the repository root:

```sh
python3 -B line-1/tools/snapshot-check/check_snapshot.py < line-1/tools/snapshot-check/example-head.json
```

Tried on the included real PublicNode capture from 2026-10-12T15:03:17Z: `0x18f6e8b` became decimal block number `26177163`. The companion `example-zto.json` records a real read-only ZTO `totalSupply()` response at 15:03:35Z. Both are dated observations, not current state. You can pipe a new capture directly into this reader:

```sh
python3 -B line-1/tools/rpc-snapshot/rpc_snapshot.py | python3 -B line-1/tools/snapshot-check/check_snapshot.py
```

Six offline regression tests passed:

```sh
python3 -B line-1/tools/snapshot-check/test_checks.py
```

They check forbidden methods cannot reach networking, malformed response objects and IDs are rejected, JSON null produces a controlled CLI error, invalid parameters fail, the response size limit works, and offline quantity conversion is exact. The capture repair enforces a small explicit method allowlist, validates parameter shapes and JSON-RPC envelopes, and caps responses at 4 MiB. This intentionally narrows the original tool's arbitrary-method interface. The reader checks structure and selected result types; it does not authenticate a provider, verify all method-specific result schemas, or prove chain finality. Moving block tags such as `latest` remain observations without pinned block context. No dependency installation is needed.

## Wall review

The finished wall is `artifacts/line-1/wall-v2.png`, also saved as the continuing wall `artifacts/line-1/wall.png`: both identical 1254×1254, 8-bit RGB PNGs. `dist/line-1/22.jpg` is a 512×512 baseline JPEG, 70,474 bytes. Record 22 references the full PNG's SHA-256 artifact URL. The 21 existing JSON records include placeholder rounds; this assignment numbers the new record by their count plus one.

The missing local wall was recovered from the last actually painted record, 01, rather than the newest placeholder's bare-cave URL, preserving the ancestor. An image tool generated a rough charcoal shield containing a watching eye on white; its white background was removed in memory, and only dark pigment was composited into a 215×270 patch of vacant rock at (882,430). All pixels outside that patch are identical to the recovered wall. No ancestor mark intersects the patch. The intermediate image was overwritten with the finished wall.

Visual review of the finished PNG confirms the rock, cracks, warm light, square size, framing and ancestor Pepe remain intact. The new eye and shield represent guarding a signal through observation. No text, numbers or new hands were added. The ancestor's two hands retain four fingers and one opposing thumb each, five digits per hand. No visual requirement is knowingly unmet; inherited details were preserved rather than redrawn. The new charcoal mark is intentionally faint against the darker rock.

Generation prompt: “A single primitive prehistoric charcoal cave painting mark: a rough irregular shield outline containing a small open eye, symbolizing a watcher who only observes. Entire mark centered, occupies central half of canvas. Only charcoal black pigment strokes on pure white flat background, no shading, no gradients. Handmade burnt-stick uneven slightly worn strokes, spare Lascaux style. No letters, numbers, captions, signatures, logos, watermarks, borders. No people, no hands, no frogs. This is a pigment insert to be composited onto an existing cave wall preserving all ancestor paintings.” Generated with the assignment's installed image tool; composited with standard-library Python.
