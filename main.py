"""Copy entry.png byte-for-byte into MAKEFUN_OUTPUT_DIR (stdlib only)."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    src = os.path.join(HERE, "entry.png")
    with open(src, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png: bad PNG magic bytes", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)
    with open(dst, "rb") as fh:
        back = fh.read()
    if back != data:
        print("entry.png: copy mismatch", file=sys.stderr)
        return 1
    print("wrote %s (%d bytes)" % (dst, len(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
