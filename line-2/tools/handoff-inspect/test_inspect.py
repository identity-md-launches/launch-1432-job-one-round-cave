"""Offline behavioral and interoperability checks; no extraction or execution."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import struct
import sys
import unittest
from unittest.mock import patch
import warnings
import zipfile

sys.path.insert(0, str(Path(__file__).parent))
import inspect_handoff as inspector


def producer():
    path = Path(__file__).parent.parent / "handoff" / "handoff.py"
    spec = importlib.util.spec_from_file_location("previous_handoff", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_archive(files=None, manifest=None, compression=zipfile.ZIP_STORED,
                 extra=None, comment=b""):
    files = files if files is not None else {"report.txt": b"public evidence\n"}
    if manifest is None:
        manifest = {"version": 1, "algorithm": "sha256", "files": [
            {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in sorted(files.items())]}
    payload = (manifest if isinstance(manifest, bytes) else
               json.dumps(manifest, sort_keys=True).encode())
    target = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(target, "w", compression=compression) as archive:
            archive.comment = comment
            for name, data in [(inspector.MANIFEST, payload)] + list(files.items()) + (extra or []):
                entry = zipfile.ZipInfo(name)
                entry.create_system = 3
                entry.external_attr = (stat.S_IFREG | 0o644) << 16
                entry.compress_type = compression
                archive.writestr(entry, data)
    return target.getvalue()


class InspectTests(unittest.TestCase):
    def inspect(self, data, limits=None, expected=None):
        return inspector.inspect_stream(io.BytesIO(data), limits, expected)

    def reject(self, data, message=None, limits=None):
        with self.assertRaises((ValueError, zipfile.BadZipFile)) as caught:
            self.inspect(data, limits)
        if message:
            self.assertIn(message, str(caught.exception))

    def test_actual_inherited_bundle(self):
        data = Path("line-2/handoff.zip").read_bytes()
        receipt = self.inspect(data)
        old = producer().verify(data)
        self.assertEqual(receipt["archive_sha256"], old["sha256"])
        self.assertEqual(receipt["payload_bytes"], old["bytes"])
        self.assertEqual(receipt["file_count"], old["files"])
        self.assertFalse(receipt["trusted_digest_matched"])

    def test_current_real_tool_package(self):
        root = Path(__file__).parent
        files = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
        data = producer().build(files)
        receipt = self.inspect(data)
        self.assertEqual(receipt["files"], [
            {"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            for name, content in sorted(files.items())])

    def test_unicode_and_empty_file(self):
        receipt = self.inspect(make_archive({"notes/café.txt": b"", "notes/readme": b"x"}))
        self.assertEqual(receipt["payload_bytes"], 1)
        self.assertEqual(receipt["file_count"], 2)

    def test_digest_and_exact_budgets(self):
        data = make_archive()
        digest = hashlib.sha256(data).hexdigest()
        receipt = self.inspect(data, inspector.Limits(archive_bytes=len(data), payload_bytes=16,
                                                     files=1), digest.upper())
        self.assertTrue(receipt["trusted_digest_matched"])
        with self.assertRaisesRegex(ValueError, "trusted digest"):
            self.inspect(data, expected=hashlib.sha256(b"other archive").hexdigest())
        for bad in ("", "0x" + digest, digest[:-1], "z" * 64):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "64 hexadecimal"):
                self.inspect(data, expected=bad)

    def test_budget_refusals_before_zipfile_load(self):
        data = make_archive({"a": b"123", "b": b"456"})
        for limits in (inspector.Limits(archive_bytes=len(data)-1),
                       inspector.Limits(payload_bytes=5),
                       inspector.Limits(manifest_bytes=1),
                       inspector.Limits(metadata_bytes=1),
                       inspector.Limits(files=1)):
            with self.subTest(limits=limits), patch.object(inspector.zipfile, "ZipFile",
                                                         side_effect=AssertionError("too early")):
                self.reject(data, limits=limits)

    def test_streaming_reads_are_bounded(self):
        class Guarded(io.BytesIO):
            def read(self, size=-1):
                # ZipFile reads its already-seeked 22-byte end record with
                # read(-1). Bound the effective remaining span in that case.
                effective = len(self.getbuffer()) - self.tell() if size < 0 else size
                if effective > inspector.Limits.manifest_bytes:
                    raise AssertionError("unbounded archive read")
                return super().read(size)
        content = b"x" * (inspector.CHUNK * 5 + 17)
        receipt = inspector.inspect_stream(Guarded(make_archive({"data": content})))
        self.assertEqual(receipt["payload_bytes"], len(content))

    def test_crc_valid_content_tampering(self):
        data = make_archive()
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            manifest = archive.read(inspector.MANIFEST)
        # Rebuilding updates CRCs; only the SHA-256 check can catch this change.
        self.reject(make_archive({"report.txt": b"altered content\n"}, manifest), "integrity")

    def test_bad_crc(self):
        data = bytearray(make_archive())
        pos = data.index(b"public evidence\n")
        data[pos] ^= 1
        self.reject(bytes(data))

    def test_bad_manifest_structures(self):
        good = {"version": 1, "algorithm": "sha256", "files": [
            {"path": "report.txt", "bytes": 16,
             "sha256": hashlib.sha256(b"public evidence\n").hexdigest()}]}
        variants = [[], None, {**good, "version": True}, {**good, "version": 2},
                    {**good, "algorithm": "md5"}, {**good, "unexpected": 1},
                    {**good, "files": []}, {**good, "files": None}]
        for field, value in (("path", 42), ("path", "../secret"), ("bytes", True),
                             ("bytes", -1), ("bytes", 99), ("sha256", "x"),
                             ("sha256", good["files"][0]["sha256"].upper())):
            variants.append({**good, "files": [{**good["files"][0], field: value}]})
        variants.append({**good, "files": good["files"] * 2})
        for manifest in variants:
            with self.subTest(manifest=manifest):
                self.reject(make_archive(manifest=json.dumps(manifest).encode()))

    def test_duplicate_json_keys_and_nonstandard_json(self):
        for manifest in (b'{"version":1,"version":1,"algorithm":"sha256","files":[]}',
                         b'{"version":NaN,"algorithm":"sha256","files":[]}',
                         b"\xff", b"{" , b"[" * 2000):
            with self.subTest(manifest=manifest[:50]):
                with self.assertRaises((ValueError, UnicodeError, RecursionError)):
                    self.inspect(make_archive(manifest=manifest))

    def test_duplicate_and_unlisted_entries(self):
        self.reject(make_archive(extra=[("report.txt", b"another")]), "duplicate")
        self.reject(make_archive(extra=[("unlisted", b"extra")]), "unlisted")
        self.reject(make_archive(extra=[(inspector.MANIFEST, b"{}")]), "duplicate")

    def test_missing_manifest(self):
        data = make_archive().replace(b"HANDOFF.json", b"NOTHERE.json")
        self.reject(data, "manifest")

    def test_unsafe_names(self):
        for name in ("../escape", "/absolute", "a//b", "a/./b", "C:drive", "a\\b",
                     "newline\n", "trailing/", "nul\x00name"):
            with self.subTest(name=name):
                if "\x00" in name:
                    # ZipInfo truncates NUL names; mutate raw local/central names instead.
                    self.reject(make_archive({"abc": b"x"}).replace(b"abc", b"a\x00c"), "unsafe")
                else:
                    self.reject(make_archive({name: b"x"}))

    def test_unsupported_zip_features(self):
        self.reject(make_archive(compression=zipfile.ZIP_DEFLATED), "stored")
        for flags in (1, 8, 0x40):
            data = bytearray(make_archive())
            central = data.index(b"PK\x01\x02")
            struct.pack_into("<H", data, central + 8, flags)
            self.reject(bytes(data), "stored")
        data = bytearray(make_archive())
        central = data.index(b"PK\x01\x02")
        struct.pack_into("<I", data, central + 38, (stat.S_IFLNK | 0o777) << 16)
        self.reject(bytes(data), "regular")

    def test_inconsistent_local_metadata_and_overlap(self):
        data = bytearray(make_archive())
        data[14] ^= 1  # local CRC no longer matches central CRC
        self.reject(bytes(data), "headers disagree")
        data = bytearray(make_archive())
        central = data.index(b"PK\x01\x02")
        second = data.index(b"PK\x01\x02", central + 1)
        struct.pack_into("<I", data, second + 42, 0)
        self.reject(bytes(data))

    def test_truncated_prefix_trailer_and_multidisk(self):
        data = make_archive()
        for bad in (b"", data[:21], data[:-1], b"prefix" + data, data + b"trailer"):
            with self.subTest(length=len(bad)):
                self.reject(bad)
        modified = bytearray(data)
        struct.pack_into("<H", modified, len(modified)-22+4, 1)
        self.reject(bytes(modified), "multi-disk")

    def test_plain_comment(self):
        self.assertTrue(self.inspect(make_archive(comment=b"ordinary ZIP comment"))["verified"])

    def test_invalid_limits(self):
        for limits in (inspector.Limits(files=0), inspector.Limits(payload_bytes=-1),
                       inspector.Limits(archive_bytes=True)):
            self.reject(make_archive(), "positive", limits)

    def test_outside_paths_rejected_before_open(self):
        for path in ("/not/a/workspace/file", "../outside", "line-2/../../outside"):
            with self.subTest(path=path), patch.object(inspector.os, "open",
                                                     side_effect=AssertionError("path opened")):
                with self.assertRaisesRegex(ValueError, "relative workspace"):
                    inspector.inspect_path(path)


if __name__ == "__main__":
    unittest.main()
