"""Cross-cutting defect-class taxonomy for the STEP problem catalog.

The catalog markdown organizes entries by §12.x section
(location-in-corpus). This module adds an orthogonal browse axis that
answers a different question: *what kind of defect is this?*

Tag vocabulary (exactly 15 tags, intentionally small)::

    crash             kernel-side crash (signal-11, runtime-error, OOM)
    silent-loss       data dropped without diagnostic
    round-trip        surfaces only on save->reload cycle
    spec-violation    input violates ISO 10303 / AP-spec text
    interop           vendor-A-vs-vendor-B disagreement
    performance       DoS / slow / quadratic / OOM-class
    adversarial       designed to attack parser / allocator / fs
    geometry          B-rep / NURBS / surface / curve defect
    topology          shell / wire / face / edge / vertex defect
    pmi               PMI / GD&T / dimension / annotation defect
    assembly          assembly / hierarchy / instance / placement
    encoding          BOM / UTF / ASCII / character-set defect
    syntax            Part-21 grammar / framing defect
    units             mm / inch / context / unit-conversion defect
    writer            producer-side / export-time defect (§12.13)

Each entry receives 1-3 tags. Tags are derived deterministically from
existing entry fields (section, expected_validation, notes, sources,
title, description); the markdown remains the source of truth.
"""
from __future__ import annotations

from typing import Iterable

# Canonical 15-tag vocabulary. Order is presentation order; tag pages,
# legend, etc. should iterate in this order.
TAG_VOCABULARY: tuple[str, ...] = (
    "crash",
    "silent-loss",
    "round-trip",
    "spec-violation",
    "interop",
    "performance",
    "adversarial",
    "geometry",
    "topology",
    "pmi",
    "assembly",
    "encoding",
    "syntax",
    "units",
    "writer",
)

TAG_SET = frozenset(TAG_VOCABULARY)

# Human-friendly descriptions for the by-tag pages.
TAG_DESCRIPTIONS: dict[str, str] = {
    "crash":          "Kernel-side crash (signal-11 / segfault, runtime-error, infinite-loop, OOM).",
    "silent-loss":    "Data silently dropped without a diagnostic (faces, colors, labels, geometry).",
    "round-trip":     "Defect surfaces only on a save->reload cycle.",
    "spec-violation": "Input violates ISO 10303 / AP-spec text and should be rejected.",
    "interop":        "Vendor-A vs vendor-B disagreement; cross-product inconsistencies.",
    "performance":    "DoS, slow, quadratic, or OOM-class scaling pathologies.",
    "adversarial":    "Designed to attack parser, allocator, or file-system handling.",
    "geometry":       "B-rep / NURBS / surface / curve defect.",
    "topology":       "Shell / wire / face / edge / vertex topology defect.",
    "pmi":            "PMI / GD&T / dimension / annotation defect.",
    "assembly":       "Assembly hierarchy / instance graph / placement defect.",
    "encoding":       "BOM / UTF / ASCII / character-set defect.",
    "syntax":         "Part-21 grammar / framing / lexical defect.",
    "units":          "mm / inch / context / unit-conversion defect.",
    "writer":         "Producer-side / export-time defect (§12.13 Wr*).",
}


# ---------------------------------------------------------------------------
# Section_dir -> primary tag mapping
# ---------------------------------------------------------------------------

# Each entry's section_dir always contributes one tag from this map. A few
# section_dirs (12-4-tolerance, 12-8-mixed) don't map to one of the 15
# vocabulary tags directly; entries there get tags from the cross-cutting
# rules (crash / silent-loss / round-trip / spec-violation / interop) and
# from any auxiliary cues described below.
SECTION_TO_TAG: dict[str, str] = {
    "12-13-writer-pathology": "writer",
    "12-11-adversarial":      "adversarial",
    "12-10-perf":             "performance",
    "12-12-cross-product":    "interop",
    "12-6-assembly":          "assembly",
    "12-7-pmi":               "pmi",
    "12-5-units":             "units",
    "12-1a-encoding":         "encoding",
    "12-1b-header":           "syntax",
    "12-1c-syntax":           "syntax",
    "12-2a-pcurves":          "geometry",
    "12-2b-nurbs":            "geometry",
    "12-2c-surfaces":         "geometry",
    "12-3a-shells":           "topology",
    "12-3b-wires":            "topology",
    "12-3c-faces":            "topology",
    # 12-4-tolerance and 12-8-mixed have no single best section-tag; they
    # rely on cross-cutting cues plus the section-keyword fallback below.
}


# ---------------------------------------------------------------------------
# Cross-cutting tag derivation
# ---------------------------------------------------------------------------

_CRASH_NOTES_KEYWORDS = (
    "crash",
    "segfault",
    "signal 11",
    "signal(11)",
    "infinite loop",
    "infinite-loop",
    "stack overflow",
    "stack-overflow",
    "oom",
)

_SILENT_LOSS_NOTES_KEYWORDS = (
    "silently accept",
    "silently accepts",
    "silently drop",
    "silently drops",
    "silent-accept observed",
    "silent accept",
    "silent drop",
    "silently ignore",
)

_ROUND_TRIP_KEYWORDS = (
    "round-trip",
    "round trip",
    "after import",
    "on export",
    "on round-trip",
    "save/reload",
    "save then reload",
    "re-export",
)


def _has_crash(entry: dict) -> bool:
    ev = (entry.get("expected_validation") or "").lower()
    if "signal(11)" in ev or "signal(" in ev or "process_signal" in ev:
        return True
    notes = (entry.get("notes") or "").lower()
    occ_note = (entry.get("occ_behavior_note") or "").lower()
    blob = notes + " " + occ_note
    return any(kw in blob for kw in _CRASH_NOTES_KEYWORDS)


def _has_silent_loss(entry: dict) -> bool:
    notes = (entry.get("notes") or "").lower()
    occ_note = (entry.get("occ_behavior_note") or "").lower()
    blob = notes + " " + occ_note
    return any(kw in blob for kw in _SILENT_LOSS_NOTES_KEYWORDS)


def _has_round_trip(entry: dict) -> bool:
    title = (entry.get("title") or "").lower()
    desc = (entry.get("description") or "").lower()
    blob = title + " " + desc
    return any(kw in blob for kw in _ROUND_TRIP_KEYWORDS)


def _has_spec_violation(entry: dict) -> bool:
    sources = " ".join(entry.get("sources") or []).lower()
    ekb = (entry.get("expected_kernel_behavior") or "").lower()
    has_iso = "iso 10303" in sources or "iso-10303" in sources or "iso10303" in sources
    has_spec = has_iso or "ap214" in sources or "ap242" in sources or "ap203" in sources \
        or "part 21" in sources or "part-21" in sources or "spec" in sources
    if not has_spec:
        return False
    return "reject" in ekb


# Auxiliary keyword cues for entries whose section_dir doesn't pin a tag
# (12-4-tolerance, 12-8-mixed). These look at the title/category/description
# for strong topical signals and only contribute if no section_dir tag was
# assigned, to avoid over-tagging.
_KEYWORD_CUES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("pmi",       ("pmi", "gd&t", "tolerance frame", "datum", "annotation",
                   "dimensional tolerance", "geometric tolerance")),
    ("assembly",  ("assembly", "nauo", "next_assembly_usage", "instance graph",
                   "mapped_item", "axis2_placement")),
    ("units",     ("unit", "millimet", "inch", "scale", "conversion")),
    ("topology",  ("shell", "wire", "edge", "face_bound", "vertex", "loop")),
    ("geometry",  ("nurbs", "b-spline", "bspline", "pcurve", "surface", "curve",
                   "knot")),
    ("syntax",    ("part-21", "part 21", "header", "grammar", "tokeniz",
                   "instance number", "anchor")),
    ("encoding",  ("bom", "utf-8", "utf8", "utf-16", "encoding", "ascii")),
)


def _keyword_fallback_tag(entry: dict) -> str | None:
    """Pick a best-fit content tag from title/category/description keywords.

    Used as a fallback for sections whose section_dir doesn't itself map to
    a vocabulary tag (12-4-tolerance, 12-8-mixed).
    """
    blob = " ".join([
        entry.get("title") or "",
        entry.get("category") or "",
        entry.get("description") or "",
    ]).lower()
    for tag, keywords in _KEYWORD_CUES:
        for kw in keywords:
            if kw in blob:
                return tag
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def derive(entry: dict) -> list[str]:
    """Return the deduplicated tag list for one catalog entry.

    Each entry receives 1-3 tags. The ordering follows ``TAG_VOCABULARY``
    so the output is deterministic across runs.
    """
    tags: set[str] = set()

    # 1. Section-derived tag (covers ~14 of 18 section_dirs).
    section_dir = entry.get("section_dir") or ""
    section_tag = SECTION_TO_TAG.get(section_dir)
    if section_tag is not None:
        tags.add(section_tag)

    # 2. Cross-cutting tags. These can stack on top of the section tag.
    if _has_crash(entry):
        tags.add("crash")
    if _has_silent_loss(entry):
        tags.add("silent-loss")
    if _has_round_trip(entry):
        tags.add("round-trip")
    if _has_spec_violation(entry):
        tags.add("spec-violation")

    # 3. Fallback: if we still have no tags (e.g. 12-4-tolerance / 12-8-mixed
    #    entry that doesn't crash, isn't silent-loss, etc.), pick a best-fit
    #    keyword tag so every entry gets at least one tag.
    if not tags:
        fb = _keyword_fallback_tag(entry)
        if fb is not None:
            tags.add(fb)

    # 4. Cap at 3 tags. If we somehow accumulated more, drop the lowest-
    #    priority cross-cutting ones first (round-trip then spec-violation,
    #    then silent-loss). Section tags and crash always survive.
    if len(tags) > 3:
        priority = (
            "crash", "writer", "adversarial", "performance", "interop",
            "assembly", "pmi", "units", "encoding", "syntax", "geometry",
            "topology", "silent-loss", "spec-violation", "round-trip",
        )
        kept: list[str] = []
        for t in priority:
            if t in tags:
                kept.append(t)
                if len(kept) == 3:
                    break
        tags = set(kept)

    # 5. Final guard: every entry gets at least one tag. If derivation
    #    produced nothing, default to the best fallback we have (section
    #    label as a last resort). This should never trigger in practice
    #    but keeps the invariant testable.
    if not tags:
        tags.add("spec-violation")  # neutral catch-all: an unhandled defect

    # Return in canonical vocabulary order for determinism.
    return [t for t in TAG_VOCABULARY if t in tags]


def derive_all(entries: Iterable[dict]) -> dict[str, list[str]]:
    """Convenience: return ``{id: [tags]}`` for an iterable of entries."""
    return {e["id"]: derive(e) for e in entries}


def main(argv: list[str] | None = None) -> int:
    """CLI: dump derived tags for every catalog entry to /tmp/cad-taxonomy.json.

    Useful for spot-checks during catalog edits; it's deterministic from
    the JSON catalog so re-running yields a stable file.
    """
    import json
    from pathlib import Path

    from step_corpus import catalog

    out_path = Path("/tmp/cad-taxonomy.json")
    if argv:
        out_path = Path(argv[0])
    entries = catalog.load_catalog()
    tags = derive_all(entries)
    out_path.write_text(
        json.dumps(tags, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(tags)} entries to {out_path}")
    return 0


__all__ = [
    "TAG_VOCABULARY",
    "TAG_SET",
    "TAG_DESCRIPTIONS",
    "SECTION_TO_TAG",
    "derive",
    "derive_all",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
