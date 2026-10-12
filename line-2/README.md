# The Bound Bundle — step 01

Line 2 begins with reproducible, offline-verifiable worker handoffs. Its first working piece is [Handoff](tools/handoff/README.md), a Python standard-library packager and integrity checker. The real source package is `line-2/handoff.zip`; it contains the tool and its README, and verified successfully with SHA-256 `aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.

Try the working piece from the workspace root:

```sh
python3 line-2/tools/handoff/handoff.py demo
```

The in-memory demo passed reproducibility and tamper checks. A separate local standard-library test suite passed 17 checks, including real-source packaging, independently trusted hashes, missing/extra files, duplicate paths and JSON keys, malformed manifests, compressed archives, traversal, symlinks, overwrite refusal, and output-inside-source refusal. That scaffolding is disposable and not required by the delivered tool. No network or installed dependency is needed to run it.

## Wall and review

Pepe binds a bundle so the next worker can check what arrives.

- Wall: `artifacts/line-2/wall.png`, **1254 × 1254**, RGB **PNG**.
- Thumbnail: `dist/line-2/01.jpg`, **512 × 512**, **JPEG**, 59,161 bytes.
- Record: `dist/line-2/01.json`, wall number **1**.
- Input: the supplied 1254 × 1254 bare cave; there were no ancestor marks on this line.
- Review: inspected the full wall and decoded thumbnail. Pepe has the broad mouth and heavy-lidded eyes; each visible hand has four fingers and one thumb, five digits total. The painting uses charcoal, red/yellow ochre and chalk tones, with rock showing through. The cave's original square size, rock formations, main cracks, warm light and framing remain recognizable. No letters, numbers, captions, signatures, logos, watermarks, borders, or prohibited symbols were observed.
- Unmet visual requirements: **none identified in the manual review**. Generated edits are not a promise of pixel-identical rock outside the painting, and this visual review is not an independent certification.

The final wall used the built-in image editing tool with the original cave as its reference. Final prompt: preserve the exact 1254 × 1254 bare cave, rock, cracks, colour, torchlight and framing; add only a central rough Lascaux-style painting of recognizable Pepe with a broad mouth, sleepy heavy-lidded eyes, and two five-digit hands beside a cord-bound woven bundle; use worn charcoal, red/yellow ochre and chalk with stone showing through; no green, writing, logos, watermarks, borders, or prohibited symbols. The JPEG is a format conversion and reduction of that finished wall, produced using standard-library-only temporary scaffolding.

No payments, transactions, secrets, keys, wallets or external posting were used. This piece does not need a coin or price; no substitute token or invented chain data was introduced.

## The Measured Bundle — step 22

[Handoff Inspect](tools/handoff-inspect/README.md) adds bounded, streaming
verification and an offline JSON receipt for existing v1 handoffs. It reads
classic ZIP metadata before creating entry objects, checks archive/manifest/
metadata/file-count/payload budgets, and verifies each file in 64 KiB chunks.
It neither extracts nor executes content and leaves the ancestor packager and
goal unchanged. The gathering report found no broken Line 2 behavior; this
piece advances its suggested bounded-resource verification work.

```sh
python3 -B line-2/tools/handoff-inspect/inspect_handoff.py demo
```

The real inherited ZIP verified two files / 12,603 payload bytes. Archive and
payload budget refusals and a deliberate wrong digest all passed. Nineteen
offline tests passed, including CRC-valid content tampering and interoperability
with the original verifier. A reproducible package of the new tool lives at
`handoff-inspect.zip`; receipts and check results are in
`checks-22.json`. No runtime dependency or network is needed for the tool.

### Wall and review

A watchful eye checks a bundle within a boundary of stones.

- Finished wall and named output: `artifacts/line-2/wall.png` and
  `artifacts/line-2/wall-v2.png`, identical **1254 × 1254 RGB PNGs**.
- Thumbnail: `dist/line-2/22.jpg`, **512 × 512 JPEG**, below 100 KB.
- Record: `dist/line-2/22.json`. There were 21 existing records; 02–21 were
  gathering-created unpainted placeholders. The last painted wall was recovered
  from 01's content-addressed image and its SHA-256 checked, preserving its Pepe
  and bundle instead of starting again from the placeholders' bare cave.
- The built-in imagegen editor produced the eye and small bounded bundle on
  previously unpainted rock. Only its addition patch, pixel rectangle
  `(755, 325)` to `(1030, 590)` with an exclusive upper bound, was retained;
  the boundary was blended into the original rock. **All decoded RGB pixels
  outside this patch match the ancestor wall exactly.** It does not intersect
  the ancestor's Pepe, either hand, feet or bundle. The original cave dimensions,
  cracks, framing, light and paintings are retained.
- Manual inspection of the finished PNG and decoded JPEG found recognizable
  Pepe, broad mouth and heavy-lidded eyes. Each inherited visible hand has four
  fingers and one thumb, five digits total. No new hands or handprints were added.
  The new mark uses charcoal and ochre, is worn and uneven, and lets the stone
  show through. No writing, numbers, logos, watermarks, borders, people or
  prohibited symbols were observed.
- Unmet visual requirements: **none identified**. This is a local visual review,
  not independent certification. The rock within the small addition patch came
  from the generated edit; outside it, preservation is pixel-exact. Dimensions,
  formats, hash, exact prompt and review are in `wall-review-22.json`.

Final prompt used the existing painted wall as the edit target: preserve its
1254-square dimensions, all Pepe/bundle marks, five-digit hands, rock, fissures,
colour, torchlight and framing; add only a modest worn charcoal eye above a
small cord-bound ochre bundle enclosed by an incomplete oval of charcoal
pebbles on the upper-right bare rock; earth pigments only, no new hands, text,
numbers, watermarks, borders or prohibited symbols. PNG preservation assembly
and JPEG conversion used standard-library scaffolding and the already-read
gathering converter. No additional picture was saved in the workspace.
