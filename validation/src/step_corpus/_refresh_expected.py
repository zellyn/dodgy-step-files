"""Refresh `**Expected validation**:` lines from live validate2 output.

For every catalog entry that has a corresponding /tmp/cad-v2-out/<section>/<id>.json
file, replace the `**Expected validation**: ...` line in
STEP_PROBLEM_CATALOG.md with the live-observed spec string.

Used after a corpus-wide ``_run_corpus`` pass to ground-truth Expected
lines from live oracle output.

Usage::

    cd validation
    uv run python -m step_corpus._refresh_expected            # dry-run summary
    uv run python -m step_corpus._refresh_expected --apply    # write changes
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from step_corpus._final_verdict import format_live_spec, V2_BASE
from step_corpus._build_catalog_json import CATALOG_MD, RESEARCH_ROOT, PREFIX_MAP

EXPECTED_RE = re.compile(
    r"(- \*\*Expected validation\*\*:\s*)`([^`]+)`",
)


def _section_dir(entry_id: str) -> str | None:
    for prefix, _section, section_dir in PREFIX_MAP:
        if entry_id.startswith(prefix):
            tail = entry_id[len(prefix):]
            if tail and tail.isdigit():
                return section_dir
    return None


def _load_summary(entry_id: str) -> dict | None:
    sec = _section_dir(entry_id)
    if not sec:
        return None
    path = V2_BASE / sec / f"{entry_id}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _refresh_for_entry(text: str, entry_id: str, new_spec: str) -> tuple[str, bool]:
    """Replace the entry's Expected validation line.

    Anchors on the entry's `### {id} —` header so we don't accidentally
    rewrite a different entry's line.
    """
    head = re.search(rf"^### {re.escape(entry_id)}\s+[—-]", text, re.MULTILINE)
    if not head:
        return text, False
    # Find next entry header (or EOF) to scope the replacement.
    after = text[head.end():]
    next_match = re.search(r"^### ", after, re.MULTILINE)
    end = head.end() + (next_match.start() if next_match else len(after))

    block = text[head.end():end]
    new_block, n = EXPECTED_RE.subn(rf"\1`{new_spec}`", block, count=1)
    if n == 0:
        return text, False
    if new_block == block:
        return text, False
    return text[:head.end()] + new_block + text[end:], True


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._refresh_expected")
    p.add_argument("--apply", action="store_true", help="write the changes (default: dry-run)")
    args = p.parse_args(argv)

    text = CATALOG_MD.read_text(encoding="utf-8")
    # Find every canonical entry id from the catalog
    entry_ids = re.findall(r"^### ([A-Za-z]+\d+)\s+[—-]", text, flags=re.MULTILINE)
    # Deduplicate while preserving order
    seen: set[str] = set()
    ids: list[str] = []
    for eid in entry_ids:
        if eid not in seen:
            seen.add(eid)
            ids.append(eid)

    no_v2 = []
    no_change = []
    changed: list[tuple[str, str, str]] = []  # (id, old, new)

    for eid in ids:
        v2 = _load_summary(eid)
        if v2 is None:
            no_v2.append(eid)
            continue
        s = v2.get("summary", {})
        new_spec = format_live_spec(s)

        # What's the current spec?
        head = re.search(rf"^### {re.escape(eid)}\s+[—-]", text, re.MULTILINE)
        if not head:
            continue
        after = text[head.end():]
        next_match = re.search(r"^### ", after, re.MULTILINE)
        end = head.end() + (next_match.start() if next_match else len(after))
        block = text[head.end():end]
        cur = EXPECTED_RE.search(block)
        old_spec = cur.group(2) if cur else None
        if old_spec is None:
            no_change.append(eid)
            continue
        if old_spec == new_spec:
            no_change.append(eid)
            continue
        text, ok = _refresh_for_entry(text, eid, new_spec)
        if ok:
            changed.append((eid, old_spec, new_spec))

    print(f"Catalog entries: {len(ids)}")
    print(f"  no v2 output:  {len(no_v2)}")
    print(f"  no spec line:  (subset of no-change)")
    print(f"  unchanged:     {len(no_change)}")
    print(f"  changed:       {len(changed)}")

    if changed:
        print("\nFirst 15 changes:")
        for eid, old, new in changed[:15]:
            print(f"  {eid}: {old!r}")
            print(f"   -> {new!r}")

    if args.apply and changed:
        CATALOG_MD.write_text(text, encoding="utf-8")
        print(f"\nWrote {len(changed)} updates to {CATALOG_MD}")
        # regenerate JSON
        from step_corpus._build_catalog_json import build_catalog, write_catalog, CATALOG_JSON
        rebuilt = build_catalog(CATALOG_MD)
        write_catalog(rebuilt, CATALOG_JSON)
        print(f"Regenerated {CATALOG_JSON} ({len(rebuilt)} entries)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
