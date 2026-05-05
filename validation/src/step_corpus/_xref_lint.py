"""Cross-reference lint for the catalog markdown.

The catalog uses two cross-reference idioms:

- ``**See also**: Foo123, Bar456``: non-equivalence pointers between
  related entries (different defects that share context, surface, or
  reproducer pattern).
- ``**Originally also catalogued as**: Foo789``: equivalence pointer
  for entries that absorbed older IDs during dedup passes.

Either form is broken if the target ID isn't an entry that exists in
the catalog. A broken ref is a small but real quality bug; it makes
the catalog navigation lie. This lint catches them.

False-positive guard: ``\\X2\\``, ``\\X0\\`` and similar Part-21 escape
directives match the entry-ID regex; they are excluded by the
``_KNOWN_FALSE_POSITIVES`` set.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from step_corpus._build_catalog_json import CATALOG_MD


_HEADER_RE = re.compile(r"^### ([A-Za-z]+\d+)\s+[—-]", re.MULTILINE)
_SEE_ALSO_RE = re.compile(r"\*\*See also\*\*:\s*([^\.\n]+)")
_ORIG_AS_RE = re.compile(r"\*\*Originally also catalogued as\*\*:\s*([^\.\n]+)")
_ID_TOKEN_RE = re.compile(r"\b([A-Za-z]+\d+)\b")

# Tokens that look like entry-IDs but are something else (Part-21 escape
# directives, ISO standard identifiers, etc.). Add to this set when a
# false positive shows up.
_KNOWN_FALSE_POSITIVES: set[str] = {
    "X2", "X0",  # \X2\…\X0\ Part-21 UCS-2 escape directive
}


def find_broken_xrefs(text: str) -> list[dict[str, Any]]:
    """Return [{"referrer": id, "kind": str, "missing": id}, ...]."""
    headers = list(_HEADER_RE.finditer(text))
    known_ids = {m.group(1) for m in headers}

    out: list[dict[str, Any]] = []
    for i, m in enumerate(headers):
        eid = m.group(1)
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]
        for kind, regex in [("See also", _SEE_ALSO_RE),
                             ("Originally also catalogued as", _ORIG_AS_RE)]:
            for sm in regex.finditer(block):
                refs = _ID_TOKEN_RE.findall(sm.group(1))
                for r in refs:
                    if r in _KNOWN_FALSE_POSITIVES:
                        continue
                    if r not in known_ids:
                        out.append({"referrer": eid, "kind": kind, "missing": r})
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._xref_lint")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 if any broken xref is present")
    args = p.parse_args(argv)

    text = Path(CATALOG_MD).read_text(encoding="utf-8")
    rows = find_broken_xrefs(text)

    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if not rows:
        print("No broken cross-references.")
        return 0
    print(f"Broken cross-references: {len(rows)}")
    for r in rows:
        print(f"  {r['referrer']} → {r['missing']} (in `{r['kind']}`)")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
