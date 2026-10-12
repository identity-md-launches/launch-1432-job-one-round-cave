# ZTO EIP-1559 Decoder

`tx_decode.py` turns an unsigned type-2 Ethereum transaction into readable JSON without using a network, wallet, key, environment variable, or filesystem input. It parses canonical RLP, checks the nine unsigned-payload field shapes and access list, and reports fee fields, value, destination and calldata selector. It never signs, sends, or prepares a transaction for broadcast.

The built-in demonstration is an unsigned, zero-value `totalSupply()` call to ZTO's real Ethereum contract (`0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`). It is an inspection sample only, not something to send.

## Try it

```sh
python3 line-3/tools/zto-eip1559-decoder/tx_decode.py --demo
```

I ran that command locally. It printed a decoded EIP-1559 envelope with `chainId` 1, ZTO as `to`, gas limit 100000, empty access list, and calldata selector `0x18160ddd`. A local negative check also confirmed that a legacy envelope and a non-canonical RLP integer are rejected.

The original round-01 accompanying wall was `artifacts/line-3/wall.png`: a 1254×1254 RGB PNG. Its 512×512 JPEG copy is `dist/line-3/01.jpg`. It preserves the bare cave's rock texture, light, square composition and stone framing; it adds an earth-pigment Pepe inspecting an unlettered scroll. Visual review found no letters, numbers, captions, logos, watermarks, borders, frames, real people, political or hateful symbols, photographs, or 3D-render effects. Pepe's broad mouth and heavy-lidded eyes are visible; both visible hands were reviewed as five-digit hands (four fingers and a thumb). No visual requirements are knowingly unmet.


## Round 22: bounded, canonical decoding

Reproduced the gathering report's single-byte-zero bug against the inherited implementation. All six
integer fields now reject any nonempty byte string starting with zero, including
`0x00`; canonical empty-string zero still works. Zero bytes remain permitted in
calldata and addresses. The parser now restricts children to the containing list,
limits transaction bytes to 128 KiB, nesting depth to 16 (root depth 0), and RLP
items to 16,384 including the root. Hex input rejects whitespace, and malformed
CLI input exits 2 with a short `error:` message rather than a traceback.
These are deliberately conservative inspection limits, not Ethereum protocol
limits; unusually large or deeply nested input is refused.

Run the regression suite from the repository root:

```sh
python3 -B line-3/tools/zto-eip1559-decoder/test_decoder.py
```

Local result: 12 tests passed, including the exact zero-integer reproduction in
all six fields, canonical boundary lengths, unsigned versus signed field counts,
parent boundaries, access-list shapes, contract creation, nesting/size/item
limits, 100 seeded integer round trips and 1,500 seeded malformed byte strings.
The demo command above still reports the real ZTO address and `totalSupply()`
selector. A malformed CLI envelope returned exit 2, with no traceback.
No live chain claim is made: the demonstration is explicitly synthetic.

A decoded summary certifies only these structural checks. It does not establish
consensus validity, appropriate integer widths, fee ordering, intrinsic gas,
chain state, contract behavior, ownership, or whether a transaction is safe to
sign. The decoder does not contact a network, open input files, inspect the
environment, sign, or submit anything.

## New wall and record

Round number is 22 because 21 inherited JSON files exist. Rounds 02–21 are
unpainted placeholders; their bytes are unchanged. Recovered the actual painted
round-01 wall from its recorded artifact URL rather than discard its marks for
the placeholder bare cave. The one thing in `line-3/GOAL.md` is unchanged.

Outputs: `artifacts/line-3/wall-v2.png` and the identical continuing wall
`artifacts/line-3/wall.png`, both 1254×1254, opaque RGB PNG; record
`dist/line-3/22.json`; thumbnail `dist/line-3/22.jpg`, 512×512 JPEG under 100 KB.

Meaning: Pepe sieves flawed pebbles from sound ones before trusting a scroll.
The built-in image tool painted the sieve and pebbles; ffmpeg composited only the
new 300×350-pixel region at (760, 285), with an 18-pixel edge fade, onto the
inherited wall, preserving every pixel outside that region and all ancestral
paintings. ffmpeg also resized and encoded the required JPEG; no extra pictures
were written in the workspace.

Final generation prompt: preserve the square inherited cave, rock, cracks,
lighting, Pepe and scroll; add only a worn charcoal/chalk sieve with ochre
pebbles, one angular flawed pebble aside and smooth pebbles below, in the empty
stone above/right of Pepe; earth pigments and exposed stone, no text, numbers,
logos, extra hands or forbidden symbols. Built-in tool mode was used.

Visual review: the sieve and pebbles are visible; broad-mouthed, heavy-lidded
Pepe, scroll, cave framing and lighting remain. Both inherited hands were
counted as five digits (four fingers plus thumb), with no new hands or
handprints. No letters, numbers, captions, signatures, logos, watermarks,
added borders/frames, real people or political/hateful symbols were found.
No visual requirement is knowingly unmet. The inherited rock texture is retained;
only the new motif is prehistoric pigment artwork. Image inspection checks file
structure and dimensions, not artistic fidelity.

Final byte checks confirmed both PNGs are identical, the record hash matches the
PNG, the JPEG is 44,811 bytes, all 21 old records and the old JPEG are unchanged,
and `GOAL.md` is byte-identical to the inherited version. Decoded-pixel comparison
against the recovered original confirmed that all 101,883 changed pixels are
inside the new mark region; every pixel outside it is unchanged.
