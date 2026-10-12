#!/usr/bin/env python3
"""Offline structural checks for gathering 02; never writes or uses the network."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
import zlib


class Gallery(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.sections = [], [], []
        self.external_code = []
        self.group = None
        self.future = False
        self.order = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.group = attrs["id"]
            self.sections.append(self.group)
        if tag == "details": self.future = True
        if tag == "article":
            self.order.setdefault((self.group, self.future), []).append(int(attrs["data-number"]))
        if tag == "a": self.links.append(attrs.get("href", ""))
        if tag == "img":
            assert attrs.get("alt"), "gallery image needs alt text"
            self.images.append(attrs["src"])
        if tag in ("script", "link"):
            self.external_code.append(tag)

    def handle_endtag(self, tag):
        if tag == "details": self.future = False
        if tag == "section": self.group = None


def png_dimensions(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height, depth, color, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", data[16:29])
    assert (depth, color, compression, filtering, interlace) == (8,2,0,0,0)
    pos = 8
    while pos < len(data):
        length = int.from_bytes(data[pos:pos+4], "big")
        chunk = data[pos+4:pos+8+length]
        crc = int.from_bytes(data[pos+8+length:pos+12+length], "big")
        assert zlib.crc32(chunk) == crc, "PNG checksum mismatch"
        pos += 12+length
        if chunk[:4] == b"IEND": break
    assert pos == len(data)
    return width, height


def jpeg_dimensions(data):
    assert data[:2] == b"\xff\xd8" and data[-2:] == b"\xff\xd9"
    pos = 2
    while pos < len(data):
        assert data[pos] == 255
        marker = data[pos+1]
        length = int.from_bytes(data[pos+2:pos+4], "big")
        assert length >= 2
        if marker == 0xc0:
            depth,height,width,components = struct.unpack(">BHHB", data[pos+4:pos+10])
            assert depth == 8 and components == 3
            return width,height
        assert marker != 0xda, "missing baseline JPEG frame"
        pos += length+2
    raise AssertionError("missing JPEG dimensions")


PLACEHOLDER = {"name": "Not painted yet", "image": "https://api.imd.fun/artifacts/9cbb7bb2a41efa92e010921f287819c9ffb02c4375fa9496c8468701d8e00cc5", "attributes": [{"trait_type": "Cave", "value": "Base"}]}
TRAITS = ["Cave", "Wall", "Number", "Left behind", "Meaning", "One thing"]


def check_painted(obj, wall, number):
    assert set(obj) == {"name", "image", "attributes"}
    assert obj["image"].startswith("https://api.imd.fun/artifacts/")
    attrs = obj["attributes"]
    assert [a["trait_type"] for a in attrs] == TRAITS
    assert all(set(a) == {"trait_type", "value"} for a in attrs)
    assert attrs[0]["value"] == "Base" and attrs[1]["value"] == wall
    assert type(attrs[2]["value"]) is int and attrs[2]["value"] == number


def main():
    root = Path(".")
    baseline = json.loads(Path("gathering/line-source-hashes.json").read_text())
    actual = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(root.glob("line-*/**/*")) if p.is_file()}
    assert actual == baseline, "a line folder was changed"
    goals = json.loads(Path("dist/goals.json").read_text())
    assert goals == [{"line": n, "goal": Path(f"line-{n}/GOAL.md").read_text().strip()}
                     for n in range(1,5)]
    png = Path("artifacts/gathering/wall-v2.png").read_bytes()
    assert Path("artifacts/gathering/wall.png").read_bytes() == png
    jpg = Path("dist/gathering/02.jpg").read_bytes()
    assert png_dimensions(png) == (1254,1254)
    assert jpeg_dimensions(jpg) == (512,512)
    record = json.loads(Path("dist/gathering/02.json").read_text())
    check_painted(record, "Gathering", 2)
    assert record["image"] == "https://api.imd.fun/artifacts/" + hashlib.sha256(png).hexdigest()
    attrs = record["attributes"]
    assert attrs[-1]["value"] == "Gathering"
    assert all(isinstance(a["value"], str) and a["value"] for a in attrs if a["trait_type"] != "Number")
    walls = ["line-1", "line-2", "line-3", "line-4", "gathering"]
    records, painted, placeholders = [], 0, 0
    for wall in walls:
        label = "Gathering" if wall == "gathering" else "Line " + wall[-1]
        for path in sorted(Path(f"dist/{wall}").glob("[0-9][0-9].json")):
            obj = json.loads(path.read_text())
            records.append(path.relative_to("dist").as_posix())
            if obj == PLACEHOLDER:
                placeholders += 1
                assert not path.with_suffix(".jpg").exists()
            else:
                painted += 1
                check_painted(obj, label, int(path.stem))
                assert path.with_suffix(".jpg").is_file()
        for number in range(1, 22):
            assert Path(f"dist/{wall}/{number:02d}.json").is_file()
    gallery = Gallery()
    gallery.feed(Path("dist/index.html").read_text())
    assert gallery.sections == walls
    assert set(records) <= set(gallery.links)
    assert len(gallery.images) == len(records)
    assert not gallery.external_code
    for numbers in gallery.order.values(): assert numbers == sorted(numbers, reverse=True)
    for src in gallery.images:
        assert src.startswith("https://api.imd.fun/artifacts/") or (Path("dist")/src).is_file()
    for directory in ("gathering", "shared", "dist"):
        for path in Path(directory).rglob("*"):
            assert not path.is_symlink()
            if path.is_file(): assert path.stat().st_size <= 100000, str(path)
            if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                assert directory == "dist" and path.suffix == ".jpg", str(path)
    assert Path("gathering/COINS.md").read_text().splitlines()[0] == "none"
    assert not Path("gathering/coin-order.json").exists()
    assert not Path("gathering/deploy-order.json").exists()
    print(json.dumps({"passed": True, "line_files_unchanged": len(actual), "goals": 4,
                      "records": len(records), "painted": painted, "placeholders": placeholders,
                      "png": "1254x1254 RGB", "jpeg": "512x512 baseline color",
                      "wall_sha256": hashlib.sha256(png).hexdigest(),
                      "visual_review": "See gathering/README.md; not certified by this checker."}, indent=2))


if __name__ == "__main__":
    main()
