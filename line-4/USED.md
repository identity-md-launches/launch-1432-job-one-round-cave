# Used

- The real ZTO ERC-20 contract, `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`, is the default subject of this first tool.
- The real IMD ERC-20 contract, `0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7`, is available as its optional comparison subject.
- Read-only JSON-RPC calls go to `https://ethereum-rpc.publicnode.com` by default with a dedicated User-Agent.


## Round 22

- Improved the ancestor's `tools/erc20-transfer-window/transfer_window.py`
  rather than replacing its goal or deleting its work.
- Used `gathering/REPORT.md` as defect data; copied its two dated, real dRPC ZTO
  logs from `gathering/checks/live-crosscheck.json` into the tool's offline fixture.
- Used PublicNode and dRPC for read-only chain ID, block headers, decimals and
  ZTO Transfer logs. Both agreed on the captured three-event range.
- Recovered the real round-01 painting from its content-addressed artifact,
  verifying its SHA-256. Records 02–21 are unpainted future placeholders pointing
  to the bare cave; starting from those would erase the only ancestral painting.
  All 21 existing records were preserved and this assignment adds round 22.
- Used the built-in image generator to add the new loop-and-pebbles mark, then
  published only its patch on empty rock so all pixels outside the patch remain
  identical to the ancestor. Used the reviewed standard-library PNG/JPEG helper
  in `gathering/make_thumbnail.py` for format conversion; no dependency installed.
