"""Extract structured outcome tags from catalog entries' prose.

Each catalog entry's `**Expected kernel behavior**:` field is prose like:

    "heal — silently strip a single leading UTF-8 BOM ... reject UTF-16
    BOMs with a clear E_UNEXPECTED_BOM diagnostic"

Downstream tooling (kernel test harnesses) wants this as structured data:

    allowed:    [heal, reject]
    disallowed: [silent-accept, crash, infinite-loop]

This module derives that mapping by regex over the prose. It's a helper,
not a replacement for the prose; the prose remains the source of truth
for nuance. The tags are the *machine-checkable subset*.

Tags vocabulary
---------------

- ``heal``: kernel silently fixes / repairs / coerces.
- ``reject``: kernel raises / refuses / fails-to-read with a diagnostic.
- ``warn-and-proceed``: kernel notes the issue but loads anyway.
- ``silent-accept``: kernel loads without comment (usually a disallowed
  outcome, since the catalog rarely *wants* silent acceptance).
- ``crash``: kernel segfaults / aborts (always disallowed).
- ``infinite-loop``: kernel hangs / loops (always disallowed).

The extractor is conservative: when prose is ambiguous, fewer tags are
emitted. When prose explicitly forbids an outcome, it goes into
``disallowed``.

Usage
-----

    cd validation
    uv run python -m step_corpus._outcome_extractor              # CLI summary
    uv run python -m step_corpus._outcome_extractor --json       # full data
    uv run python -m step_corpus._outcome_extractor --id Le001   # one entry
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from typing import Any

from step_corpus import catalog


# Phrase → outcome mapping. Tested against expected_kernel_behavior text
# (lowercase). Order matters: first match wins for ambiguous phrases.
_TAG_PATTERNS: list[tuple[str, list[str]]] = [
    # Disallowed outcomes (when explicitly called out)
    ("crash",            [r"\bsegfault", r"\bsegfaults\b", r"\bcrash(es|ed|ing)?\b",
                          r"\babort\b", r"\bsignal\(11\)", r"\bsigsegv\b"]),
    ("infinite-loop",    [r"\binfinite loop", r"\bhang(s|ing)?\b",
                          r"\bnon-terminating\b", r"\bunbounded\b"]),
    ("silent-accept",    [r"\bsilently accept", r"\bsilent acceptance",
                          r"\bsilently load", r"\bsilently ignore",
                          r"\bsilently swallow", r"\bsilent acceptance"]),
    # Allowed outcomes
    ("reject",           [r"\breject", r"\brefuse",
                          r"\braise (a |an )?diagnostic\b",
                          r"\bemit (a |an )?error\b", r"\bdiagnose\b",
                          r"\bfail to read", r"\bfail-to-read",
                          r"\bthrow (a |an )?(diagnostic|error|exception)\b",
                          r"\bstop (with|on) (a |an )?diagnostic\b"]),
    ("heal",             [r"\bheal\b", r"\brepair\b", r"\bcoerce\b",
                          r"\brecover\b", r"\bnormali[sz]e\b",
                          r"\bcollapse\b", r"\bsplit\b", r"\bmerge\b",
                          r"\bsynth(esi[sz]e)?\b", r"\bbridge\b",
                          r"\bsmooth\b", r"\bfix\b", r"\bsanitize\b",
                          r"\bsew\b", r"\bstitch\b", r"\bclose (the )?gap\b",
                          r"\bunify\b"]),
    ("warn-and-proceed", [r"\bwarn (and |then |but )", r"\bwarning\b",
                          r"\bemit (a |an )?warning\b",
                          r"\b(a |an )?diagnostic .{0,10}(and |then |but )(?:still )?(load|continue|proceed)",
                          r"\baccept (with )?(a |an )?(diagnostic|warning|notice)",
                          r"\bload (with )?(a |an )?warning",
                          r"\breport (and|but) continue"]),
]


# Phrases that indicate a disallowed outcome ("must not", "should not",
# "cannot ... silently", etc.); these negate the surrounding tag.
_NEGATION_RE = re.compile(
    r"\b(must not|should not|never|don'?t|cannot|do not|may not)\b\s+"
    r"(silently|silent|crash|hang|infinite|loop|abort|segfault|accept)",
    re.IGNORECASE,
)


def extract_outcomes(prose: str) -> dict[str, list[str]]:
    """Return ``{"allowed": [...], "disallowed": [...]}`` for one entry's prose."""
    if not prose:
        return {"allowed": [], "disallowed": []}
    text = prose.lower()
    allowed: list[str] = []
    disallowed: list[str] = []

    # Always-disallowed outcomes mentioned positively in the prose are
    # typically descriptions of *what kernels currently do wrong*; we
    # treat those as "disallowed" (the catalog says these outcomes
    # are unacceptable).
    DISALLOWED_AT_FACE_VALUE = {"crash", "infinite-loop", "silent-accept"}

    for tag, patterns in _TAG_PATTERNS:
        for pat in patterns:
            if re.search(pat, text):
                if tag in DISALLOWED_AT_FACE_VALUE:
                    if tag not in disallowed:
                        disallowed.append(tag)
                else:
                    if tag not in allowed:
                        allowed.append(tag)
                break  # don't double-count tag

    # Negations: "must not silently accept" → silent-accept disallowed
    # We already capture silent-accept on its own above, but explicit
    # negations are stronger signal, so always include them.
    for m in _NEGATION_RE.finditer(text):
        action = m.group(2).lower()
        if action in {"silently", "silent", "accept"}:
            if "silent-accept" not in disallowed:
                disallowed.append("silent-accept")
        elif action in {"crash", "abort", "segfault"}:
            if "crash" not in disallowed:
                disallowed.append("crash")
        elif action in {"hang", "infinite", "loop"}:
            if "infinite-loop" not in disallowed:
                disallowed.append("infinite-loop")

    return {"allowed": allowed, "disallowed": disallowed}


def all_outcomes() -> list[dict[str, Any]]:
    out = []
    for entry in catalog.iter_canonical():
        prose = entry.get("expected_kernel_behavior") or ""
        outcomes = extract_outcomes(prose)
        out.append({
            "id": entry["id"],
            "section": entry["section"],
            "title": entry["title"],
            "expected": prose[:200],
            **outcomes,
        })
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._outcome_extractor")
    p.add_argument("--json", action="store_true")
    p.add_argument("--id", type=str)
    args = p.parse_args(argv)

    if args.id:
        e = catalog.find(args.id)
        if not e:
            print(f"unknown id: {args.id}", file=sys.stderr)
            return 1
        outcomes = extract_outcomes(e.get("expected_kernel_behavior") or "")
        print(f"{args.id} — {e['title']}")
        print(f"  prose: {e.get('expected_kernel_behavior')!r}")
        print(f"  allowed:    {outcomes['allowed']}")
        print(f"  disallowed: {outcomes['disallowed']}")
        return 0

    rows = all_outcomes()
    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    # Histograms
    allowed_count = Counter()
    disallowed_count = Counter()
    no_tag_count = 0
    for r in rows:
        if not r["allowed"] and not r["disallowed"]:
            no_tag_count += 1
        for t in r["allowed"]:
            allowed_count[t] += 1
        for t in r["disallowed"]:
            disallowed_count[t] += 1

    print(f"Outcome extraction across {len(rows)} entries:\n")
    print("Allowed outcomes (kernel SHOULD produce one of these):")
    for t, n in allowed_count.most_common():
        pct = 100 * n / len(rows)
        print(f"  {t:<22} {n:>5}  ({pct:.1f} %)")
    print("\nDisallowed outcomes (kernel SHOULD NOT produce these):")
    for t, n in disallowed_count.most_common():
        pct = 100 * n / len(rows)
        print(f"  {t:<22} {n:>5}  ({pct:.1f} %)")
    print(f"\nEntries with no extracted tag: {no_tag_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
