#!/usr/bin/env python3
"""Merge occt-coverage/*/problems.json (+excluded.json) into one report.

Each domain directory under occt-coverage/ (e.g. exchange/, tkshhealing/) is
produced independently by a separate audit pass and may land at different
times. This script is tolerant of a domain directory existing without a
problems.json yet (in-progress / not-started domains are skipped with a
note, not an error).

Input schema per domain, in occt-coverage/<domain>/problems.json (a JSON
array of objects):
    problem_id, domain, description, occt_evidence[], subvariants[],
    fixture_ids[], coverage_verdict (COVERED|PARTIAL|GAP), notes,
    detect_only (optional bool)

occt-coverage/<domain>/excluded.json (optional, a JSON array of objects):
    pattern, example_locations[], reason, source_domain

Output: occt-coverage/OCCT_PROBLEM_COVERAGE.md — deterministic (sorted),
no timestamps, no other non-deterministic content, so repeated runs over
unchanged inputs produce byte-identical output.

Usage:
    python3 occt-coverage/merge_coverage.py
    python3 occt-coverage/merge_coverage.py --check   # print headline only, exit 0

Stdlib only, no third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
COVERAGE_ROOT = REPO_ROOT / "occt-coverage"
OUTPUT_PATH = COVERAGE_ROOT / "OCCT_PROBLEM_COVERAGE.md"

VALID_VERDICTS = ("COVERED", "PARTIAL", "GAP")

# ---------------------------------------------------------------------------
# Domain-level structural carve-outs.
#
# A "carve-out domain" is a `domain` field value (exact string, e.g.
# "exchange/iges-reader") whose entire population is GAP for a *structural*
# reason unrelated to fixture quality -- e.g. the corpus is STEP-only and
# contains zero .igs/.iges files, so no IGES-reader code path can ever be
# exercised regardless of how many fixtures are written. Each such carve-out
# must be documented in its domain's own SUMMARY.md; this list is the
# machine-readable mirror of that documentation (problems.json itself has no
# field for it). Extend this set as sibling domains land their own
# documented structural carve-outs -- do not add an entry here without a
# corresponding SUMMARY.md explanation in that domain's directory.
#
# exchange/iges-reader: MAINTAINER SCOPING DECISION (2026-07-16) -- IGES is
# formally out of scope for this corpus. The corpus targets generic
# shape/surface repair knowledge plus STEP as the standard exchange-format
# carrier; IGES is reader-format-specific and will not gain its own fixture
# section. This resolves the carve-out permanently (not a placeholder
# pending an IGES fixture section -- see BACKLOG.md for the closed item).
CARVEOUT_DOMAINS = {
    "exchange/iges-reader",  # out of scope per maintainer decision (2026-07-16); corpus-wide: zero .igs/.iges fixtures exist (verified)
}


def discover_domain_dirs():
    """Return sorted list of subdirectories of occt-coverage/ that look like domains."""
    if not COVERAGE_ROOT.is_dir():
        return []
    return sorted(p for p in COVERAGE_ROOT.iterdir() if p.is_dir())


def load_domain(domain_dir: Path):
    """Load one domain's problems.json + excluded.json.

    Returns (problems, excluded, status_note) where status_note is None on
    success or a short string explaining why the domain was skipped/partial.
    """
    problems_path = domain_dir / "problems.json"
    excluded_path = domain_dir / "excluded.json"

    if not problems_path.exists():
        return [], [], f"no problems.json yet (domain in progress)"

    try:
        problems = json.loads(problems_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [], [], f"problems.json unreadable: {exc}"

    if not isinstance(problems, list):
        return [], [], "problems.json is not a JSON array; skipped"

    excluded = []
    if excluded_path.exists():
        try:
            excluded = json.loads(excluded_path.read_text())
            if not isinstance(excluded, list):
                excluded = []
        except (OSError, json.JSONDecodeError):
            excluded = []

    return problems, excluded, None


def is_unreachable(entry):
    """True iff this class is a JUSTIFIED per-class structural carve-out.

    A class is "structurally unreachable" when no conforming STEP Part-21
    file can reach the OCCT code path at all -- not merely when writing a
    fixture would be hard or nobody has gotten to it. Example: OCCT clamps
    a negative CONICAL_SURFACE semi-angle to Precision::Angular() during
    STEP->Geom conversion, so the negative-semi-angle repair branch cannot
    be driven from a STEP file no matter what bytes you write.

    DELIBERATELY STRICT: the boolean alone does NOTHING. It is honored only
    when accompanied by a non-empty ``unreachable_rationale`` naming the
    OCCT file:line (or equivalent hard evidence) that blocks the path. A
    bare ``structurally_unreachable: true`` is IGNORED and the class stays a
    GAP -- see check_unreachable_claims(), which reports the discrepancy
    loudly. This keeps the flag from degrading into a way to make an
    inconvenient GAP disappear from the denominator.
    """
    return bool(entry.get("structurally_unreachable")) and bool(
        (entry.get("unreachable_rationale") or "").strip()
    )


def check_unreachable_claims(entries):
    """Return warning strings for unreachable flags that lack a rationale.

    Surfaced in the report (and on stderr) rather than silently tolerated,
    so an unjustified claim is *more* visible than an ordinary GAP.
    """
    bad = []
    for e in entries:
        if e.get("structurally_unreachable") and not (
            e.get("unreachable_rationale") or ""
        ).strip():
            bad.append(
                f"{e.get('domain', '?')}/{e.get('problem_id', '?')}: "
                "structurally_unreachable set without unreachable_rationale "
                "-- flag IGNORED, class still counted as a GAP"
            )
    return bad


def is_exercisable(entry):
    """STEP-exercisable view.

    Excludes detect_only classes, carve-out domains, and justified per-class
    structurally-unreachable classes.
    """
    if entry.get("detect_only"):
        return False
    if entry.get("domain") in CARVEOUT_DOMAINS:
        return False
    if is_unreachable(entry):
        return False
    return True


def pct(n, total):
    if total == 0:
        return "n/a"
    return f"{100.0 * n / total:.1f}%"


def verdict_counts(entries):
    c = {v: 0 for v in VALID_VERDICTS}
    for e in entries:
        v = e.get("coverage_verdict")
        if v in c:
            c[v] += 1
        else:
            c.setdefault("UNKNOWN", 0)
            c["UNKNOWN"] += 1
    return c


def render_headline_table(label, entries):
    total = len(entries)
    c = verdict_counts(entries)
    lines = [
        f"| view | classes | COVERED | PARTIAL | GAP |",
        f"|---|---:|---:|---:|---:|",
        f"| **{label}** | **{total}** | {c['COVERED']} ({pct(c['COVERED'], total)}) "
        f"| {c['PARTIAL']} ({pct(c['PARTIAL'], total)}) | {c['GAP']} ({pct(c['GAP'], total)}) |",
    ]
    return "\n".join(lines)


def render_per_subdomain_table(entries):
    """Break down by the full `domain` field (e.g. exchange/sewing), sorted."""
    by_sub = defaultdict(list)
    for e in entries:
        by_sub[e.get("domain", "?")].append(e)

    lines = [
        "| sub-domain | classes | COVERED | PARTIAL | GAP | detect-only | unreachable | carve-out |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for sub in sorted(by_sub):
        es = by_sub[sub]
        c = verdict_counts(es)
        n_detect = sum(1 for e in es if e.get("detect_only"))
        n_unreach = sum(1 for e in es if is_unreachable(e))
        is_carveout = sub in CARVEOUT_DOMAINS
        lines.append(
            f"| `{sub}` | {len(es)} | {c['COVERED']} | {c['PARTIAL']} | {c['GAP']} "
            f"| {n_detect} | {n_unreach or ''} | {'yes' if is_carveout else ''} |"
        )
    return "\n".join(lines)


def gap_rank_key(entry):
    """Deterministic tiering for the ranked GAP list.

    Tier 0: STEP-exercisable gaps (not detect_only, not a carve-out domain) --
            the most actionable: a missing fixture in the default/live path.
    Tier 1: detect_only gaps -- a BRepCheck status a kernel author must know
            but which is validity-*detection*, not a repair behavior.
    Tier 2: carve-out-domain gaps -- structural (e.g. IGES: no .igs fixtures
            exist in the corpus at all), not an individual fixture gap.
    Tier 3: structurally-unreachable gaps -- NO conforming STEP file can
            reach the code path (justified per-class; see is_unreachable).
            Ranked last because no fixture can ever close them, but still
            LISTED so the claim stays auditable rather than disappearing.
    Within a tier, sorted alphabetically by domain then problem_id for
    reproducibility (no manual-judgment "importance" ranking is encoded here
    -- see each domain's SUMMARY.md for the curated narrative ranking).
    """
    if is_unreachable(entry):
        tier = 3
    elif entry.get("domain") in CARVEOUT_DOMAINS:
        tier = 2
    elif entry.get("detect_only"):
        tier = 1
    else:
        tier = 0
    return (tier, entry.get("domain", ""), entry.get("problem_id", ""))


def render_gap_list(entries):
    gaps = [e for e in entries if e.get("coverage_verdict") == "GAP"]
    gaps.sort(key=gap_rank_key)

    if not gaps:
        return "_No GAP-verdict classes._"

    lines = [
        "| rank | tier | problem_id | domain | description |",
        "|---:|---|---|---|---|",
    ]
    tier_names = {
        0: "STEP-exercisable",
        1: "detect-only",
        2: "domain carve-out",
        3: "structurally unreachable",
    }
    for i, e in enumerate(gaps, 1):
        tier = gap_rank_key(e)[0]
        desc = (e.get("description") or "").replace("\n", " ").replace("|", "\\|")
        if len(desc) > 160:
            desc = desc[:157] + "..."
        lines.append(
            f"| {i} | {tier_names[tier]} | `{e['problem_id']}` | `{e.get('domain','?')}` | {desc} |"
        )
    return "\n".join(lines)


def excluded_source_key(entry):
    """excluded.json schema varies slightly between sibling domains (e.g.
    exchange/ uses `source_domain`, tkshhealing/ uses `source_group`) --
    accept either, falling back to a placeholder rather than erroring."""
    for key in ("source_domain", "source_group", "group", "category"):
        if key in entry and entry[key]:
            return str(entry[key])
    return "(ungrouped)"


def render_excluded_appendix(domain_name, excluded):
    if not excluded:
        return f"_No excluded.json (or it is empty) for `{domain_name}`._"

    by_source = defaultdict(int)
    for e in excluded:
        by_source[excluded_source_key(e)] += 1

    lines = [f"Total excluded branch/pattern entries: **{len(excluded)}**", ""]
    lines.append("| source | excluded patterns |")
    lines.append("|---|---:|")
    for src in sorted(by_source):
        lines.append(f"| `{src}` | {by_source[src]} |")
    return "\n".join(lines)


def build_report():
    domain_dirs = discover_domain_dirs()

    all_entries = []
    domain_data = {}  # domain_name -> (problems, excluded, status_note)
    domain_status_notes = {}

    for d in domain_dirs:
        problems, excluded, note = load_domain(d)
        domain_data[d.name] = (problems, excluded)
        if note:
            domain_status_notes[d.name] = note
        all_entries.extend(problems)

    # Sort the merged entry list deterministically for any listing that
    # iterates all_entries directly.
    all_entries_sorted = sorted(
        all_entries, key=lambda e: (e.get("domain", ""), e.get("problem_id", ""))
    )

    exercisable_entries = [e for e in all_entries_sorted if is_exercisable(e)]

    out = []
    out.append("# OCCT problem-class coverage — merged report")
    out.append("")
    out.append(
        "Auto-generated by `occt-coverage/merge_coverage.py` from every "
        "`occt-coverage/<domain>/problems.json` found at merge time. "
        "Deterministic: re-running over unchanged inputs reproduces this file "
        "byte-for-byte (no timestamps, sorted throughout). Do not hand-edit; "
        "edit the source `problems.json` / `excluded.json` files and re-run."
    )
    out.append("")

    domains_with_data = sorted(n for n in domain_data if domain_data[n][0])
    domains_without_data = sorted(n for n in domain_status_notes)
    out.append(
        f"Domains merged: **{', '.join(domains_with_data) if domains_with_data else '(none)'}**."
    )
    if domains_without_data:
        skipped_desc = "; ".join(
            f"`{n}` ({domain_status_notes[n]})" for n in domains_without_data
        )
        out.append(f"Domains present but not yet merged: {skipped_desc}.")
    out.append("")

    out.append("## Headline")
    out.append("")
    out.append(
        "Two views are shown. **All** counts every problem class found. "
        "**STEP-exercisable** additionally excludes `detect_only` classes "
        "(validity-*detection* status codes, not repair behaviors) and any "
        "classes belonging to a documented domain-level structural carve-out "
        "(currently: the IGES-reader sub-domain. IGES is formally out of "
        "scope for this corpus per a maintainer scoping decision "
        "(2026-07-16): the corpus targets generic shape/surface repair "
        "knowledge plus STEP as the standard exchange-format carrier, and "
        "IGES is reader-format-specific -- not a placeholder pending an "
        "IGES fixture section. This corpus is STEP-only and contains zero "
        "`.igs`/`.iges` fixtures)."
    )
    out.append("")
    out.append(
        "It also excludes individual classes flagged `structurally_unreachable` "
        "-- classes where NO conforming STEP Part-21 file can reach the OCCT "
        "code path at all, so no fixture could ever close them. This is a "
        "deliberately narrow escape hatch, not a way to retire hard work: the "
        "flag is honored ONLY with a non-empty `unreachable_rationale` citing "
        "the blocking OCCT `file:line`, an unjustified flag is IGNORED (the "
        "class stays a GAP and the discrepancy is reported below), and every "
        "such class is still LISTED in the ranked GAP table as tier 3 so the "
        "claim remains auditable. Each rationale names the condition that "
        "would make it reachable again if OCCT changes."
    )
    out.append("")
    unreachable = [e for e in all_entries_sorted if is_unreachable(e)]
    if unreachable:
        out.append(
            f"Structurally unreachable ({len(unreachable)}): "
            + ", ".join(
                f"`{e.get('problem_id')}` ({e.get('domain')})" for e in unreachable
            )
            + "."
        )
        out.append("")
    warnings = check_unreachable_claims(all_entries_sorted)
    if warnings:
        out.append("> **UNJUSTIFIED UNREACHABLE CLAIMS -- flags ignored:**")
        for w in warnings:
            out.append(f"> - {w}")
        out.append("")
    out.append(render_headline_table("All classes", all_entries_sorted))
    out.append("")
    out.append(render_headline_table("STEP-exercisable classes", exercisable_entries))
    out.append("")

    out.append("## Per sub-domain breakdown (all classes)")
    out.append("")
    if all_entries_sorted:
        out.append(render_per_subdomain_table(all_entries_sorted))
    else:
        out.append("_No problem classes loaded from any domain._")
    out.append("")

    out.append("## Ranked GAP list (all domains)")
    out.append("")
    out.append(
        "Ranking is a deterministic tiering, not a manual importance "
        "judgment: Tier 1 (STEP-exercisable) gaps are the most actionable "
        "-- a missing fixture on a default/live code path. Tier 2 "
        "(detect-only) gaps are BRepCheck status codes worth knowing but not "
        "repair behaviors. Tier 3 (domain carve-out) gaps are structural "
        "(e.g. the corpus has no IGES fixtures at all), not per-fixture gaps. "
        "Within a tier, sorted alphabetically by domain then problem_id. See "
        "each domain's own SUMMARY.md for a curated narrative ranking within "
        "its own scope."
    )
    out.append("")
    out.append(render_gap_list(all_entries_sorted))
    out.append("")

    out.append("## Excluded-branches appendix")
    out.append("")
    out.append(
        "Per domain, counts of branch/enum patterns judged out-of-scope for "
        "the denominator (plumbing, dead code, API-contract guards, etc.) -- "
        "see each domain's `excluded.json` for the full reasoning."
    )
    out.append("")
    for name in sorted(domain_data):
        _, excluded = domain_data[name]
        if not excluded and name in domain_status_notes and not domain_data[name][0]:
            continue  # domain had no problems.json at all; nothing to say
        out.append(f"### `{name}`")
        out.append("")
        out.append(render_excluded_appendix(name, excluded))
        out.append("")

    return "\n".join(out).rstrip() + "\n", all_entries_sorted, exercisable_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Print the headline to stdout and exit without writing the report file.",
    )
    args = parser.parse_args()

    report_text, all_entries, exercisable_entries = build_report()

    total = len(all_entries)
    c_all = verdict_counts(all_entries)
    c_ex = verdict_counts(exercisable_entries)
    ex_total = len(exercisable_entries)

    print(f"Merged {total} problem classes.")
    print(
        f"All:              COVERED {c_all['COVERED']} ({pct(c_all['COVERED'], total)}) | "
        f"PARTIAL {c_all['PARTIAL']} ({pct(c_all['PARTIAL'], total)}) | "
        f"GAP {c_all['GAP']} ({pct(c_all['GAP'], total)})"
    )
    print(
        f"STEP-exercisable ({ex_total}): COVERED {c_ex['COVERED']} ({pct(c_ex['COVERED'], ex_total)}) | "
        f"PARTIAL {c_ex['PARTIAL']} ({pct(c_ex['PARTIAL'], ex_total)}) | "
        f"GAP {c_ex['GAP']} ({pct(c_ex['GAP'], ex_total)})"
    )

    if args.check:
        return 0

    OUTPUT_PATH.write_text(report_text)
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
