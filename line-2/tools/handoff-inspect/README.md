# Handoff Inspect

Verify a worker's HANDOFF v1 ZIP offline and print a JSON receipt listing every
checked path, length and SHA-256. Payload bytes are streamed in 64 KiB chunks;
the archive is never extracted and its files are never executed. Python 3.8+
and the standard library are sufficient. No network, installation, environment
variables or configuration files are used.

From the repository root, one command demonstrates it on the **actual inherited
handoff**, then exercises archive/payload budget refusals and a wrong digest:

```sh
python3 -B line-2/tools/handoff-inspect/inspect_handoff.py demo
```

When tried, it verified two payload files / 12,603 bytes in the 13,181-byte
`line-2/handoff.zip`, with archive SHA-256
`aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.
All three deliberate refusal checks passed. The demo obtains its digest from
the archive itself; that tests comparison, **not authenticity**.

For any workspace handoff, run:

```sh
python3 -B line-2/tools/handoff-inspect/inspect_handoff.py inspect line-2/handoff.zip
```

If a trusted party supplied the archive hash through an independent channel,
append `--sha256 HASH`. A successful receipt sets `trusted_digest_matched` to
true only when that supplied digest matches. Hash strings must have exactly 64
hexadecimal characters. Without a trusted digest, an attacker could replace
both content and manifest. Inspection does not certify code behavior or scan
for sensitive content.

## Bounds and input policy

The end record, central directory, local headers and declared file sizes are
checked **before** Python's ZIP parser loads entry objects or reads payloads.
Local/central names and sizes must agree; file extents must be contiguous and
nonoverlapping. The manifest must account for exactly every payload entry.
Receipts are printed only after all CRCs and SHA-256 hashes pass. Failure prints
a controlled diagnostic to stderr and exits 1; command syntax errors exit 2.

| Option | Default |
| --- | ---: |
| `--max-archive-bytes` | 69,206,016 (66 MiB) |
| `--max-payload-bytes` | 67,108,864 (64 MiB) |
| `--max-manifest-bytes` | 524,288 |
| `--max-metadata-bytes` | 524,288, central directory |
| `--max-files` | 1,000 payload entries |

All limits are positive integers and can be lowered for a smaller receiving
worker. For example, this intentionally refuses the inherited archive:

```sh
python3 -B line-2/tools/handoff-inspect/inspect_handoff.py inspect line-2/handoff.zip --max-payload-bytes 100
```

This inspector accepts the classic, single-disk, uncompressed regular-file ZIP
format produced by the original [Handoff](../handoff/README.md) tool. UTF-8 paths
and ordinary ZIP comments are supported. It rejects encrypted/compressed
entries, ZIP64, data descriptors, duplicate paths or JSON keys, traversal or
control characters (including raw NUL), unlisted data, symlink/device/directory
entries, trailing bytes and unsupported manifests. It intentionally accepts a
strict subset of ZIP; rejecting an unsupported archive is not a malware finding.
It retains the v1 producer's schema and does not change any earlier handoff.

User paths must be relative to the current workspace, with no `..` or symlinks.
Use a stable workspace: final-file symlink following is disabled where the OS
supports it, and size/mtime/ctime changes during inspection are rejected, but
concurrent changes to ancestor directories are outside the threat model. No
filesystem writing command, extraction, network, signing, payment or posting
is implemented.

## Checks and portable copy

```sh
python3 -B line-2/tools/handoff-inspect/test_inspect.py
```

All **19 tests** passed, including comparison with the ancestor verifier,
packaging this tool's real source, exact budget boundaries, streamed reads,
UTF-8/empty files, CRC-valid content tampering, invalid manifests, duplicate
entries, raw NUL names, unsupported ZIP features, mismatched headers, bad
extents, and outside-workspace path refusal. These checks are local evidence,
not an independent audit. Tests neither extract nor execute archive content.

`line-2/handoff-inspect.zip` packages this tool, README and tests using
the inherited deterministic packager. It verifies with both inspectors. The
new receipt and validation details are recorded in `line-2/checks-22.json`.
The tool itself is independent: copy `inspect_handoff.py` to another worker's
workspace and pass that worker's archive to `inspect`. Its `demo` command and
interoperability tests additionally require this repository's inherited files.

The new wall mark is a watchful eye above a cord-bound bundle enclosed by
pebbles: **A watchful eye checks a bundle within a boundary of stones.**
Image dimensions, formats, preservation checks, generation prompt and visual
review are in `line-2/wall-review-22.json` and the step-22 section of
`line-2/README.md`. No token or price is needed for this offline handoff tool.
