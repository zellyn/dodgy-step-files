"""Command-line interface for browsing the STEP defect catalog.

Subcommands:

    list                       list all entries (one line each)
    list --section §12.3a      filter by section
    list --prefix Twi          filter by ID prefix
    show <ID>                  print full entry text + fixture path
    random [N]                 print N random entries (default 1)
    sections                   show section table with counts
    search <query>             bug-report BM25 search (alias for _bug_search)

Plumbed as a console script in pyproject.toml: ``step-corpus``.
"""
from __future__ import annotations

import argparse
import random as _random
import sys
import textwrap
from typing import Sequence

from step_corpus import catalog
from step_corpus._bug_search import BugIndex
from step_corpus._build_catalog_json import RESEARCH_ROOT


def _format_one_line(entry: dict) -> str:
    title = entry["title"]
    if len(title) > 90:
        title = title[:87] + "..."
    return f"{entry['id']:<8}  [§{entry['section']:<6}]  {title}"


def cmd_list(args: argparse.Namespace) -> int:
    entries = list(catalog.iter_canonical())
    if args.section:
        sec = args.section.lstrip("§")
        entries = [e for e in entries if e["section"] == sec]
    if args.prefix:
        entries = [e for e in entries if e["id"].startswith(args.prefix)]
    for e in entries:
        print(_format_one_line(e))
    print(f"\n{len(entries)} entries", file=sys.stderr)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    entry = catalog.find(args.entry_id)
    if entry is None:
        print(f"no entry {args.entry_id!r}", file=sys.stderr)
        return 1
    print(f"# {entry['id']} — {entry['title']}\n")
    print(f"**Section**: §{entry['section']} ({entry['section_dir']})")
    print(f"**Fixture**: {entry['fixture_path']}")
    if entry.get("sender"):
        print(f"**Sender**:  {entry['sender']}")
    if entry.get("sources"):
        print(f"**Sources**:")
        for s in entry["sources"]:
            print(f"  - {s}")
    print()
    print("**Description:**")
    print(textwrap.indent(textwrap.fill(entry["description"], width=78), "  "))
    print()
    print("**Reproducer recipe:**")
    print(textwrap.indent(textwrap.fill(entry["reproducer"], width=78), "  "))
    print()
    print("**Expected kernel behavior:**")
    print(textwrap.indent(textwrap.fill(entry["expected_kernel_behavior"], width=78), "  "))
    if entry.get("notes"):
        print("\n**Notes:**")
        print(textwrap.indent(textwrap.fill(entry["notes"], width=78), "  "))
    print(f"\n**Expected validation**: `{entry['expected_validation']}`")
    if entry.get("see_also"):
        print(f"**See also**: {', '.join(entry['see_also'])}")

    abs_path = RESEARCH_ROOT / entry["fixture_path"]
    print(f"\n--- Fixture {abs_path} ---")
    if abs_path.is_file():
        body = abs_path.read_text(encoding="latin-1", errors="replace")
        # Show the leading /* */ comment + first ~30 lines
        print(body.split("\n", 30)[:30][-1] if False else "\n".join(body.splitlines()[:30]))
        if len(body.splitlines()) > 30:
            print(f"  ... ({len(body.splitlines())} total lines, {abs_path.stat().st_size} bytes)")
    else:
        print(f"  (fixture file not found)")
    return 0


def cmd_random(args: argparse.Namespace) -> int:
    entries = list(catalog.iter_canonical())
    n = max(1, args.count)
    if args.seed is not None:
        _random.seed(args.seed)
    sample = _random.sample(entries, min(n, len(entries)))
    for e in sample:
        print(_format_one_line(e))
    return 0


def cmd_sections(_args: argparse.Namespace) -> int:
    entries = list(catalog.iter_canonical())
    from collections import Counter
    by_sec = Counter(e["section"] for e in entries)
    title_w = 18
    print(f"{'Section':<{title_w}}  Count")
    print(f"{'-' * title_w}  -----")
    for sec in sorted(by_sec):
        print(f"§{sec:<{title_w-1}}  {by_sec[sec]:>5}")
    print(f"{'Total':<{title_w}}  {len(entries):>5}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    idx = BugIndex.load()
    hits = idx.search(args.query, k=args.k)
    if not hits:
        print(f"no matches for: {args.query!r}", file=sys.stderr)
        return 1
    for rank, (score, entry) in enumerate(hits, start=1):
        print(f"{rank:>3}. [{score:6.2f}] {_format_one_line(entry)}")
    return 0


def cmd_stats(_args: argparse.Namespace) -> int:
    """Print one-screen corpus statistics for downstream users."""
    from collections import Counter
    entries = list(catalog.iter_canonical())
    by_section = Counter(e["section"] for e in entries)
    n_with_tier3 = sum(
        1 for e in entries
        if "**Tier-3 assertion**" in (e.get("notes") or "")
        or any("tier-3" in s.lower() for s in (e.get("sources") or []))
    )
    n_with_seealso = sum(1 for e in entries if e.get("see_also"))
    ev_specs = Counter()
    for e in entries:
        spec = e.get("expected_validation") or ""
        if "shape(" in spec:
            ev_specs["loads-with-shapes"] += 1
        elif "signal(" in spec:
            ev_specs["segfaults"] += 1
        elif "reject" in spec:
            ev_specs["parser-rejects"] += 1
        elif "process_signal" in spec or "accept(" in spec:
            ev_specs["other-non-silent"] += 1
        elif spec:
            ev_specs["silent-empty"] += 1

    print(f"STEP Defect Corpus — current state\n")
    print(f"Catalog entries:        {len(entries)}")
    print(f"Distinct §12.x sections: {len(by_section)}")
    print(f"Entries with see_also:  {n_with_seealso}")
    print()
    print("By section:")
    for sec in sorted(by_section):
        print(f"  §{sec:<8} {by_section[sec]:>4}")
    print()
    print("By Expected validation oracle baseline:")
    for k in ("silent-empty", "loads-with-shapes", "segfaults", "parser-rejects", "other-non-silent"):
        n = ev_specs.get(k, 0)
        pct = 100 * n / len(entries) if entries else 0
        print(f"  {k:<22} {n:>4}  ({pct:.1f} %)")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step-corpus", description=__doc__.strip().split("\n", 1)[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list catalog entries")
    p_list.add_argument("--section", help="filter by section, e.g. 12.3a")
    p_list.add_argument("--prefix", help="filter by ID prefix, e.g. Twi")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="show one entry + its fixture head")
    p_show.add_argument("entry_id", help="catalog ID, e.g. Le001")
    p_show.set_defaults(func=cmd_show)

    p_rand = sub.add_parser("random", help="pick N random entries")
    p_rand.add_argument("count", type=int, nargs="?", default=1)
    p_rand.add_argument("--seed", type=int, default=None)
    p_rand.set_defaults(func=cmd_random)

    p_sec = sub.add_parser("sections", help="show section table")
    p_sec.set_defaults(func=cmd_sections)

    p_search = sub.add_parser("search", help="bug-report BM25 search")
    p_search.add_argument("query", nargs="+", help="query string")
    p_search.add_argument("-k", type=int, default=10)
    p_search.set_defaults(func=cmd_search)

    p_stats = sub.add_parser("stats", help="one-screen corpus stats")
    p_stats.set_defaults(func=cmd_stats)

    args = p.parse_args(argv)
    if hasattr(args, "query") and isinstance(args.query, list):
        args.query = " ".join(args.query)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
