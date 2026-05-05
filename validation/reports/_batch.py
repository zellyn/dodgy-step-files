"""Batch runner: process all .stp files in a directory, write JSON per-file."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _runner import gather


def main():
    if len(sys.argv) != 3:
        print("usage: _batch.py <stp_dir> <out_json>", file=sys.stderr)
        sys.exit(2)
    stp_dir = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    files = sorted(stp_dir.glob("*.stp"))
    out = {}
    for i, f in enumerate(files):
        print(f"[{i+1}/{len(files)}] {f.name}", file=sys.stderr, flush=True)
        out[f.name] = gather(f)
        # write incrementally so a crash mid-run preserves progress
        out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"done -> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
