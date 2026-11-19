#!/usr/bin/env python3
"""Place the finished front page into the harness output directory.

render.py draws entry.png and keeps it in this repository. All this
program does is copy those bytes to $MAKEFUN_OUTPUT_DIR (or /output
when the variable is unset), after checking the PNG header and the
1 MiB size cap, then confirming the copy byte for byte. It uses only
the standard library and touches no network.
"""

import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PICTURE = ROOT / "entry.png"
LIMIT = 1024 * 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


def place_entry():
    blob = PICTURE.read_bytes()
    if blob[:8] != MAGIC:
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    if len(blob) > LIMIT:
        print("entry.png exceeds 1 MiB", file=sys.stderr)
        return 1
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / "entry.png"
    destination.write_bytes(blob)
    if destination.read_bytes() != blob:
        print("copy check failed", file=sys.stderr)
        return 1
    digest = hashlib.sha256(blob).hexdigest()
    print("entry.png placed at " + str(destination) + " (PNG OK)")
    print("size " + str(len(blob)) + " bytes, sha256 " + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(place_entry())
