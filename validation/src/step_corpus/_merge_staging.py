"""Merge staged gap-fill output (/tmp/cad-gapfill-*/) into the main corpus.

Each gap-fill agent stages its output to ``/tmp/cad-gapfill-<LETTER>/``:

    /tmp/cad-gapfill-X/
      entries.md            # markdown entries to append
      fixtures/
        12-Na-something/
          NewId001.stp
          ...

This script does the deterministic merge:

1. Validates every staged fixture has the expected header (Top-of-file
   ``/* <ID> - ... */`` comment matching its filename).
2. Verifies no ID collision with existing catalog entries.
3. Copies fixtures into ``../step-examples/<section_dir>/``.
4. Inserts the staged ``entries.md`` content into
   ``STEP_PROBLEM_CATALOG.md`` at the end of the appropriate section
   (or as a new section if the staged output declares one).
5. Re-runs the JSON catalog generator.
6. Reports what was merged and what (if anything) was skipped.

The merger does NOT run validate2; the caller should do that explicitly
after a successful merge.

Usage::

    uv run python -m step_corpus._merge_staging /tmp/cad-gapfill-E
    uv run python -m step_corpus._merge_staging --dry-run /tmp/cad-gapfill-C

Multiple staging dirs at once::

    uv run python -m step_corpus._merge_staging /tmp/cad-gapfill-A /tmp/cad-gapfill-C /tmp/cad-gapfill-E
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path

from step_corpus import catalog
from step_corpus._build_catalog_json import (
    CATALOG_MD,
    RESEARCH_ROOT,
    build_catalog,
    write_catalog,
)

STEP_EXAMPLES = RESEARCH_ROOT / "step-examples"

# Match an entry header line in staged entries.md.
# Catalog convention: "### <ID> — <Title>" or "### <ID> - <Title>" (em-dash or hyphen).
_ENTRY_HEAD_RE = re.compile(r"^###\s+([A-Za-z][A-Za-z0-9]*\d+)\s+[—-]\s+(.+?)\s*$")
_FIXTURE_HEADER_RE = re.compile(r"^/\*\s*([A-Za-z][A-Za-z0-9]*\d+)\s+[-—]")


class MergeError(RuntimeError):
    pass


def _existing_ids() -> set[str]:
    return {e["id"] for e in catalog.load_catalog()}


def _validate_fixture(fix: Path) -> None:
    """Read first 8 lines and confirm a /* ID - ... */ header is present
    and matches the filename's stem.

    Allows for the BOM byte sequence at the very start (the Pass E
    Xp009 fixture demonstrates this pattern legitimately)."""
    expect_id = fix.stem
    with fix.open("rb") as fh:
        head = fh.read(2048)
    # Strip BOMs for the comment scan but keep the file as-is on disk.
    if head.startswith(b"\xef\xbb\xbf"):
        head = head[3:]
    text = head.decode("utf-8", errors="replace")
    for line in text.splitlines()[:10]:
        m = _FIXTURE_HEADER_RE.match(line.strip())
        if m:
            if m.group(1) == expect_id:
                return
            raise MergeError(
                f"{fix}: header id {m.group(1)!r} != filename {expect_id!r}"
            )
    raise MergeError(f"{fix}: no '/* {expect_id} - ... */' header in first 10 lines")


def _staged_entries(staging: Path) -> list[tuple[str, str, str]]:
    """Return list of (entry_id, title, raw_block) parsed from entries.md.

    A "raw_block" is the markdown text from the entry's ``###`` heading up
    to (but not including) the next ``###`` heading or end-of-file.
    """
    entries_path = staging / "entries.md"
    if not entries_path.is_file():
        raise MergeError(f"{entries_path} missing; agent may not have run to completion")
    text = entries_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[tuple[str, str, str]] = []
    cur_id: str | None = None
    cur_title: str | None = None
    cur_buf: list[str] = []
    for line in lines:
        m = _ENTRY_HEAD_RE.match(line)
        if m:
            if cur_id is not None:
                out.append((cur_id, cur_title or "", "".join(cur_buf)))
            cur_id, cur_title = m.group(1), m.group(2)
            cur_buf = [line]
        else:
            if cur_id is not None:
                cur_buf.append(line)
    if cur_id is not None:
        out.append((cur_id, cur_title or "", "".join(cur_buf)))
    return out


def _staged_fixtures(staging: Path) -> dict[str, Path]:
    """Map ``entry_id -> fixture path`` for everything under fixtures/."""
    root = staging / "fixtures"
    if not root.is_dir():
        return {}
    out: dict[str, Path] = {}
    for fix in root.rglob("*.stp"):
        if fix.is_file():
            out[fix.stem] = fix
    return out


def _section_dir_for(entry_block: str) -> str | None:
    """Pull the section_dir out of an entry's `**Fixture path**:` line.

    Returns None if no path line is present (in which case the merger
    falls back to inferring from the staged fixture's parent dir name)."""
    m = re.search(r"\*\*Fixture path\*\*:\s*step-examples/([^/\s]+)/", entry_block)
    if m:
        return m.group(1)
    return None


def merge_one(staging: Path, *, dry_run: bool = False) -> dict[str, list[str]]:
    """Merge a single staging directory.

    Returns a report dict with keys: merged, skipped_id_collision,
    skipped_no_fixture, skipped_validation_error, fixtures_copied.
    """
    if not staging.is_dir():
        raise MergeError(f"{staging} is not a directory")

    existing = _existing_ids()
    entries = _staged_entries(staging)
    fixtures = _staged_fixtures(staging)

    merged: list[str] = []
    skipped_id_collision: list[str] = []
    skipped_no_fixture: list[str] = []
    skipped_validation_error: list[str] = []
    fixtures_copied: list[str] = []

    md_text = CATALOG_MD.read_text(encoding="utf-8")
    # We'll append accepted blocks to a buffer keyed by section_dir; at
    # write time we'll insert each per-section blob just before the next
    # section's level-2 heading.
    per_section_blocks: dict[str, list[str]] = {}

    for entry_id, _title, block in entries:
        if entry_id in existing:
            skipped_id_collision.append(entry_id)
            continue
        fix = fixtures.get(entry_id)
        if fix is None:
            skipped_no_fixture.append(entry_id)
            continue
        try:
            _validate_fixture(fix)
        except MergeError as exc:
            skipped_validation_error.append(f"{entry_id}: {exc}")
            continue

        section_dir = _section_dir_for(block) or fix.parent.name
        per_section_blocks.setdefault(section_dir, []).append(block)
        merged.append(entry_id)

        if not dry_run:
            target = STEP_EXAMPLES / section_dir / fix.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fix, target)
            fixtures_copied.append(str(target.relative_to(RESEARCH_ROOT)))

    if not dry_run and per_section_blocks:
        # Insert each block group before the heading of the next section
        # in the markdown. If the section heading is missing entirely
        # (a brand-new section), append it at end of file.
        for section_dir, blocks in per_section_blocks.items():
            new_md = _insert_blocks(md_text, section_dir, blocks)
            md_text = new_md
        CATALOG_MD.write_text(md_text, encoding="utf-8")

        # Regenerate JSON.
        rebuilt = build_catalog(CATALOG_MD)
        write_catalog(rebuilt, RESEARCH_ROOT / "STEP_PROBLEM_CATALOG.json")

    return {
        "merged": merged,
        "skipped_id_collision": skipped_id_collision,
        "skipped_no_fixture": skipped_no_fixture,
        "skipped_validation_error": skipped_validation_error,
        "fixtures_copied": fixtures_copied,
    }


def _insert_blocks(md_text: str, section_dir: str, blocks: list[str]) -> str:
    """Insert ``blocks`` into ``md_text`` at the end of the section
    matching ``section_dir``. If no such section exists, append a new
    section heading at end-of-file.
    """
    # Section dirs look like "12-3a-shells" → "## §12.3a"; "12-12-cross-product" → "## §12.12".
    parts = section_dir.split("-", 2)
    section_token = parts[1] if len(parts) >= 2 else section_dir
    # "1a" → "1a", "12" → "12".
    heading_marker = f"§12.{section_token}"

    # Find the section's level-2 header line (e.g. "## §12.3a Pcurves").
    section_re = re.compile(r"^##\s+" + re.escape(heading_marker) + r"\b", re.MULTILINE)
    sec_match = section_re.search(md_text)
    payload = "\n" + "\n".join(blocks).rstrip() + "\n"
    if sec_match is None:
        # New section: append at EOF with a fresh heading.
        appended = (
            f"\n## {heading_marker} {section_dir.split('-', 2)[-1].replace('-', ' ').title()}\n"
            f"{payload}"
        )
        return md_text.rstrip() + "\n" + appended
    # Find the start of the next ## heading after the section, or EOF.
    next_match = re.search(r"^##\s+§", md_text[sec_match.end():], re.MULTILINE)
    if next_match is None:
        return md_text.rstrip() + "\n" + payload
    insert_at = sec_match.end() + next_match.start()
    return md_text[:insert_at] + payload + md_text[insert_at:]


def merge_many(stagings: Iterable[Path], *, dry_run: bool = False) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    for s in stagings:
        out[str(s)] = merge_one(s, dry_run=dry_run)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._merge_staging")
    p.add_argument("staging", type=Path, nargs="+", help="staging dir, e.g. /tmp/cad-gapfill-E")
    p.add_argument("--dry-run", action="store_true", help="don't copy files; only report")
    args = p.parse_args(argv)

    try:
        result = merge_many(args.staging, dry_run=args.dry_run)
    except MergeError as exc:
        print(f"merge error: {exc}", file=sys.stderr)
        return 2

    for src, rep in result.items():
        print(f"\n=== {src} ===")
        print(f"  merged: {len(rep['merged'])}")
        for k in (
            "skipped_id_collision",
            "skipped_no_fixture",
            "skipped_validation_error",
        ):
            if rep[k]:
                print(f"  {k}: {len(rep[k])}")
                for item in rep[k][:5]:
                    print(f"    - {item}")
                if len(rep[k]) > 5:
                    print(f"    ... and {len(rep[k]) - 5} more")
        if rep["fixtures_copied"]:
            print(f"  fixtures_copied: {len(rep['fixtures_copied'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
