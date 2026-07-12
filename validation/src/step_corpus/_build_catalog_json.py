"""Generator for STEP_PROBLEM_CATALOG.json.

Parses ``research/STEP_PROBLEM_CATALOG.md`` and emits a deterministic JSON
array of canonical (non-merged) entries alongside the markdown.

Run from anywhere::

    python -m step_corpus._build_catalog_json

The output is written to ``research/STEP_PROBLEM_CATALOG.json``. Re-running
must produce a byte-identical file (sort_keys=True, deterministic ordering,
trailing newline) so this script is safe to wire into CI.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from step_corpus import _taxonomy

# ---------------------------------------------------------------------------
# Path discovery
# ---------------------------------------------------------------------------

# This file lives at: research/validation/src/step_corpus/_build_catalog_json.py
# So the research root is parents[3].
RESEARCH_ROOT = Path(__file__).resolve().parents[3]
CATALOG_MD = RESEARCH_ROOT / "STEP_PROBLEM_CATALOG.md"
CATALOG_JSON = RESEARCH_ROOT / "STEP_PROBLEM_CATALOG.json"
STEP_EXAMPLES = RESEARCH_ROOT / "step-examples"


# ---------------------------------------------------------------------------
# Section / fixture-directory mapping
# ---------------------------------------------------------------------------

# ID prefix -> (section code, section_dir name under step-examples/)
# Order of keys matters for prefix-resolution: longer prefixes first.
PREFIX_MAP: list[tuple[str, str, str]] = [
    # (prefix, section, section_dir)
    ("Tsh", "12.3a", "12-3a-shells"),
    ("Twi", "12.3b", "12-3b-wires"),
    ("Tfa", "12.3c", "12-3c-faces"),
    ("Pmi", "12.7", "12-7-pmi"),
    ("Le", "12.1a", "12-1a-encoding"),
    ("Lh", "12.1b", "12-1b-header"),
    ("Ls", "12.1c", "12-1c-syntax"),
    ("Gp", "12.2a", "12-2a-pcurves"),
    ("Gn", "12.2b", "12-2b-nurbs"),
    ("Gs", "12.2c", "12-2c-surfaces"),
    ("Gb", "12.2c", "12-2c-surfaces"),  # TKGeomBase utility defects
    ("Pf", "12.10", "12-10-perf"),
    ("Ad", "12.11", "12-11-adversarial"),
    ("Xp", "12.12", "12-12-cross-product"),  # cross-product synthesized defects
    ("Wr", "12.13", "12-13-writer-pathology"),  # writer pathology
    ("Tb", "12.4", "12-4-tolerance"),  # time-bombs (mostly tolerance)
    ("Ps", "12.3a", "12-3a-shells"),  # pathological-success
    ("Bo", "12.3a", "12-3a-shells"),  # BRepCheck/Builder shell defects
    ("Sw", "12.3a", "12-3a-shells"),  # BRepBuilderAPI_Sewing
    ("Hea", "12.3c", "12-3c-faces"),  # shape-healing umbrella
    ("Fi", "12.8", "12-8-mixed"),  # BRepFilletAPI
    ("Os", "12.8", "12-8-mixed"),  # BRepOffsetAPI
    ("In", "12.1c", "12-1c-syntax"),  # Interface/Transfer
    ("N", "12.4", "12-4-tolerance"),
    ("U", "12.5", "12-5-units"),
    ("A", "12.6", "12-6-assembly"),
    ("P", "12.6", "12-6-assembly"),  # P001..P028: FreeCAD-origin findings
    ("M", "12.8", "12-8-mixed"),
    ("Me", "12.14", "12-14-mesh"),  # mesh-defect fixtures (parallel corpus, not Part-21)
    ("Ip", "12.15", "12-15-import-formats"),  # import-format parser-robustness (raw malformed mesh/format files, not Part-21)
]


def resolve_prefix(entry_id: str) -> tuple[str, str]:
    """Return ``(section, section_dir)`` for an entry id.

    Matches the longest prefix whose remainder is purely numeric. ``PREFIX_MAP``
    is ordered so that more-specific prefixes (e.g. ``Pf``, ``Pmi``) are tried
    before less-specific ones (``P``).
    """
    for prefix, section, section_dir in PREFIX_MAP:
        if entry_id.startswith(prefix):
            tail = entry_id[len(prefix):]
            if tail and tail.isdigit():
                return section, section_dir
    raise ValueError(f"Unknown ID prefix for entry {entry_id!r}")


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

ENTRY_HEADING_RE = re.compile(r"^### ([A-Za-z]+\d+)\s+—\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^- \*\*([^*]+)\*\*:\s*(.*)$")
ID_REF_RE = re.compile(r"\b([A-Z][a-z]{0,2}\d{1,3})\b")


def split_entries(md_text: str) -> list[list[str]]:
    """Split the markdown into per-entry line blocks.

    Each block starts at a ``### {ID} — title`` line and runs to (but not
    including) the next ``### `` line. Skips the example placeholder
    ``### {ID} — Short title`` and category-summary headings ``### §...``.
    """
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in md_text.splitlines():
        # Any heading at h1/h2 or h3 closes the current entry. So does a
        # horizontal-rule line ("---"), which separates entries from
        # section trailers ("End of file.", "Total: N entries.", etc.).
        is_h3 = line.startswith("### ")
        closes = (
            is_h3
            or line.startswith("## ")
            or line.startswith("# ")
            or line.strip() == "---"
        )
        if closes and current is not None:
            blocks.append(current)
            current = None
        if is_h3:
            # Skip non-entry headings (placeholder, category-summary,
            # and section index headings like "### A-prefix entries").
            if not ENTRY_HEADING_RE.match(line):
                continue
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        blocks.append(current)
    return blocks


def parse_fields(block: list[str]) -> tuple[str, str, dict[str, str]]:
    """Parse one entry block into (id, title, {field_name: field_value})."""
    head_match = ENTRY_HEADING_RE.match(block[0])
    if not head_match:
        raise ValueError(f"Cannot parse heading: {block[0]!r}")
    entry_id = head_match.group(1)
    title = head_match.group(2).strip()

    fields: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_key is None:
            return
        # Trim trailing blanks; collapse runs of whitespace within a single
        # logical field while preserving inline markdown.
        text = "\n".join(current_lines).rstrip()
        fields[current_key] = text

    for raw in block[1:]:
        if not raw.strip():
            # Blank line: keep but don't open a new field.
            if current_key is not None:
                current_lines.append("")
            continue
        m = FIELD_RE.match(raw)
        if m:
            flush()
            current_key = m.group(1).strip()
            current_lines = [m.group(2).rstrip()]
        else:
            # Continuation line (indented bullet, wrapped prose, etc.).
            if current_key is not None:
                current_lines.append(raw.rstrip())
            # Lines outside any field (e.g., the **[MERGED into …]** marker)
            # are recorded under a synthetic key so we can detect them.
            elif raw.startswith("**[MERGED into"):
                fields["_merged_marker"] = raw.strip()

    flush()
    return entry_id, title, fields


def is_merged(fields: dict[str, str]) -> bool:
    if "_merged_marker" in fields:
        return True
    status = fields.get("Status", "")
    return status.startswith("merged")


# ---------------------------------------------------------------------------
# Field extraction helpers
# ---------------------------------------------------------------------------

def _normalize_inline(text: str) -> str:
    """Collapse soft-wrapped continuation lines to single-spaced text.

    For prose fields like Description / Reproducer recipe / Notes, any
    continuation lines that come from markdown soft-wraps (2-space indent
    or no indent) are joined with a single space. Sub-bullets (`  -`) are
    preserved with newlines.
    """
    lines = text.splitlines()
    if not lines:
        return ""
    out: list[str] = []
    buf: list[str] = []

    def flush_buf() -> None:
        if buf:
            out.append(" ".join(s.strip() for s in buf if s.strip()))
            buf.clear()

    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            flush_buf()
            continue
        if stripped.startswith("- ") or ln.startswith("  -"):
            flush_buf()
            out.append(stripped)
        else:
            buf.append(stripped)
    flush_buf()
    return "\n".join(out).strip()


def _strip_backticks(text: str) -> str:
    """Return *text* with surrounding/embedded markdown backticks removed.

    The Expected-validation line is consistently wrapped in single backticks,
    e.g. ``` `occt=reject/reject gmsh=reject ifc=reject` ```. We strip them to
    get a stable plain-text token for downstream tooling.
    """
    return text.replace("`", "").strip()


# Pattern for the canonical Expected-validation spec triple.
_RE_EXPECTED_VALIDATION = re.compile(
    r"occt=\S+(?:/\S+)?\s+gmsh=\S+\s+ifc=\S+"
)


def _clean_expected_validation(text: str) -> str:
    """Extract the canonical ``occt=… gmsh=… ifc=…`` spec from raw text.

    A handful of catalog entries have continuation prose belonging to the
    preceding ``Expected kernel behavior`` accidentally attached after the
    validation line (the markdown soft-wrapped one bullet's text under the
    next bullet). Pull out the validation triple and discard the trailing
    chatter.
    """
    flat = _strip_backticks(text)
    flat = " ".join(flat.split())  # collapse whitespace
    if not flat:
        return ""
    m = _RE_EXPECTED_VALIDATION.search(flat)
    if m:
        return m.group(0)
    return flat


def _split_sources(text: str) -> list[str]:
    text = _normalize_inline(text)
    if not text:
        return []
    # Sources are usually semicolon-delimited.
    parts = [p.strip() for p in text.split(";")]
    return [p for p in parts if p]


_RE_SEE_ALSO = re.compile(
    r"\*\*See also\*\*\s*:\s*([^.]*?)(?:\.|$)"
)


def _extract_id_list(notes_text: str, pattern: re.Pattern[str]) -> list[str]:
    m = pattern.search(notes_text)
    if not m:
        return []
    chunk = m.group(1)
    ids = ID_REF_RE.findall(chunk)
    # Deduplicate while preserving order.
    seen: set[str] = set()
    result: list[str] = []
    for token in ids:
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result


# ---------------------------------------------------------------------------
# Build a single entry dict
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = (
    "id",
    "title",
    "section",
    "section_dir",
    "category",
    "sources",
    "sender",
    "description",
    "reproducer",
    "expected_kernel_behavior",
    "notes",
    "expected_validation",
    "fixture_path",
    "see_also",
    # Structured fields promoted from notes / catalog markdown so downstream
    # tooling can grade kernel behavior without parsing prose.
    "provenance_tier",
    "tier3_assertions",
    "byte_assertions",
    "cross_oracle_note",
    "occ_behavior_note",
    # P0/P1/P2/P3 severity ranking (None for entries without OCC behavior).
    "severity",
    # Cross-cutting defect-class taxonomy
    "taxonomy",
)


# Canonical provenance-tier vocabulary. Documents what kind of evidence
# backs the entry's claim.
PROVENANCE_TIERS = (
    "bytes-sufficient",       # default: bytes alone embody the defect
    "bytes-only",             # defect only visible in bytes; oracles cannot verify
    "runtime-only",           # defect is kernel runtime behavior, not in any file
    "requires-sibling-pair",  # defect requires both <id>.input.stp and <id>.stp
    "cross-file-state",       # defect lives across multiple files / process state
    "writer-side",            # defect is on the writer; bytes show post-writer state
    "misfiled",               # entry is in the wrong section (kept for ID stability)
)


# Patterns extracted from the freeform Notes field.
_RE_PROVENANCE_TIER = re.compile(
    r"Provenance[_ ]tier:\s*([a-z][a-z\-]*)", re.IGNORECASE,
)
_RE_CROSS_ORACLE = re.compile(
    r"(?:Cross[- ]oracle|Cross oracle):\s*(.+?)(?=\s*(?:\*\*|\Z|\n\s*-\s*\*\*))",
    re.IGNORECASE | re.DOTALL,
)
_RE_OCC_BEHAVIOR = re.compile(
    r"(?:OCC behavior|Validation observed|BRepCheck does not):\s*(.+?)(?=\s*(?:\*\*|\Z|\n\s*-\s*\*\*))",
    re.IGNORECASE | re.DOTALL,
)
_RE_TIER3_ASSERTION = re.compile(
    r"^- \*\*Tier-3 assertion\*\*:\s*(.+?)\s*$", re.MULTILINE,
)
_RE_BYTE_ASSERTION = re.compile(
    r"^- \*\*Byte assertion\*\*:\s*(.+?)\s*$", re.MULTILINE,
)
# Structural-oracle assertion, e.g. `struct == UNITS_INCONSISTENT`. Verified by
# the non-kernel structural linter (_structural_oracle) independent of any
# geometry kernel — used by structural-defect fixtures whose defect is invisible
# to occt/gmsh shape-counts.
_RE_STRUCTURAL_ASSERTION = re.compile(
    r"^- \*\*Structural assertion\*\*:\s*(.+?)\s*$", re.MULTILINE,
)
# P0/P1/P2/P3 severity line lives directly under `**OCC behavior**:`.
_RE_SEVERITY = re.compile(
    r"^- \*\*Severity\*\*:\s*(P[0-3])\s*$", re.MULTILINE,
)
# Closure intent for fixtures whose STEP bytes contain OPEN_SHELL or
# SHELL_BASED_SURFACE_MODEL: "sheet" (intentional sheet body), "solid"
# (accidentally-unclosed solid; heal target), or "ambiguous". When solid,
# an optional Closure defect line records the defect kind.
_RE_CLOSURE_INTENT = re.compile(
    r"^- \*\*Closure intent\*\*:\s*(sheet|solid|ambiguous)\s*$", re.MULTILINE,
)
_RE_CLOSURE_DEFECT = re.compile(
    r"^- \*\*Closure defect\*\*:\s*(gap|missing_face|unstitched_seam)\s*$", re.MULTILINE,
)
# Fixture-kind: how a consumer should route the expectation.
_RE_FIXTURE_KIND = re.compile(
    r"^- \*\*Fixture kind\*\*:\s*(malformed-file|conformance-probe|receiver-behavior|producer-receiver-pair|kernel-test-pair)\s*$",
    re.MULTILINE,
)
# Pair-with: sibling fixture id for producer/receiver paired defects.
_RE_PAIR_WITH = re.compile(
    r"^- \*\*Pair with\*\*:\s*([A-Za-z]+\d+(?:\.input)?)\s*$", re.MULTILINE,
)

CLOSURE_INTENTS = ("sheet", "solid", "ambiguous")
CLOSURE_DEFECTS = ("gap", "missing_face", "unstitched_seam")
FIXTURE_KINDS = ("malformed-file", "conformance-probe", "receiver-behavior", "producer-receiver-pair")


def _extract_provenance_tier(notes: str) -> str:
    """Extract provenance tier from notes; default to 'bytes-sufficient'."""
    m = _RE_PROVENANCE_TIER.search(notes)
    if m:
        tier = m.group(1).strip().lower()
        if tier in PROVENANCE_TIERS:
            return tier
    return "bytes-sufficient"


def _extract_inline_note(notes: str, pattern: re.Pattern[str]) -> str | None:
    m = pattern.search(notes)
    if not m:
        return None
    text = m.group(1).strip()
    # Truncate long, multi-line notes to one trimmed line: easier to consume
    # downstream and keeps the JSON clean.
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    return text


def _extract_assertions(block_text: str, pattern: re.Pattern[str]) -> list[str]:
    """Extract assertion expressions (one per line) from a raw entry block."""
    return [m.group(1).strip() for m in pattern.finditer(block_text)]


def build_entry(entry_id: str, title: str, fields: dict[str, str], block_text: str = "") -> dict:
    section, section_dir = resolve_prefix(entry_id)
    sources_raw = fields.get("Sources") or fields.get("Source(s)") or fields.get("Source") or ""
    notes_raw = _normalize_inline(fields.get("Notes", ""))

    # Honor an explicit "Fixture path" field when present (e.g. §12.14 mesh
    # fixtures use mesh-examples/.../<id>.mesh.json). Default to the
    # STEP location otherwise.
    explicit_path = _normalize_inline(fields.get("Fixture path", ""))
    if explicit_path:
        fixture_relative = explicit_path
    else:
        fixture_relative = f"step-examples/{section_dir}/{entry_id}.stp"

    # Structured fields extracted from notes prose / assertion lines
    provenance_tier = _extract_provenance_tier(notes_raw)
    cross_oracle_note = _extract_inline_note(notes_raw, _RE_CROSS_ORACLE)
    occ_behavior_note = _extract_inline_note(notes_raw, _RE_OCC_BEHAVIOR)
    tier3_assertions = _extract_assertions(block_text, _RE_TIER3_ASSERTION)
    byte_assertions = _extract_assertions(block_text, _RE_BYTE_ASSERTION)
    structural_assertions = _extract_assertions(block_text, _RE_STRUCTURAL_ASSERTION)
    severity_match = _RE_SEVERITY.search(block_text)
    severity = severity_match.group(1) if severity_match else None
    closure_match = _RE_CLOSURE_INTENT.search(block_text)
    closure_intent = closure_match.group(1) if closure_match else None
    closure_defect_match = _RE_CLOSURE_DEFECT.search(block_text)
    closure_defect = closure_defect_match.group(1) if closure_defect_match else None
    fixture_kind_match = _RE_FIXTURE_KIND.search(block_text)
    fixture_kind = fixture_kind_match.group(1) if fixture_kind_match else None
    pair_with_match = _RE_PAIR_WITH.search(block_text)
    pair_with = pair_with_match.group(1) if pair_with_match else None

    # Alternative-field fallbacks: many wave-53+ entries use a different
    # vocabulary ("Defect", "Geometry", "Healer impact", "File") instead of
    # the canonical ("Description", "Expected kernel behavior",
    # "Fixture path"). Accept both forms; canonical takes precedence.
    def _field_with_fallback(*keys: str) -> str:
        for k in keys:
            v = fields.get(k, "")
            if v:
                return _normalize_inline(v)
        return ""

    # Compose description from Description, else Defect (or Defect + Geometry
    # joined). The composed form preserves enough text for downstream
    # tooling that wants a single 'what is the defect' string.
    description = fields.get("Description", "")
    if not description:
        defect = fields.get("Defect", "")
        geometry = fields.get("Geometry", "")
        if defect and geometry:
            description = f"{defect} Geometry: {geometry}"
        elif defect:
            description = defect
        elif geometry:
            description = geometry
    description_norm = _normalize_inline(description)

    record = {
        "id": entry_id,
        "title": title,
        "section": section,
        "section_dir": section_dir,
        # Category falls back to section directory name; better than empty.
        "category": _field_with_fallback("Category") or f"§{section}",
        # Sources falls back to a placeholder for alt-format entries that
        # don't cite a source line. The placeholder marks the entry as
        # synthesized rather than evidence-cited; the catalog claim still
        # stands but the auditor knows there's no externally-cited source.
        "sources": _split_sources(sources_raw) or ["synthesized — no external source cited"],
        "sender": _normalize_inline(fields.get("Sender", "")),
        "description": description_norm or title,  # never empty: title is a fallback summary
        "reproducer": _normalize_inline(fields.get("Reproducer recipe", "")),
        "expected_kernel_behavior": _field_with_fallback(
            "Expected kernel behavior", "Healer impact", "Expected behavior"
        ) or "heal or reject (mechanism-specific; see Description)",
        "notes": notes_raw,
        "expected_validation": _clean_expected_validation(
            fields.get("Expected validation", "")
        ),
        "fixture_path": fixture_relative,
        "see_also": _extract_id_list(notes_raw, _RE_SEE_ALSO),
        # Structured fields promoted from prose
        "provenance_tier": provenance_tier,
        "tier3_assertions": tier3_assertions,
        "byte_assertions": byte_assertions,
        "structural_assertions": structural_assertions,
        "cross_oracle_note": cross_oracle_note,
        "occ_behavior_note": occ_behavior_note,
        "severity": severity,
        "closure_intent": closure_intent,
        "closure_defect": closure_defect,
        "fixture_kind": fixture_kind,
        "pair_with": pair_with,
    }
    # Cross-cutting taxonomy tags. Derived deterministically from the
    # other fields above; the markdown stays human-readable and the JSON
    # gets a computer-readable orthogonal browse axis.
    record["taxonomy"] = _taxonomy.derive(record)
    return record


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------

def build_catalog(md_path: Path = CATALOG_MD) -> list[dict]:
    text = md_path.read_text(encoding="utf-8")
    entries: list[dict] = []
    for block in split_entries(text):
        entry_id, title, fields = parse_fields(block)
        if is_merged(fields):
            continue
        # Pass the raw block text so build_entry can extract Tier-3 /
        # Byte assertion lines that aren't part of `**Field**:` form.
        block_text = "\n".join(block)
        entries.append(build_entry(entry_id, title, fields, block_text))
    # Sort deterministically: by section, then by ID. Within an ID, numeric
    # suffixes are compared as integers so Le2 sorts before Le10.
    def sort_key(entry: dict) -> tuple:
        eid = entry["id"]
        m = re.match(r"^([A-Za-z]+)(\d+)$", eid)
        if m:
            return (entry["section"], m.group(1), int(m.group(2)))
        return (entry["section"], eid, 0)

    entries.sort(key=sort_key)
    return entries


def write_catalog(entries: list[dict], out_path: Path = CATALOG_JSON) -> None:
    payload = json.dumps(entries, indent=2, sort_keys=True, ensure_ascii=False)
    out_path.write_text(payload + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    md_path = CATALOG_MD
    json_path = CATALOG_JSON
    if argv:
        md_path = Path(argv[0])
    if len(argv) > 1:
        json_path = Path(argv[1])
    entries = build_catalog(md_path)
    write_catalog(entries, json_path)
    print(f"Wrote {len(entries)} canonical entries to {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
