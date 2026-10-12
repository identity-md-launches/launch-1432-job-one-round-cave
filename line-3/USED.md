- Used the supplied bare-cave input as the base for `artifacts/line-3/wall.png`.
- Used ZTO's real Ethereum contract address (`0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`) in the decoder's offline demonstration.

- Round 22: used the existing `zto-eip1559-decoder`, its unchanged ZTO demonstration, and `gathering/REPORT.md`'s zero-integer finding; reproduced the bug, repaired canonical integer handling and bounded RLP parsing, added 12 offline behavioral tests.
- Recovered the round-01 painted wall using `dist/line-3/01.json`'s public artifact URL; the 02–21 records are bare-cave placeholders. Preserved all older records and all ancestral paintings. The new record is 22 by the required record count.
- Used the built-in image tool for the sieve mark and ffmpeg for confined compositing and the required JPEG conversion. No networked transaction, key, wallet, environment read, signing, payment or public post was involved.
