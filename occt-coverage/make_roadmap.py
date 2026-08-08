#!/usr/bin/env python3
"""Generate IMPLEMENTERS_ROADMAP.md — the corpus re-cut for a kernel author.

The catalog is organised for *auditing* (3335 defect entries, one per file).
Someone writing a new CAD kernel needs the other axis: the ~200 distinct
REPAIR MECHANISMS they have to implement, in an order that front-loads the
failures that hurt users most, each pointing at the fixtures that prove it.

Everything here is joined from data that already exists and is CI-verified:
  - occt-coverage/*/problems.json  -> the mechanism classes + their fixtures
  - STEP_PROBLEM_CATALOG.md        -> each fixture's live `Expected validation`

Nothing is hand-asserted. Re-run after either source changes:
    python3 occt-coverage/make_roadmap.py
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "IMPLEMENTERS_ROADMAP.md")

# ---------------------------------------------------------------- load

VACUOUS = re.compile(
    r"^(heal\.?|heal:\s*investigate\s*/\s*reject:\s*geometric degeneracy\.?|"
    r"heal:\s*detect and correct the issue;\s*reject:\s*if precondition unrecoverable\.?)$",
    re.I,
)


def load_catalog_tokens() -> tuple[dict[str, str], dict[str, str], set[str]]:
    """fixture id -> (occt_heal_on token, entry title, set-of-specced-ids).

    "Specced" means the entry carries an `Expected kernel behavior` that
    actually says something. An entry can be a perfectly good *test* — real
    file, real CI-checked assertions — while telling an implementer nothing
    about what their kernel ought to do. This page must not send someone to
    one of those pretending it is a specification.
    """
    text = open(os.path.join(ROOT, "STEP_PROBLEM_CATALOG.md")).read()
    starts = [(m.start(), m.group(1), m.group(2))
              for m in re.finditer(r"^### (\S+) — (.*)$", text, re.M)]
    tok, title, specced = {}, {}, set()
    for i, (pos, fid, ttl) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        block = text[pos:end]
        m = re.search(r"\*\*Expected validation\*\*: `occt=([^/]+)/", block)
        if m:
            tok[fid] = m.group(1)
        title[fid] = ttl
        e = re.search(r"^- \*\*Expected kernel behavior\*\*:\s*(.*)$", block, re.M)
        if e and e.group(1).strip() and not VACUOUS.match(e.group(1).strip()):
            specced.add(fid)
    return tok, title, specced


def load_classes() -> list[dict]:
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "occt-coverage", "*", "problems.json"))):
        try:
            out.extend(json.load(open(path)))
        except (OSError, json.JSONDecodeError):
            continue
    return out


# ------------------------------------------------------- classification

# How a fixture behaves in the reference engine (OCCT 7.8.1), from its
# CI-verified Expected line. These are OBSERVATIONS, not judgements about
# what is correct -- see the caveat rendered into the document.
def bucket(token: str) -> str:
    if token.startswith("signal"):
        return "crash"
    if token == "empty":
        return "empty"
    if token == "reject":
        return "reject"
    if token.startswith("shape"):
        return "loads"
    return "other"


def tier_of(counts: collections.Counter) -> tuple[int, str]:
    """Priority tier. Deliberately simple and stated in the document.

    T0  the class has at least one fixture that CRASHES the reference engine.
        A kernel must never abort on input; this is the one unambiguous
        must-not-do, so it sorts first regardless of anything else.
    T1  a majority of the class's fixtures make the reference engine accept
        the file and return nothing. Silent total loss is the worst
        *correctness* outcome: the user believes the import succeeded.
    T2  everything else -- the file loads and the question is whether the
        geometry was repaired faithfully.
    """
    if counts.get("crash", 0):
        return 0, "T0 crash-exposing"
    total = sum(counts.values())
    if total and counts.get("empty", 0) / total > 0.5:
        return 1, "T1 silent-empty dominant"
    return 2, "T2 loads-and-heals"


# ------------------------------------------------------------- render

def main() -> None:
    tok, title, specced = load_catalog_tokens()
    classes = load_classes()

    rows = []
    for c in classes:
        fids = [f for f in (c.get("fixture_ids") or []) if f in tok]
        if not fids:
            continue
        counts = collections.Counter(bucket(tok[f]) for f in fids)
        rank, label = tier_of(counts)
        rows.append({
            "id": c.get("problem_id", "?"),
            "domain": c.get("domain", "?"),
            "desc": (c.get("description") or "").strip(),
            "fids": fids,
            "counts": counts,
            "rank": rank,
            "label": label,
            "verdict": c.get("coverage_verdict", "?"),
            "specced": sum(1 for f in fids if f in specced),
        })

    # Within a tier: most crash fixtures first, then most fixtures overall.
    rows.sort(key=lambda r: (r["rank"], -r["counts"].get("crash", 0), -len(r["fids"]), r["id"]))

    n_fix = len({f for r in rows for f in r["fids"]})
    tally = collections.Counter(r["label"] for r in rows)

    L: list[str] = []
    A = L.append
    A("# Implementer's roadmap")
    A("")
    A("**Audience: you are writing a CAD kernel and need to survive real-world "
      "STEP files.** This document is the corpus re-cut along the axis you "
      "actually work on.")
    A("")
    A("The catalog ([`STEP_PROBLEM_CATALOG.md`](STEP_PROBLEM_CATALOG.md)) is "
      "organised one entry per broken file, which is right for auditing and "
      "wrong for building — 3335 entries do not tell you where to start. This "
      "page inverts it into the "
      f"**{len(rows)} distinct repair mechanisms** those files exercise, "
      f"ordered so the failures that hurt users most come first, each pointing "
      f"at the fixtures that prove you got it right ({n_fix} fixtures cited).")
    A("")
    A("> **Generated file — do not edit.** `python3 occt-coverage/make_roadmap.py`.")
    A("> Everything below is joined from `occt-coverage/*/problems.json` and the "
      "catalog's CI-verified `Expected validation` lines. No hand-entered claims.")
    A("")

    A("## How to use this")
    A("")
    A("1. Work down the tiers. Inside a tier the order is by blast radius, not importance-by-opinion.")
    A("2. For each mechanism, read the cited fixtures' **`Expected kernel behavior`** field in the "
      "catalog. That field — not `Expected validation` — is the specification of what a *correct* "
      "kernel should do. `Expected validation` records what OCCT 7.8.1 was measured doing, which "
      "includes its bugs.")
    A("3. Run your kernel over the cited `.stp` files and compare.")
    A("")

    A("## The one caveat that matters")
    A("")
    A("The tiering below is derived from **observed reference-engine behaviour**, not from a "
      "judgement about correctness. In particular `empty` — the file parsed but no shape came "
      "back — is sometimes exactly right (a garbage file *should* yield nothing) and sometimes "
      "the worst possible outcome (a valid solid silently vanished). The corpus cannot tell "
      "these apart from the token alone; the per-fixture `Expected kernel behavior` field can. "
      "Treat T1 as *\"look here first\"*, not as *\"these are all bugs\"*.")
    A("")

    A("## What this page does *not* cover")
    A("")
    # Both gaps are stated with live numbers, and whichever is currently the
    # LARGER one is named as such. Hard-coding "spec coverage is the biggest
    # gap" was true at 70% and became wrong at 97% -- the page must not keep
    # asserting a ranking it no longer measures.
    n_spec = sum(1 for f in tok if f in specced)
    total_fix = len(tok)
    spec_pct = 100.0 * n_spec / total_fix if total_fix else 0.0
    link_pct = 100.0 * n_fix / total_fix if total_fix else 0.0
    spec_gap, link_gap = total_fix - n_spec, total_fix - n_fix
    biggest = "linkage" if link_gap > spec_gap else "spec coverage"

    A(f"**{n_spec} of the {total_fix} STEP fixtures ({spec_pct:.0f}%) carry a written "
      f"`Expected kernel behavior`.** The other {spec_gap} are real fixtures with real, "
      "CI-verified assertions — they are good *tests* — but they do not state what a correct "
      "kernel should do, so they teach an implementer nothing on their own. They are marked † "
      "below. Most of that remainder is deliberate: an entry whose bytes were found to "
      "contradict its own title is left unspecced ON PURPOSE, because a specification written "
      "on a disproved claim would propagate the error rather than fix it.")
    A("")
    A(f"It cites **{n_fix} of the {total_fix} STEP fixtures ({link_pct:.0f}%)**. The other "
      f"{link_gap} are real, CI-verified fixtures that simply have not been linked to a named "
      "repair mechanism yet — they are reachable through the catalog and "
      "[`browse/`](browse/), just not from here. So this is a *starting* map, not an "
      "exhaustive one: finishing a tier does not mean you have handled everything the corpus "
      "knows about. Growing the linkage is tracked in `occt-coverage/`.")
    A("")
    A(f"> Of the two, **{biggest} is currently the larger gap** "
      f"({max(spec_gap, link_gap)} fixtures vs {min(spec_gap, link_gap)}).")
    A("")

    A("## Tier summary")
    A("")
    A("| tier | meaning | mechanisms |")
    A("|---|---|---:|")
    for lbl in ["T0 crash-exposing", "T1 silent-empty dominant", "T2 loads-and-heals"]:
        meaning = {
            "T0 crash-exposing": "at least one fixture **aborts** the reference engine — a kernel must never do this",
            "T1 silent-empty dominant": "most fixtures parse but yield **no geometry** — silent loss, check these early",
            "T2 loads-and-heals": "the file loads; the question is whether the repair was **faithful**",
        }[lbl]
        A(f"| `{lbl.split()[0]}` | {meaning} | {tally.get(lbl, 0)} |")
    A("")

    cur = None
    for r in rows:
        if r["label"] != cur:
            cur = r["label"]
            A("")
            A(f"## {cur}")
            A("")
        c = r["counts"]
        mix = ", ".join(f"{k}×{v}" for k, v in c.most_common())
        desc = r["desc"]
        if len(desc) > 400:
            desc = desc[:397].rsplit(" ", 1)[0] + "…"
        A(f"### `{r['id']}`")
        A("")
        sp = r["specced"]
        spec_note = (f"**{sp}/{len(r['fids'])} carry a written spec**"
                     if sp else "**none carry a written spec — read the files**")
        A(f"*{r['domain']}* · {len(r['fids'])} fixtures · observed: {mix} · "
          f"{spec_note} · corpus coverage: {r['verdict']}")
        A("")
        if desc:
            A(desc)
            A("")
        show = r["fids"][:12]
        listed = ", ".join(f"`{f}`" + ("" if f in specced else " †") for f in show)
        more = "" if len(r["fids"]) <= 12 else f" …and {len(r['fids']) - 12} more"
        A(f"**Test against:** {listed}{more}")
        if any(f not in specced for f in show):
            A("")
            A("<sub>† file + CI-checked assertions only — no written "
              "`Expected kernel behavior`. Read the `.stp` and the live oracle result.</sub>")
        A("")

    open(OUT, "w").write("\n".join(L) + "\n")
    print(f"Wrote {OUT}: {len(rows)} mechanisms, {n_fix} fixtures cited")
    for lbl, n in tally.most_common():
        print(f"  {lbl:28} {n}")


if __name__ == "__main__":
    main()
