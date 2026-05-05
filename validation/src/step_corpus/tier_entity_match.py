"""Tier: catalog↔fixture entity-citation match.

Drift detector: every canonical entry in ``STEP_PROBLEM_CATALOG.md`` carries
a ``**Reproducer recipe**:`` field that names the STEP entity types the
fixture is supposed to demonstrate (e.g. ``MANIFOLD_SOLID_BREP``,
``EDGE_LOOP``, ``TOROIDAL_SURFACE``). This module pulls those entity-type
tokens out of the recipe and confirms they all show up at least once in the
matching ``.stp`` fixture. A low ``match_ratio`` means either:

1. The catalog was edited but the fixture wasn't refreshed (stale fixture).
2. The fixture was rebuilt with a different scaffold but the catalog text
   wasn't updated (stale recipe).
3. The recipe is intentionally abstract -- e.g. §12.10 perf entries
   describe scaling patterns ("thousands of MANIFOLD_SOLID_BREPs in nested
   NEXT_ASSEMBLY_USAGE_OCCURRENCE chains") that no minimal reproducer can
   honour. The pytest layer is lenient in those sections.

Public API:

    extract_entry_blocks(catalog_text)        -> dict[id, block]
    extract_cited_entities(recipe_text)       -> list[str]
    check_fixture(fixture_path, entry_block)  -> dict
    iter_canonical_entries(catalog_text)      -> generator over (id, block)

The ``check_fixture`` return is::

    {
      "id":          "Tsh026",
      "recipe":      "<verbatim recipe line>",
      "cited":       ["ADVANCED_FACE", "PLANE", "CLOSED_SHELL"],
      "present":     ["ADVANCED_FACE", "PLANE", "CLOSED_SHELL"],
      "missing":     [],
      "match_ratio": 1.0,
      "abstract":    False,
    }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, Iterator

# ---------------------------------------------------------------------------
# Regexes & vocabulary
# ---------------------------------------------------------------------------

# Match ``### Le001 — Title`` style headers. Catalog uses an em-dash (—).
_ENTRY_HEADER = re.compile(r"^### ([A-Za-z]+\d+)\b", re.MULTILINE)

# Match ``- **Reproducer recipe**: <text>`` (recipe text is the rest of the line).
# In practice every catalog recipe is one line; if it is not, we err on the
# side of capturing too little rather than swallowing the next bullet.
_RECIPE_LINE = re.compile(r"^- \*\*Reproducer recipe\*\*:\s*(.+)$", re.MULTILINE)

# A candidate entity-type token. STEP entity names are uppercase ASCII with
# underscores and digits, and at least 3 characters long. We also accept
# tokens enclosed in backticks.
_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")

# Tokens the regex picks up that are NOT STEP entity types. Kept tight on
# purpose: we'd rather report a spurious miss than silently filter a real
# entity type. Tuned against Le001 / Tsh026 / Tfa011 / Pmi049 plus a wider
# spot-check across the corpus.
_DENYLIST: frozenset[str] = frozenset({
    # Standards / schemas / acronyms commonly cited in recipes.
    "STEP", "ISO", "OCCT", "AP203", "AP214", "AP242", "AP238", "BOM",
    "IFC", "STL", "OBJ", "VRML", "JT", "PDF", "PMI", "GD", "FEA", "CFD",
    "SAT", "CAD", "API", "DLL", "URL", "URI", "RGB", "UTC", "DST", "GMT",
    "MIME", "JSON", "XML", "CSV", "ASCII", "ANSI", "EBU", "EBNF", "BNF",
    "UCS", "UTF", "UTF8", "UTF16", "UTF32", "BOM", "BIG5", "EUC",
    "NIST", "STEPCODE", "STEPVIEW",
    # Editions / version strings the recipes mention.
    "ED", "ED2", "ED3", "EDITION",
    # Hex byte sequences and similar literal payloads commonly appearing in
    # recipes ("EF BB BF", "FE FF", "FFFE"). Two-byte hex pairs already fail
    # the >=3-char length filter; cover the ones that slip through.
    "FFFE", "FEFF", "BFEF", "BBEF",
    # Encodings & character sets.
    "ISO_8859", "ISO8859", "LATIN1", "LATIN2", "WIN1252",
    # Generic English / writing tokens that happen to be ALL-CAPS.
    "TODO", "FIXME", "NOTE", "WARNING", "ERROR", "HEADER", "DATA", "ENDSEC",
    "FILE", "SCHEMA", "ANCHOR", "REFERENCE", "SIGNATURE",
    # Domain-specific abbreviations that are not entity types.
    "NURBS", "CSG", "BREP", "BIM", "MES", "MBD",
    # SI unit symbols / prefixes that occasionally appear in caps.
    "SI", "MKS",
    # Catalog-specific tags & status keywords.
    "MERGED", "PENDING", "CANONICAL", "DEFECT", "TRUE", "FALSE",
    # Part-21 / EXPRESS keywords that look like entity types.
    "EXPRESS", "STRING", "INTEGER", "REAL", "BOOLEAN", "LOGICAL", "BINARY",
    "ENTITY", "ATTRIBUTE", "OPTIONAL", "INVERSE", "DERIVE", "WHERE",
    # CAD vendor names that occasionally appear in caps in recipes.
    "CATIA", "INVENTOR", "SOLIDWORKS", "FREECAD", "CREO", "RHINO",
    "AUTOCAD", "NAVISWORKS", "BAMBU", "KICAD", "OPENSCAD", "GMSH",
    "PARASOLID", "ACIS", "OCC",
    # Common error code prefixes used as backticked tokens.
    "E_BAD_X_DIRECTIVE", "E_BAD_X2_DIRECTIVE", "E_BAD_X4_DIRECTIVE",
    "E_BAD_PAGE_DIRECTIVE", "E_UNEXPECTED_BOM", "E_INSTANCE_LIMIT",
    # Filename-ish things.
    "STP", "P21",
    # Misc.
    "OPEN", "CLOSED",  # bare; "OPEN_SHELL" / "CLOSED_SHELL" still match.
    "MAKE", "MAKEFACE", "REHOST",
})

# Sections whose recipes are intentionally abstract (perf / adversarial).
# pytest is lenient on these: they contribute to the report but never to the
# failure threshold.
_ABSTRACT_SECTION_PREFIXES: tuple[str, ...] = ("Pf", "Ad")


# ---------------------------------------------------------------------------
# Catalog parsing
# ---------------------------------------------------------------------------


def extract_entry_blocks(catalog_text: str) -> dict[str, str]:
    """Split the catalog into ``{id: block}`` for every ``### <ID> — title``
    header. Each block runs from its own header up to the next header.
    """
    blocks: dict[str, str] = {}
    matches = list(_ENTRY_HEADER.finditer(catalog_text))
    for i, m in enumerate(matches):
        eid = m.group(1)
        # Skip the literal template ``### {ID} — Short title`` line.
        if eid == "ID":  # pragma: no cover -- template header skipped by id shape
            continue
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(catalog_text)
        blocks[eid] = catalog_text[start:end]
    return blocks


def is_canonical(block: str) -> bool:
    """A canonical entry has ``Status: pending`` (or absent, defensive).
    Merged stubs say ``Status: merged → <other>`` and have no recipe.
    """
    return "**Status**: merged" not in block


def extract_recipe(block: str) -> str | None:
    """Return the verbatim recipe-line text, or ``None`` if missing."""
    m = _RECIPE_LINE.search(block)
    if not m:
        return None
    return m.group(1).strip()


def iter_canonical_entries(catalog_text: str) -> Iterator[tuple[str, str]]:
    """Yield ``(id, block)`` for every canonical entry that has a recipe."""
    for eid, block in extract_entry_blocks(catalog_text).items():
        if not is_canonical(block):
            continue
        if extract_recipe(block) is None:
            continue
        yield eid, block


# ---------------------------------------------------------------------------
# Token extraction
# ---------------------------------------------------------------------------


def extract_cited_entities(recipe_text: str) -> list[str]:
    """Pull plausible STEP entity-type tokens out of one recipe string.

    Returned in first-seen order, deduplicated, denylist-filtered.
    """
    seen: list[str] = []
    seen_set: set[str] = set()
    for tok in _TOKEN_RE.findall(recipe_text):
        if tok in _DENYLIST:
            continue
        # Reject tokens with no underscore *and* fewer than 5 chars: those are
        # almost always abbreviations like "PLM" or "PCB" rather than entity
        # types. Real STEP types are either underscore-joined (FACE_BOUND)
        # or long single words (TRIANGULATION, TESSELLATION).
        if "_" not in tok and len(tok) < 5:
            continue
        if tok in seen_set:
            continue
        seen.append(tok)
        seen_set.add(tok)
    return seen


# ---------------------------------------------------------------------------
# Fixture check
# ---------------------------------------------------------------------------


def _read_fixture_text(path: Path) -> str:
    """Tolerant read: fixtures may be UTF-8, UTF-16, or contain stray bytes
    (Le031 etc). We only need to find ASCII entity-type tokens, so any
    decoding that preserves ASCII works.
    """
    raw = path.read_bytes()
    # Strip a UTF-16 BOM up front (those fixtures encode entity names in
    # UTF-16 -- decode it). For everything else, latin-1 round-trips bytes.
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            return raw.decode("utf-16")
        except UnicodeDecodeError:
            return raw.decode("latin-1", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def check_fixture(fixture_path: Path, entry_block: str) -> dict:
    """Run the entity-match check.

    Parameters
    ----------
    fixture_path : Path
        Absolute path to the ``.stp`` file.
    entry_block : str
        The raw markdown block for the catalog entry, as produced by
        :func:`extract_entry_blocks`.
    """
    recipe = extract_recipe(entry_block) or ""
    cited = extract_cited_entities(recipe)
    eid_match = _ENTRY_HEADER.search(entry_block)
    eid = eid_match.group(1) if eid_match else ""

    abstract = eid.startswith(_ABSTRACT_SECTION_PREFIXES)

    if not fixture_path.exists():
        return {
            "id": eid,
            "fixture": str(fixture_path),
            "recipe": recipe,
            "cited": cited,
            "present": [],
            "missing": cited,
            "match_ratio": 0.0 if cited else 1.0,
            "abstract": abstract,
            "fixture_missing": True,
        }

    text = _read_fixture_text(fixture_path)
    # We look for whole-word matches, anchored on STEP token boundaries
    # (``=`` for entity assignments, ``(`` for inline use, plus whitespace).
    # A simple ``token in text`` would be tricked by substring overlaps:
    # ``CIRCLE`` is a substring of ``CIRCLE_3D_REPRESENTATION``. Use a
    # word-boundary regex per token instead.
    present: list[str] = []
    missing: list[str] = []
    for tok in cited:
        if re.search(rf"\b{re.escape(tok)}\b", text):
            present.append(tok)
        else:
            missing.append(tok)

    if not cited:
        ratio = 1.0
    else:
        ratio = len(present) / len(cited)

    return {
        "id": eid,
        "fixture": str(fixture_path),
        "recipe": recipe,
        "cited": cited,
        "present": present,
        "missing": missing,
        "match_ratio": ratio,
        "abstract": abstract,
        "fixture_missing": False,
    }


# ---------------------------------------------------------------------------
# Corpus runner
# ---------------------------------------------------------------------------

# Map ID prefix -> step-examples subdirectory.
_PREFIX_TO_DIR: dict[str, str] = {
    "Le":  "12-1a-encoding",
    "Lh":  "12-1b-header",
    "Ls":  "12-1c-syntax",
    "In":  "12-1c-syntax",      # Interface/Transfer
    "Gp":  "12-2a-pcurves",
    "Gn":  "12-2b-nurbs",
    "Gs":  "12-2c-surfaces",
    "Gb":  "12-2c-surfaces",    # TKGeomBase
    "Tsh": "12-3a-shells",
    "Bo":  "12-3a-shells",      # BRepCheck/Builder
    "Sw":  "12-3a-shells",      # BRepBuilderAPI_Sewing
    "Hea": "12-3c-faces",       # shape-healing umbrella
    "Ps":  "12-3a-shells",      # pathological-success
    "Twi": "12-3b-wires",
    "Tfa": "12-3c-faces",
    "N":   "12-4-tolerance",
    "Tb":  "12-4-tolerance",    # time-bombs
    "U":   "12-5-units",
    "A":   "12-6-assembly",
    "P":   "12-6-assembly",   # FreeCAD-derived P001..P028
    "Pmi": "12-7-pmi",
    "M":   "12-8-mixed",
    "Fi":  "12-8-mixed",        # BRepFilletAPI
    "Os":  "12-8-mixed",        # BRepOffsetAPI
    "Pf":  "12-10-perf",
    "Ad":  "12-11-adversarial",
    "Xp":  "12-12-cross-product",  # cross-product synthesized defects
    "Wr":  "12-13-writer-pathology",  # writer pathology
}


def _id_to_prefix(eid: str) -> str:
    """Return the longest matching prefix from ``_PREFIX_TO_DIR``."""
    # Order matters: ``Pmi`` and ``Pf`` must beat ``P``, ``Tsh``/``Tfa``/``Twi``
    # must beat anything starting with ``T``, etc.
    for prefix in sorted(_PREFIX_TO_DIR, key=len, reverse=True):
        if eid.startswith(prefix):
            # Make sure the next char is a digit, so e.g. ``Le`` doesn't
            # eat ``Lh001``. (All categorisation prefixes end before a digit.)
            tail = eid[len(prefix):]
            if tail and tail[0].isdigit():
                return prefix
    return ""


def fixture_path_for_id(examples_root: Path, eid: str) -> Path | None:
    prefix = _id_to_prefix(eid)
    if not prefix:
        return None
    return examples_root / _PREFIX_TO_DIR[prefix] / f"{eid}.stp"


def run_corpus(catalog_path: Path, examples_root: Path) -> list[dict]:
    """Run the entity-match check across every canonical entry."""
    catalog_text = catalog_path.read_text()
    out: list[dict] = []
    for eid, block in iter_canonical_entries(catalog_text):
        fpath = fixture_path_for_id(examples_root, eid)
        if fpath is None:
            continue
        out.append(check_fixture(fpath, block))
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    # This file lives at: <repo-root>/validation/src/step_corpus/tier_entity_match.py
    # So the repo root is parents[3].
    _repo_root = Path(__file__).resolve().parents[3]
    ap.add_argument(
        "--catalog",
        default=str(_repo_root / "STEP_PROBLEM_CATALOG.md"),
    )
    ap.add_argument(
        "--examples",
        default=str(_repo_root / "step-examples"),
    )
    ap.add_argument(
        "--id",
        help="Check a single entry (e.g. Le001). If omitted, run the corpus.",
    )
    ap.add_argument(
        "--threshold", type=float, default=0.5,
        help="match_ratio threshold below which an entry is 'failing' (default 0.5).",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(list(argv) if argv is not None else None)

    catalog_path = Path(args.catalog)
    examples_root = Path(args.examples)

    if args.id:
        block = extract_entry_blocks(catalog_path.read_text()).get(args.id)
        if block is None:
            print(f"unknown entry: {args.id}", file=sys.stderr)
            return 2
        fpath = fixture_path_for_id(examples_root, args.id)
        if fpath is None:
            print(f"no fixture path for: {args.id}", file=sys.stderr)
            return 2
        result = check_fixture(fpath, block)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_one(result)
        return 0

    results = run_corpus(catalog_path, examples_root)
    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    bad = [r for r in results if r["match_ratio"] < args.threshold and not r["abstract"]]
    abstract_bad = [r for r in results if r["match_ratio"] < args.threshold and r["abstract"]]
    print(f"checked {len(results)} canonical entries")
    print(f"  {len(bad)} entries below {args.threshold:.0%} match (concrete)")
    print(f"  {len(abstract_bad)} entries below {args.threshold:.0%} match (abstract -- §12.10/§12.11)")
    print()
    print("worst (concrete):")
    for r in sorted(bad, key=lambda x: x["match_ratio"])[:25]:
        print(
            f"  {r['id']:>6}  ratio={r['match_ratio']:.2f}  "
            f"missing={r['missing']}"
        )
    return 0


def _print_one(r: dict) -> None:
    print(f"{r['id']}  ratio={r['match_ratio']:.2f}")
    print(f"  recipe : {r['recipe']}")
    print(f"  cited  : {r['cited']}")
    print(f"  present: {r['present']}")
    print(f"  missing: {r['missing']}")
    if r.get("fixture_missing"):
        print("  (fixture file not found)")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
