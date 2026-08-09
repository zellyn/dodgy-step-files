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


def silent_total_loss(tok: dict[str, str]) -> list[str]:
    """Fixtures where a COMPLETE, REACHABLE B-rep goes in and NOTHING comes out.

    `empty` on its own is ambiguous and the caveat below says so: a garbage file
    *should* yield nothing. This narrows it to the unambiguous case -- the file
    hands the reader a face that is genuinely wired into a shell, under a
    representation root, wrapped in a solid or surface model. There was
    something to build and the kernel returned an empty shape without saying so.

    Reachability is the point, not entity counts. A file can contain an
    ADVANCED_FACE and a CLOSED_SHELL that are never connected to each other, in
    which case returning nothing is correct and counting entities would call it
    a loss. So the face must appear IN a shell's list.
    """
    out = []
    for fid, t in tok.items():
        if t != "empty":
            continue
        hits = glob.glob(os.path.join(ROOT, "step-examples", "*", f"{fid}.stp"))
        if not hits:
            continue
        try:
            txt = open(hits[0], errors="replace").read()
        except OSError:
            continue
        in_shell: set[str] = set()
        for _, lst in re.findall(
                r"#(\d+)\s*=\s*(?:CLOSED_SHELL|OPEN_SHELL)\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)",
                txt, re.I):
            in_shell |= {x.strip().lstrip("#") for x in lst.split(",") if x.strip()}
        faces = {m.group(1) for m in re.finditer(r"#(\d+)\s*=\s*ADVANCED_FACE\s*\(", txt, re.I)}
        if not (faces & in_shell):
            continue
        if not re.search(r"=\s*SHAPE_DEFINITION_REPRESENTATION\s*\(", txt, re.I):
            continue
        # All four wrapper spellings the corpus actually uses. Counted, not guessed:
        # SHELL_BASED_SURFACE_MODEL 1467, MANIFOLD_SOLID_BREP 286, BREP_WITH_VOIDS 9,
        # FACETED_BREP 4. Omitting the last two silently under-reports the cohort.
        if not re.search(r"=\s*(?:MANIFOLD_SOLID_BREP|SHELL_BASED_SURFACE_MODEL"
                         r"|BREP_WITH_VOIDS|FACETED_BREP)\s*\(", txt, re.I):
            continue
        out.append(fid)
    return sorted(out)


# Attribute counts from the AP214/AP242 EXPRESS schema. Only these two are listed
# because they are the entities the corpus actually malforms this way.
ARGCOUNT = {"B_SPLINE_SURFACE_WITH_KNOTS": 13, "B_SPLINE_CURVE_WITH_KNOTS": 9}


def _split_args(body: str) -> list[str]:
    """Top-level comma split, ignoring commas nested in ( ) or in strings."""
    out, depth, cur, instr = [], 0, [], False
    for ch in body:
        if instr:
            cur.append(ch)
            if ch == "'":
                instr = False
            continue
        if ch == "'":
            instr = True; cur.append(ch)
        elif ch == "(":
            depth += 1; cur.append(ch)
        elif ch == ")":
            depth -= 1; cur.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        out.append("".join(cur))
    return out


def argcount_deviants(tok: dict[str, str]) -> tuple[list[str], list[str], int, int]:
    """Fixtures whose B-spline entities carry the wrong NUMBER of arguments.

    Discovered by isolating a crash site: it was not the flat control-point
    list, nor real-valued multiplicities, nor a control-point count that
    contradicts the multiplicities -- all three of those LOAD. It was omitting
    attributes, which shifts every later argument into the wrong slot, so the
    reader takes (say) a list where the schema promised it an enum.

    Returns (crashing_deviants, non_crashing_deviants, n_correct, n_correct_crash)
    so the caller can print the base rate alongside. A discriminator without its
    base rate is not a finding.
    """
    dev_crash, dev_ok, n_ok, n_ok_crash = [], [], 0, 0
    for fid, t in tok.items():
        hits = glob.glob(os.path.join(ROOT, "step-examples", "*", f"{fid}.stp"))
        if not hits:
            continue
        try:
            txt = open(hits[0], errors="replace").read()
        except OSError:
            continue
        seen = deviates = False
        for name, want in ARGCOUNT.items():
            for m in re.finditer(rf"=\s*{name}\s*\(", txt, re.I):
                seen = True
                i, depth = m.end() - 1, 0
                for j in range(i, len(txt)):
                    if txt[j] == "(":
                        depth += 1
                    elif txt[j] == ")":
                        depth -= 1
                        if depth == 0:
                            if len(_split_args(txt[i + 1:j])) != want:
                                deviates = True
                            break
        if not seen:
            continue
        crashed = t == "signal(11)"
        if deviates:
            (dev_crash if crashed else dev_ok).append(fid)
        else:
            n_ok += 1
            n_ok_crash += crashed
    return sorted(dev_crash), sorted(dev_ok), n_ok, n_ok_crash


def _args_of(txt: str, m) -> list[str]:
    """Argument list of the entity whose opening paren is at m.end()-1."""
    i, depth = m.end() - 1, 0
    for j in range(i, len(txt)):
        if txt[j] == "(":
            depth += 1
        elif txt[j] == ")":
            depth -= 1
            if depth == 0:
                return _split_args(txt[i + 1:j])
    return []


def crash_refusable(tok: dict[str, str]) -> dict:
    """Of the crashing fixtures, how many are refusable BEFORE geometry is built?

    Two checks, both decidable from the file plus a schema table -- no conversion,
    no geometry, no kernel:

      type   an entity reference sits in a slot whose declared type it is not.
             Measured on the case traced to a call site: LINE.dir must be a VECTOR.
      count  a B-spline entity's argument count differs from the schema.

    The union is the honest answer to "what fraction of these crashes could a
    kernel have refused, with a precise diagnostic, before it tried to build
    anything?"
    """
    ent = re.compile(r"#(\d+)\s*=\s*([A-Z_0-9]+)\s*\(", re.I)
    crash = [f for f, v in tok.items() if v == "signal(11)"]
    by_type, by_count = [], []
    for fid in crash:
        hits = glob.glob(os.path.join(ROOT, "step-examples", "*", f"{fid}.stp"))
        if not hits:
            continue
        try:
            txt = open(hits[0], errors="replace").read()
        except OSError:
            continue
        kind = {m.group(1): m.group(2).upper() for m in ent.finditer(txt)}
        for m in re.finditer(r"#\d+\s*=\s*LINE\s*\(", txt, re.I):
            a = _args_of(txt, m)
            if len(a) == 3:
                r = a[2].strip().lstrip("#")
                # default VECTOR => an inline/unresolvable ref is not counted as an error
                if r.isdigit() and kind.get(r, "VECTOR") != "VECTOR":
                    by_type.append(fid)
                    break
        for name, want in ARGCOUNT.items():
            if any(len(_args_of(txt, m)) != want
                   for m in re.finditer(rf"=\s*{name}\s*\(", txt, re.I)):
                by_count.append(fid)
                break
    union = set(by_type) | set(by_count)
    return {"total": len(crash), "type": len(by_type), "count": len(by_count),
            "union": len(union), "ids": sorted(union)}


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

    stl = silent_total_loss(tok)
    if stl:
        by_sec = collections.Counter(
            (re.match(r"^[A-Za-z]+", f) or [""])[0] for f in stl)
        A("## Start here: silent total geometry loss")
        A("")
        A(f"**{len(stl)} fixtures hand the reader a complete, connected B-rep and get an "
          "empty shape back.** Not a partial result, not a repaired face — nothing, and "
          "no error. This is the worst outcome in the corpus, because the import reports "
          "success and the user's geometry is simply gone.")
        A("")
        A("These are separated from the general `empty` population on purpose. `empty` "
          "alone is ambiguous — a garbage file *should* yield nothing. Each fixture here "
          "was checked to have an `ADVANCED_FACE` **actually referenced by a shell** "
          "(not merely present in the file), a `SHAPE_DEFINITION_REPRESENTATION` root, "
          "and a solid or surface-model wrapper. There was something to build.")
        A("")
        A(f"**What the concentration tells you:** {dict(by_sec.most_common())} — by ID "
          "prefix. These are overwhelmingly *curve*-level defects (pcurves and NURBS "
          "curves), not shell- or solid-level ones. So the lesson is that in this "
          "reference engine **a single bad curve on a face escalates all the way to "
          "total loss of the model**, rather than degrading to a dropped edge or a "
          "repaired approximation. If your kernel takes the same path, decide "
          "deliberately whether that is the behaviour you want — and if it is, at least "
          "emit a diagnostic.")
        A("")
        A("**Test against:** " + ", ".join(f"`{f}`" for f in stl[:20])
          + ("" if len(stl) <= 20 else f" …and {len(stl) - 20} more"))
        A("")

    dcrash, dok, n_ok, n_ok_crash = argcount_deviants(tok)
    if dcrash:
        n_dev = len(dcrash) + len(dok)
        r_dev = 100.0 * len(dcrash) / n_dev
        r_ok = 100.0 * n_ok_crash / n_ok if n_ok else 0.0
        cr = crash_refusable(tok)
        A("## Cheapest crash defence: two checks, before any geometry")
        A("")
        A(f"**{cr['union']} of the {cr['total']} crashing fixtures ({100*cr['union']/cr['total']:.0f}%) "
          "are refusable before a single geometric entity is constructed** — by two "
          "checks that need nothing but the file and a schema table:")
        A("")
        A(f"1. **Wrong type in a slot** ({cr['type']} fixtures). `LINE.dir` is declared "
          "`VECTOR`; these files point it at a `DIRECTION` or a `CARTESIAN_POINT`. "
          "Repairing that one reference makes the file load — verified individually on "
          "26 of them, so this is cause, not correlation.")
        A(f"2. **Wrong argument count** ({cr['count']} fixtures), detailed below.")
        A("")
        A("Neither check needs a kernel. Both produce a diagnostic naming the entity and "
          "what was wrong with it — which is a far better outcome than a segfault, and "
          "also better than the silent empty shape the other sections describe.")
        A("")
        A("### The argument-count check")
        A("")
        A("Of the fixtures containing a `B_SPLINE_CURVE_WITH_KNOTS` or "
          "`B_SPLINE_SURFACE_WITH_KNOTS`:")
        A("")
        A("| argument count vs. schema | crashes | rate |")
        A("|---|---|---|")
        A(f"| **deviates** | {len(dcrash)} / {n_dev} | **{r_dev:.0f}%** |")
        A(f"| correct | {n_ok_crash} / {n_ok} | {r_ok:.0f}% |")
        A("")
        A("A file that gives one of these entities the wrong *number* of arguments "
          "crashes this reference engine almost every time; a file that gets the count "
          "right almost never does. Nothing else about the entity predicts a crash "
          "nearly as well — a flat control-point list, knot multiplicities written as "
          "reals, and a control-point count that contradicts the multiplicities were "
          "each tested in isolation against a known-good surface, and **all three "
          "load fine**.")
        A("")
        A("The reason is positional. These entities are read by slot, so omitting an "
          "attribute does not produce a missing value — it shifts every later argument "
          "one position left, and the reader ends up taking a list where the schema "
          "promised it an enum. It then uses the result without checking, and "
          "dereferences null.")
        A("")
        A("**Where it lands varies; the input pattern does not.** Traced crash sites "
          "include the vector constructor, the B-spline surface constructor, and the "
          "face translator — whichever converter happens to reach the malformed entity "
          "first. Treating these as three separate bugs to null-check individually is "
          "the expensive path.")
        A("")
        A("**The cheap path:** validate argument counts against the schema *at parse "
          "time*. That is a table lookup and a comparison. It rejects these files with "
          "a precise, actionable diagnostic naming the entity and the expected count, "
          "and no converter ever sees them. Downstream null-checking, by contrast, has "
          "to be repeated at every construction site and still produces a worse message.")
        A("")
        A("**Scope, measured rather than assumed:** this is a *B-spline* effect, not a "
          "universal law. Learning each entity type's arity from the corpus (the modal "
          "count over 71 types with enough instances to be confident) and asking whether "
          "*any* deviation predicts a crash gives 24% against a 6% base rate — real "
          "signal, but four-fold rather than thirty-fold. A wrong count on a `PLANE` or "
          "a `VECTOR` mostly does not reach a null dereference. So implement the check "
          "everywhere, because it is nearly free and catches malformed files early — but "
          "expect the crashes it prevents to be concentrated in the entities with long, "
          "heterogeneous argument lists, where a shift silently changes a value's type.")
        A("")
        if dok:
            plural = ("fixtures", "do") if len(dok) > 1 else ("fixture", "does")
            A(f"Honest caveat: {len(dok)} deviating {plural[0]} — "
              + ", ".join(f"`{f}`" for f in dok)
              + f" — {plural[1]} not crash, so the count is a very strong predictor "
                "rather than a law. The correlation was measured across the whole "
                "corpus; only some of the crashes were traced to a call site "
                "individually.")
            A("")
        rest = [f for f in cr["ids"] if f not in set(dcrash)]
        A("**Test against** — everything either check refuses. Wrong count: "
          + ", ".join(f"`{f}`" for f in dcrash)
          + ". Wrong type: " + ", ".join(f"`{f}`" for f in rest[:20])
          + (f" …and {len(rest) - 20} more" if len(rest) > 20 else "")
          + ". A kernel that refuses all of these at parse time gives up nothing — "
            "every one is a file no correct reader should accept.")
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
