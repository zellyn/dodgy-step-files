"""Static-site generator for the STEP-defect catalog.

Produces per-fixture HTML pages alongside the existing markdown catalog so
the repository can be served via GitHub Pages without duplicating content.

Output layout (paths relative to the research root)::

    index.html                                 # landing page
    browse/index.html                          # top-level catalog browser
    browse/assets/style.css                    # shared stylesheet
    browse/<section_dir>/index.html            # section overview
    browse/<section_dir>/<id>.html             # per-fixture page

Per-fixture pages link back to the actual ``.stp`` fixture via a relative
path, e.g. ``../../step-examples/12-1a-encoding/Le001.stp``.

Usage::

    cd validation
    uv run python -m step_corpus._render_pages              # render all pages
    uv run python -m step_corpus._render_pages --clean      # clean browse/ first

The module has no third-party dependencies; it uses only ``html``,
``pathlib``, ``argparse``, and friends from the standard library.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from step_corpus import _byte_locations, _taxonomy, catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT

V2_OUT = Path("/tmp/cad-v2-out")

# Friendly labels for each section_dir. Used by the browser/landing pages.
SECTION_LABELS: dict[str, str] = {
    "12-1a-encoding": "§12.1a Encoding & string-literal defects",
    "12-1b-header": "§12.1b Header & instance-numbering",
    "12-1c-syntax": "§12.1c Part-21 grammar",
    "12-2a-pcurves": "§12.2a Pcurve defects",
    "12-2b-nurbs": "§12.2b NURBS / B-spline",
    "12-2c-surfaces": "§12.2c Surface / curve degeneracies",
    "12-3a-shells": "§12.3a Shells / orientation",
    "12-3b-wires": "§12.3b Wires / loops / edges",
    "12-3c-faces": "§12.3c Faces / sewing / free bound",
    "12-4-tolerance": "§12.4 Tolerance & numerical precision",
    "12-5-units": "§12.5 Units & coordinate systems",
    "12-6-assembly": "§12.6 Assembly hierarchy",
    "12-7-pmi": "§12.7 PMI / GD&T",
    "12-8-mixed": "§12.8 Mixed (tessellation, validation properties, etc.)",
    "12-10-perf": "§12.10 Scale & performance",
    "12-11-adversarial": "§12.11 Adversarial / parser robustness",
    "12-12-cross-product": "§12.12 Cross-product",
    "12-13-writer-pathology": "§12.13 Writer pathology",
}

# A human-friendly one-paragraph blurb per section. Falls back to a generic
# "see catalog markdown" sentence when no blurb is available.
SECTION_BLURBS: dict[str, str] = {
    "12-1a-encoding": (
        "Encoding pathologies in STEP files: BOMs, lone CR / NUL bytes, "
        "high-bit characters, half-escaped strings, and other lexical hazards "
        "that production parsers grow tolerance for over time."
    ),
    "12-1b-header": (
        "HEADER section, instance numbering, ANCHOR / REFERENCE / SIGNATURE "
        "and Edition-3 multi-section file pathologies."
    ),
    "12-1c-syntax": "Part-21 grammar pathologies: malformed tokens, "
                    "structural defects in DATA section, illegal references.",
    "12-2a-pcurves": "Pcurve / parametric-curve defects: near-period mismatches, "
                    "out-of-bounds parameters, degenerate or seam pcurves.",
    "12-2b-nurbs": "NURBS / B-spline knot-vector pathologies: clamped/unclamped, "
                  "degenerate weights, non-monotonic knots, degree mismatches.",
    "12-2c-surfaces": "Surface and curve degeneracies, AP242 surface subtypes, "
                     "geometric-base utilities (Gb).",
    "12-3a-shells": "Shell topology defects: orientation, free bounds, mixed "
                   "open/closed shells, UnifySameDomain pathologies.",
    "12-3b-wires": "Wire / loop / edge pathologies: self-intersecting wires, "
                  "half-edge orphans, misordered loops.",
    "12-3c-faces": "Face / sewing / free-bound pathologies, including "
                  "non-manifold sewing seams and degenerate trimming loops.",
    "12-4-tolerance": "Tolerance and numerical-precision defects: vertex "
                     "tolerances exceeding edge length, near-coincident loops.",
    "12-5-units": "Units and coordinate-systems defects: missing context, "
                 "mismatched length/angle units, frame-of-reference drift.",
    "12-6-assembly": "Assembly hierarchy: NAUO chains, instance graphs, "
                    "FreeCAD-origin P entries.",
    "12-7-pmi": "PMI / GD&T defects: dimensional tolerances, datums, "
               "geometric tolerance frames, semantic surface association.",
    "12-8-mixed": "Mixed / auxiliary defects: tessellation, validation "
                 "properties, schema-version edge cases, AP238 deep-feature.",
    "12-10-perf": "Scale and performance pathologies: large files, dependency "
                 "depth, quadratic resolution paths, multi-pass healing.",
    "12-11-adversarial": "Adversarial / parser-robustness fixtures: malicious "
                        "or boundary-case inputs intended to expose memory or "
                        "performance defects.",
    "12-12-cross-product": "Cross-product defects: vendor-specific writer "
                          "interactions and translator-pipeline pathologies.",
    "12-13-writer-pathology": "Writer-pathology defects: kernel STEP-writer "
                             "round-trip failures, malformed output, and "
                             "schema-non-conformance on emit.",
}


# A handful of curated case-A bug witnesses for the landing page. Pulled
# from CHANGELOG / dashboard summary text. Each is (id, blurb).
FEATURED_FINDINGS: list[tuple[str, str]] = [
    ("Le001", "OCC + ifcopenshell reject UTF-8 BOM in STEP header — "
              "fixture demonstrates a real interoperability gap."),
    ("Pf001", "Multi-GB Creo AP242 assemblies trigger unbounded receiver "
              "memory in OCCT-based downstream consumers."),
    ("Pf006", "Quadratic self-intersection check dominates STEP read on "
              "perforated sheets — ~90% of read time wasted on a check that "
              "almost never finds defects."),
    ("Tsh001", "Inverted shell-orientation propagates through OCCT sewing — "
               "fixture exposes a class of silent topology corruption."),
    ("Gn001", "Near-period NURBS pcurve produces silent empty geometry in "
              "OCCT but a clean reject in gmsh."),
]


# ---------------------------------------------------------------------------
# Path / link helpers
# ---------------------------------------------------------------------------

def _research_root() -> Path:
    return RESEARCH_ROOT


def _fixture_id_index(entries: list[dict]) -> dict[str, str]:
    """Map id -> section_dir for cross-section see-also resolution."""
    return {e["id"]: e["section_dir"] for e in entries}


def _entries_by_section(entries: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        out[e["section_dir"]].append(e)
    for sec in out:
        out[sec].sort(key=lambda x: x["id"])
    return out


def _section_label(section_dir: str) -> str:
    return SECTION_LABELS.get(section_dir, section_dir)


def _section_blurb(section_dir: str) -> str:
    return SECTION_BLURBS.get(section_dir,
                              f"Catalog entries in {section_dir}.")


# ---------------------------------------------------------------------------
# Cross-reference parsing
# ---------------------------------------------------------------------------

# Pattern matching catalog ids: letter prefix + digits.
# Matches: Le001, Tsh017, Pmi049, Ad027, Gn003, P001, etc.
_ID_PATTERN = re.compile(r"\b([A-Z][a-z]{0,3}\d{1,4})\b")


def _ids_from_notes(notes: str, valid_ids: set[str]) -> list[str]:
    """Extract catalog ids from a Notes string (e.g. 'See also: Foo123, Bar456')."""
    if not notes:
        return []
    found: list[str] = []
    seen: set[str] = set()
    for m in _ID_PATTERN.finditer(notes):
        token = m.group(1)
        if token in valid_ids and token not in seen:
            seen.add(token)
            found.append(token)
    return found


# ---------------------------------------------------------------------------
# Validate2 oracle data
# ---------------------------------------------------------------------------

def _read_oracle(entry: dict) -> dict[str, Any] | None:
    p = V2_OUT / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _h(text: str | None) -> str:
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


def _shared_head(title: str, css_href: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"  <title>{_h(title)}</title>\n"
        f"  <link rel=\"stylesheet\" href=\"{_h(css_href)}\">\n"
        "</head>\n"
    )


def _footer(extra: str = "") -> str:
    parts = ["<footer>"]
    if extra:
        parts.append(extra)
    parts.append('<p class="meta">STEP Defect Catalog — auto-generated; '
                 'edit <code>STEP_PROBLEM_CATALOG.md</code> instead.</p>')
    parts.append("</footer>\n</body>\n</html>\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Per-fixture page rendering
# ---------------------------------------------------------------------------

def _render_oracle_table(summary: dict | None) -> str:
    if not summary:
        return ('<p class="muted">No live oracle data — '
                "run <code>_run_corpus</code> to populate.</p>")
    rows = ['<table class="oracle"><thead><tr>'
            "<th>Oracle</th><th>Verdict</th></tr></thead><tbody>"]
    for k in ("occt_heal_on", "occt_heal_off", "gmsh_autofix_on",
              "gmsh_autofix_off", "ifcopenshell", "part21_strict", "manifold"):
        v = summary.get(k, "?")
        rows.append(f"<tr><td><code>{_h(k)}</code></td>"
                    f"<td><code>{_h(v)}</code></td></tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)


def _render_xref_links(ids: list[str], from_section: str,
                       id_index: dict[str, str]) -> str:
    """Render a list of catalog ids as relative HTML links."""
    pieces = []
    for tid in ids:
        target_section = id_index.get(tid)
        if target_section is None:
            pieces.append(f"<code>{_h(tid)}</code>")
            continue
        if target_section == from_section:
            href = f"{tid}.html"
        else:
            href = f"../{target_section}/{tid}.html"
        pieces.append(f'<a href="{_h(href)}">{_h(tid)}</a>')
    return ", ".join(pieces)


def _prev_next(section_entries: list[dict], idx: int) -> tuple[dict | None, dict | None]:
    prev = section_entries[idx - 1] if idx > 0 else None
    nxt = section_entries[idx + 1] if idx + 1 < len(section_entries) else None
    return prev, nxt


# ---------------------------------------------------------------------------
# Fixture-bytes rendering with inline highlighting
# ---------------------------------------------------------------------------

# Render budget: keep page weight bounded for very large fixtures.
_FIXTURE_LARGE_BYTES = 50 * 1024
_FIXTURE_HEADER_LINES = 5         # always show the first N lines
_FIXTURE_CONTEXT_LINES = 10       # ±N lines of context around each match
_FIXTURE_MAX_LINES = 200          # hard cap


def _byte_offset_to_line_index(line_starts: list[int], offset: int) -> int:
    """Binary search: largest i such that line_starts[i] <= offset."""
    lo, hi = 0, len(line_starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if line_starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo


def _select_visible_line_indices(
    total_lines: int,
    match_line_indices: list[int],
    *,
    header: int = _FIXTURE_HEADER_LINES,
    context: int = _FIXTURE_CONTEXT_LINES,
    cap: int = _FIXTURE_MAX_LINES,
) -> list[int | None]:
    """Compute the subset of line indices to render for a large fixture.

    Returns a list whose entries are either an integer line index (0-based) or
    ``None`` representing a truncation marker. The caller renders ``None`` as
    a ``…`` separator.
    """
    keep: set[int] = set(range(min(header, total_lines)))
    for li in match_line_indices:
        lo = max(0, li - context)
        hi = min(total_lines, li + context + 1)
        keep.update(range(lo, hi))

    if len(keep) > cap:
        # Keep as many high-priority lines as possible. Prioritise header,
        # then nearest-to-match. Simpler: cap on total lines kept by
        # truncating the sorted list at the cap.
        sorted_keep = sorted(keep)
        keep = set(sorted_keep[:cap])

    sorted_keep = sorted(keep)
    out: list[int | None] = []
    prev: int | None = None
    for li in sorted_keep:
        if prev is not None and li != prev + 1:
            out.append(None)
        out.append(li)
        prev = li
    return out


def _render_fixture_bytes_html(body: bytes,
                               assertions: list[str]) -> str:
    """Render fixture ``body`` as escaped HTML with ``<mark>`` tags around
    every byte range matched by an assertion. Adds line numbers and respects
    the truncation budget for very large fixtures.
    """
    if not body:
        return '<span class="truncation">(empty fixture)</span>'

    ranges = _byte_locations.find_all_match_locations(body, assertions)

    # Decode latin-1 -> 1:1 byte/char mapping so byte offsets == char offsets.
    text = body.decode("latin-1")

    # Compute line starts (byte offsets) by scanning for '\n'.
    line_starts: list[int] = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)
    # Number of lines = number of non-empty splits; trailing newline doesn't
    # produce an extra line of content.
    total_lines = len(line_starts)
    if line_starts[-1] >= len(text):
        # Trailing '\n' added a phantom start past EOF; drop it.
        line_starts.pop()
        total_lines = len(line_starts)

    line_ends: list[int] = []
    for i, start in enumerate(line_starts):
        if i + 1 < len(line_starts):
            # End just before the next line's start (i.e., at the '\n').
            line_ends.append(line_starts[i + 1] - 1)
        else:
            # Last line: ends at end-of-text (or just before trailing '\n').
            end = len(text)
            if end > start and text[end - 1] == "\n":
                end -= 1
            line_ends.append(end)

    # Map each match to its starting line index.
    match_line_indices = sorted({
        _byte_offset_to_line_index(line_starts, s)
        for s, _ in ranges
    })

    truncate = len(body) > _FIXTURE_LARGE_BYTES
    if truncate:
        visible = _select_visible_line_indices(total_lines, match_line_indices)
    else:
        visible = list(range(total_lines))

    # Build a per-line list of (start, end) match ranges that fall within it.
    # Ranges may span multiple lines; clip them to each line.
    ranges_by_line: dict[int, list[tuple[int, int]]] = {}
    for s, e in ranges:
        first_line = _byte_offset_to_line_index(line_starts, s)
        last_line = _byte_offset_to_line_index(line_starts, max(s, e - 1))
        for li in range(first_line, last_line + 1):
            ls = line_starts[li]
            le = line_ends[li]
            clip_s = max(s, ls)
            clip_e = min(e, le)
            if clip_e > clip_s:
                ranges_by_line.setdefault(li, []).append((clip_s, clip_e))

    out_pieces: list[str] = []
    line_no_width = max(4, len(str(total_lines)))
    for entry in visible:
        if entry is None:
            out_pieces.append(
                f'<span class="truncation">{"…":>{line_no_width}}    '
                "(lines elided)</span>\n"
            )
            continue
        li = entry
        ls = line_starts[li]
        le = line_ends[li]
        line_text = text[ls:le]
        marks = sorted(ranges_by_line.get(li, []))

        # Build HTML for this line: escape segments, wrap matched bytes in <mark>.
        parts: list[str] = []
        cursor = ls
        for s, e in marks:
            if s > cursor:
                parts.append(html.escape(text[cursor:s]))
            parts.append(f'<mark>{html.escape(text[s:e])}</mark>')
            cursor = e
        if cursor < le:
            parts.append(html.escape(text[cursor:le]))

        lineno = f'<span class="lineno">{li + 1}</span>'
        out_pieces.append(f"{lineno}{''.join(parts)}\n")

    return "".join(out_pieces)


def _fixture_bytes_section(entry: dict) -> str:
    """Return the ``<h2>Fixture content</h2>`` block, or ``""`` if no fixture."""
    fixture_path = RESEARCH_ROOT / entry["fixture_path"]
    if not fixture_path.is_file():
        return ""
    try:
        body = fixture_path.read_bytes()
    except OSError:
        return ""

    assertions = entry.get("byte_assertions") or []
    inner = _render_fixture_bytes_html(body, assertions)

    has_marks = "<mark>" in inner
    summary_text = (
        "Show fixture bytes (with defect highlighting)"
        if has_marks else "Show fixture bytes"
    )

    parts = [
        '<section><h2>Fixture content</h2>',
        '<details>',
        f'<summary>{_h(summary_text)}</summary>',
        f'<pre class="fixture-bytes">{inner}</pre>',
        '</details>',
        '</section>',
    ]
    return "\n".join(parts)


def render_fixture_page(entry: dict, section_entries: list[dict],
                        idx: int, id_index: dict[str, str]) -> str:
    eid = entry["id"]
    section_dir = entry["section_dir"]
    title = f"{eid} — {entry['title']}"
    css_href = "../assets/style.css"

    prev, nxt = _prev_next(section_entries, idx)
    valid_ids = set(id_index.keys())
    notes_xrefs = _ids_from_notes(entry.get("notes") or "", valid_ids)
    # Drop self-reference if present.
    notes_xrefs = [x for x in notes_xrefs if x != eid]
    declared_xrefs = list(entry.get("see_also") or [])
    # Combine, preserve ordering, drop dups
    combined_xrefs: list[str] = []
    seen: set[str] = set()
    for x in declared_xrefs + notes_xrefs:
        if x in valid_ids and x != eid and x not in seen:
            seen.add(x)
            combined_xrefs.append(x)

    out: list[str] = [_shared_head(title, css_href)]
    out.append('<body class="entry">')
    out.append('<nav class="topnav">')
    out.append(f'<a href="../../index.html">Home</a> '
               f'<span class="sep">/</span> '
               f'<a href="../index.html">All sections</a> '
               f'<span class="sep">/</span> '
               f'<a href="index.html">{_h(_section_label(section_dir))}</a> '
               f'<span class="sep">/</span> '
               f'<span class="current">{_h(eid)}</span>')
    out.append("</nav>")

    out.append('<header class="title-bar">')
    out.append(f"<h1>{_h(eid)} <span class=\"sep\">—</span> "
               f"<span class=\"entry-title\">{_h(entry['title'])}</span></h1>")
    out.append(f"<p class=\"category\">{_h(entry['category'])}</p>")
    # Severity badge: P0/P1/P2/P3 priority for kernel-grading.
    severity = entry.get("severity")
    if severity:
        sev_label = {
            "P0": "P0 — receiver crash / hang / OOM",
            "P1": "P1 — silent data loss",
            "P2": "P2 — spec deviation (no data loss)",
            "P3": "P3 — cosmetic / metadata-only",
        }.get(severity, severity)
        out.append(
            f'<p class="severity-badge severity-{_h(severity.lower())}">'
            f'{_h(sev_label)}</p>'
        )
    # Taxonomy tag pills: orthogonal browse axis (defect class).
    tax = entry.get("taxonomy") or []
    if tax:
        out.append('<p class="tag-pills">')
        for t in tax:
            href = f"../by-tag/{t}/index.html"
            out.append(
                f'<a class="tag tag-{_h(t)}" href="{_h(href)}">{_h(t)}</a>'
            )
        out.append("</p>")
    out.append("</header>")

    out.append('<main>')

    # Fixture link (prominent)
    fixture_rel = f"../../{entry['fixture_path']}"
    out.append('<section class="fixture-link">')
    out.append(f'<a class="big-link" href="{_h(fixture_rel)}">'
               f'View raw fixture (.stp)</a> '
               f'<code class="path">{_h(entry["fixture_path"])}</code>')
    out.append('</section>')

    # Sources
    sources = entry.get("sources") or []
    if sources:
        out.append('<section><h2>Sources</h2><ul>')
        for s in sources:
            out.append(f'<li>{_h(s)}</li>')
        out.append('</ul></section>')

    # Sender
    if entry.get("sender"):
        out.append('<section><h2>Sender</h2>')
        out.append(f'<p>{_h(entry["sender"])}</p></section>')

    # Description
    out.append('<section><h2>Description</h2>')
    out.append(f'<p>{_h(entry["description"])}</p></section>')

    # Reproducer recipe
    out.append('<section><h2>Reproducer recipe</h2>')
    out.append(f'<p>{_h(entry["reproducer"])}</p></section>')

    # Expected kernel behavior
    out.append('<section><h2>Expected kernel behavior</h2>')
    out.append(f'<p>{_h(entry["expected_kernel_behavior"])}</p></section>')

    # Notes
    if entry.get("notes"):
        out.append('<section><h2>Notes</h2>')
        out.append(f'<p>{_h(entry["notes"])}</p></section>')

    out.append('<section><h2>Expected validation</h2>')
    out.append(f'<p><code>{_h(entry["expected_validation"])}</code></p>'
               '</section>')

    # Provenance tier (if not bytes-sufficient)
    pt = entry.get("provenance_tier")
    if pt and pt != "bytes-sufficient":
        out.append('<section><h2>Provenance tier</h2>')
        out.append(f'<p><code>{_h(pt)}</code> — '
                   f'defect not fully embodied in fixture bytes.</p></section>')

    # Byte assertions
    byte_asserts = entry.get("byte_assertions") or []
    if byte_asserts:
        out.append('<section><h2>Byte assertions</h2><ul class="assertions">')
        for a in byte_asserts:
            out.append(f'<li><code>{_h(a)}</code></li>')
        out.append('</ul></section>')

    # Tier-3 assertions
    tier3 = entry.get("tier3_assertions") or []
    if tier3:
        out.append('<section><h2>Tier-3 assertions</h2><ul class="assertions">')
        for a in tier3:
            out.append(f'<li><code>{_h(a)}</code></li>')
        out.append('</ul></section>')

    # Cross-references
    if combined_xrefs:
        out.append('<section><h2>Cross-references</h2>')
        out.append(f'<p>{_render_xref_links(combined_xrefs, section_dir, id_index)}</p>')
        out.append('</section>')

    # Live oracle
    oracle = _read_oracle(entry)
    summary = (oracle or {}).get("summary") or {}
    out.append('<section><h2>Live oracle output</h2>')
    out.append(_render_oracle_table(summary))
    out.append('</section>')

    # Fixture content with inline byte-level highlighting
    fixture_block = _fixture_bytes_section(entry)
    if fixture_block:
        out.append(fixture_block)

    out.append("</main>")

    # Footer with prev/next
    nav_bits = []
    if prev:
        nav_bits.append(f'<a class="prev" href="{_h(prev["id"])}.html">'
                        f'&larr; {_h(prev["id"])}</a>')
    nav_bits.append(f'<a class="up" href="index.html">'
                    f'{_h(_section_label(section_dir))}</a>')
    if nxt:
        nav_bits.append(f'<a class="next" href="{_h(nxt["id"])}.html">'
                        f'{_h(nxt["id"])} &rarr;</a>')
    extra = '<nav class="prevnext">' + " ".join(nav_bits) + "</nav>"
    out.append(_footer(extra))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Section overview rendering
# ---------------------------------------------------------------------------

def render_section_index(section_dir: str, entries: list[dict]) -> str:
    title = _section_label(section_dir)
    css_href = "../assets/style.css"
    out: list[str] = [_shared_head(title, css_href)]
    out.append('<body class="section">')
    out.append('<nav class="topnav">')
    out.append('<a href="../../index.html">Home</a> '
               f'<span class="sep">/</span> '
               '<a href="../index.html">All sections</a> '
               f'<span class="sep">/</span> '
               f'<span class="current">{_h(title)}</span>')
    out.append('</nav>')
    out.append('<header class="title-bar">')
    out.append(f'<h1>{_h(title)}</h1>')
    out.append(f'<p class="blurb">{_h(_section_blurb(section_dir))}</p>')
    out.append(f'<p class="meta">{len(entries)} entries</p>')
    out.append('</header>')

    out.append('<main>')
    out.append('<table class="entries"><thead><tr>'
               '<th>ID</th><th>Title</th>'
               '<th>Provenance</th><th>Expected validation</th>'
               '</tr></thead><tbody>')
    for e in entries:
        href = f'{e["id"]}.html'
        pt = e.get("provenance_tier") or ""
        out.append(
            f'<tr><td><a href="{_h(href)}"><code>{_h(e["id"])}</code></a></td>'
            f'<td>{_h(e["title"])}</td>'
            f'<td><code>{_h(pt)}</code></td>'
            f'<td><code>{_h(e["expected_validation"])}</code></td></tr>'
        )
    out.append('</tbody></table>')
    out.append('</main>')
    out.append(_footer())
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Top-level browser
# ---------------------------------------------------------------------------

def render_browse_index(by_section: dict[str, list[dict]]) -> str:
    title = "STEP Defect Catalog — Browse"
    css_href = "assets/style.css"
    out: list[str] = [_shared_head(title, css_href)]
    out.append('<body class="browse">')
    out.append('<nav class="topnav">')
    out.append('<a href="../index.html">Home</a> '
               '<span class="sep">/</span> '
               '<span class="current">Browse</span>')
    out.append('</nav>')
    out.append('<header class="title-bar"><h1>Browse the STEP Defect Catalog</h1>')
    total = sum(len(v) for v in by_section.values())
    out.append(f'<p class="meta">{total} entries across {len(by_section)} sections</p>')
    out.append('</header>')

    # Cross-cutting browse axis (orthogonal to the §12.x sections).
    out.append('<main>')
    out.append('<section class="by-tag-cta">')
    out.append('<h2>Browse by defect class</h2>')
    out.append('<p>Every entry also carries 1–3 cross-cutting tags '
               '(crash, silent-loss, spec-violation, …) describing the '
               '<em>kind</em> of defect, independent of where it lives '
               'in the catalog.</p>')
    out.append('<p><a class="big-link" href="by-tag/index.html">'
               'Browse all 15 defect classes &rarr;</a></p>')
    out.append('<p><a class="big-link" href="defect-classes/index.html">'
               'Read the formal defect-class definitions &rarr;</a></p>')
    out.append('</section>')

    out.append('<h2>Browse by section</h2>')
    out.append('<div class="section-grid">')
    for section_dir in sorted(by_section.keys()):
        entries = by_section[section_dir]
        label = _section_label(section_dir)
        sample_titles = [e["title"] for e in entries[:3]]
        out.append('<div class="section-card">')
        out.append(f'<h2><a href="{_h(section_dir)}/index.html">{_h(label)}</a></h2>')
        out.append(f'<p class="meta">{len(entries)} entries</p>')
        out.append('<ul class="samples">')
        for t in sample_titles:
            out.append(f'<li>{_h(t)}</li>')
        out.append('</ul></div>')
    out.append('</div>')
    out.append('</main>')
    out.append(_footer())
    return "\n".join(out)


# ---------------------------------------------------------------------------
# By-tag (cross-cutting taxonomy) pages
# ---------------------------------------------------------------------------

def _entries_by_tag(entries: list[dict]) -> dict[str, list[dict]]:
    """Group entries by taxonomy tag. Each entry may appear under multiple tags."""
    out: dict[str, list[dict]] = {t: [] for t in _taxonomy.TAG_VOCABULARY}
    for e in entries:
        for tag in (e.get("taxonomy") or []):
            if tag in out:
                out[tag].append(e)
    # Sort entries within each tag by ID (numeric-aware via section+id).
    def sort_key(e: dict) -> tuple:
        eid = e["id"]
        m = re.match(r"^([A-Za-z]+)(\d+)$", eid)
        if m:
            return (m.group(1), int(m.group(2)))
        return (eid, 0)
    for t in out:
        out[t].sort(key=sort_key)
    return out


def render_by_tag_index(by_tag: dict[str, list[dict]]) -> str:
    """Render `browse/by-tag/index.html`: top-level taxonomy landing page."""
    title = "STEP Defect Catalog — Browse by defect class"
    css_href = "../assets/style.css"
    out: list[str] = [_shared_head(title, css_href)]
    out.append('<body class="by-tag-index">')
    out.append('<nav class="topnav">')
    out.append('<a href="../../index.html">Home</a> '
               '<span class="sep">/</span> '
               '<a href="../index.html">Browse</a> '
               '<span class="sep">/</span> '
               '<span class="current">By defect class</span>')
    out.append('</nav>')
    out.append('<header class="title-bar">')
    out.append('<h1>Browse by defect class</h1>')
    out.append('<p class="blurb">An orthogonal axis to the §12.x section '
               'taxonomy: each entry carries 1–3 cross-cutting tags '
               'describing the <em>kind</em> of defect (crash, silent-loss, '
               'spec-violation, etc.) rather than its location in the corpus.</p>')
    total_entries = sum(len(v) for v in by_tag.values())
    out.append(f'<p class="meta">{len(_taxonomy.TAG_VOCABULARY)} tags · '
               f'{total_entries} tag-entry pairs across '
               f'the catalog</p>')
    out.append('</header>')

    out.append('<main><div class="tag-grid">')
    for tag in _taxonomy.TAG_VOCABULARY:
        entries = by_tag.get(tag, [])
        desc = _taxonomy.TAG_DESCRIPTIONS.get(tag, "")
        out.append('<div class="tag-card">')
        out.append(f'<h2><a class="tag tag-{_h(tag)}" '
                   f'href="{_h(tag)}/index.html">{_h(tag)}</a></h2>')
        out.append(f'<p class="meta">{len(entries)} entries</p>')
        out.append(f'<p>{_h(desc)}</p>')
        out.append('</div>')
    out.append('</div></main>')
    out.append(_footer())
    return "\n".join(out)


def render_by_tag_section(tag: str, entries: list[dict],
                          id_index: dict[str, str]) -> str:
    """Render `browse/by-tag/<tag>/index.html` for a single tag."""
    title = f"STEP Defect Catalog — {tag}"
    css_href = "../../assets/style.css"
    out: list[str] = [_shared_head(title, css_href)]
    out.append('<body class="by-tag">')
    out.append('<nav class="topnav">')
    out.append('<a href="../../../index.html">Home</a> '
               '<span class="sep">/</span> '
               '<a href="../../index.html">Browse</a> '
               '<span class="sep">/</span> '
               '<a href="../index.html">By defect class</a> '
               '<span class="sep">/</span> '
               f'<span class="current">{_h(tag)}</span>')
    out.append('</nav>')
    out.append('<header class="title-bar">')
    out.append(f'<h1><span class="tag tag-{_h(tag)}">{_h(tag)}</span></h1>')
    desc = _taxonomy.TAG_DESCRIPTIONS.get(tag, "")
    if desc:
        out.append(f'<p class="blurb">{_h(desc)}</p>')
    out.append(f'<p class="meta">{len(entries)} entries</p>')
    out.append('</header>')

    out.append('<main>')
    out.append('<table class="entries"><thead><tr>'
               '<th>ID</th><th>Title</th><th>Section</th>'
               '<th>Expected validation</th>'
               '</tr></thead><tbody>')
    for e in entries:
        section_dir = e["section_dir"]
        # Per-fixture page lives at browse/<section>/<id>.html;
        # we are at browse/by-tag/<tag>/index.html, so the link is
        # ../../<section>/<id>.html.
        href = f'../../{section_dir}/{e["id"]}.html'
        section_label = _section_label(section_dir)
        out.append(
            f'<tr><td><a href="{_h(href)}"><code>{_h(e["id"])}</code></a></td>'
            f'<td>{_h(e["title"])}</td>'
            f'<td><a href="../../{_h(section_dir)}/index.html">'
            f'{_h(section_label)}</a></td>'
            f'<td><code>{_h(e["expected_validation"])}</code></td></tr>'
        )
    out.append('</tbody></table>')
    out.append('</main>')
    out.append(_footer())
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

def render_landing(by_section: dict[str, list[dict]],
                   id_index: dict[str, str]) -> str:
    title = "STEP Defect Catalog"
    css_href = "browse/assets/style.css"
    out: list[str] = [_shared_head(title, css_href)]
    out.append('<body class="landing">')
    out.append('<header class="hero">')
    out.append('<h1>STEP Defect Catalog</h1>')
    out.append(
        '<p>A catalogued corpus of STEP-file (ISO 10303-21 / -42 / -214 / -242) '
        'input pathologies, paired with a multi-tier validator that '
        'adversarially confirms each fixture really exhibits the defect '
        'it claims.</p>'
    )
    out.append(
        '<p>The goal: a license-clean, citable, reproducible reference for '
        'CAD-kernel and STEP-tooling authors — every BOM, half-escaped '
        'string, near-period pcurve, knot-vector mistake, schema mash-up, '
        'unit confusion, PMI corner case, and adversarial input that '
        'production parsers grow tolerance for over time.</p>'
    )
    total = sum(len(v) for v in by_section.values())
    out.append('<p class="stats">'
               f'<strong>{total}</strong> entries · '
               f'<strong>{len(by_section)}</strong> sections · '
               '<strong>455</strong> validator tests · '
               '<strong>0</strong> DRIFT/FAIL/ERROR'
               '</p>')
    out.append('</header>')

    out.append('<main>')
    out.append('<section class="quicklinks">')
    out.append('<h2>Quick links</h2>')
    out.append('<ul>')
    out.append('<li><a href="browse/index.html">Browse by section &rarr;</a></li>')
    out.append('<li><a href="browse/by-tag/index.html">Browse by defect class '
               '(crash, silent-loss, …) &rarr;</a></li>')
    # Pick a representative section for "browse all"
    out.append('<li><a href="browse/index.html">Browse all entries &rarr;</a></li>')
    out.append('<li><a href="STEP_PROBLEM_CATALOG.md">Catalog markdown (raw) &rarr;</a></li>')
    out.append('<li><a href="QUALITY_DASHBOARD.md">Quality dashboard &rarr;</a></li>')
    out.append('<li><a href="https://github.com/zellyn/cad/tree/main/research">View on GitHub &rarr;</a></li>')
    out.append('</ul>')
    out.append('</section>')

    out.append('<section class="featured">')
    out.append('<h2>Featured findings</h2>')
    out.append('<ul class="findings">')
    for fid, blurb in FEATURED_FINDINGS:
        sec = id_index.get(fid)
        if sec:
            href = f"browse/{sec}/{fid}.html"
            link = f'<a href="{_h(href)}"><code>{_h(fid)}</code></a>'
        else:
            link = f'<code>{_h(fid)}</code>'
        out.append(f'<li>{link} — {_h(blurb)}</li>')
    out.append('</ul>')
    out.append('</section>')

    out.append('</main>')
    out.append(_footer())
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
/* STEP Defect Catalog — static-site stylesheet */
:root {
    --bg: #ffffff;
    --fg: #1a1a1a;
    --muted: #555;
    --border: #d0d0d0;
    --accent: #0a4d8c;
    --accent-bg: #f3f7fb;
    --code-bg: #f4f4f4;
    --row-alt: #f8f9fa;
    --hover: #eef3f8;
}
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #15181c;
        --fg: #e6e6e6;
        --muted: #9aa0a6;
        --border: #2c3035;
        --accent: #6db1e8;
        --accent-bg: #1c2632;
        --code-bg: #1f2429;
        --row-alt: #1a1d22;
        --hover: #232a32;
    }
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--fg);
    line-height: 1.5;
    max-width: 60rem;
    margin: 0 auto;
    padding: 1.5rem 1.25rem 4rem;
}
code, pre, .path { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
code {
    background: var(--code-bg);
    padding: 0.05rem 0.3rem;
    border-radius: 3px;
    font-size: 0.95em;
}
pre {
    background: var(--code-bg);
    padding: 0.75rem 1rem;
    border-radius: 4px;
    overflow-x: auto;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { font-size: 1.6rem; margin: 0 0 0.5rem; }
h2 { font-size: 1.2rem; margin: 1.5rem 0 0.5rem;
     padding-bottom: 0.25rem;
     border-bottom: 1px solid var(--border); }
h3 { font-size: 1.05rem; margin: 1.25rem 0 0.4rem; }
p { margin: 0.4rem 0 0.8rem; }
ul { margin: 0.4rem 0 0.8rem; padding-left: 1.5rem; }
li { margin: 0.15rem 0; }
.muted, .meta { color: var(--muted); font-size: 0.9em; }
.sep { color: var(--muted); margin: 0 0.25rem; }
.current { color: var(--muted); }

/* Top nav */
nav.topnav {
    font-size: 0.9em;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* Title bar */
header.title-bar {
    margin-bottom: 1.5rem;
}
header.title-bar .entry-title { font-weight: normal; color: var(--muted); }
header.title-bar .category { color: var(--muted); margin: 0.25rem 0; }
header.title-bar .blurb { font-size: 1.05em; margin: 0.5rem 0; }

/* Fixture link */
.fixture-link {
    background: var(--accent-bg);
    border-left: 3px solid var(--accent);
    padding: 0.6rem 0.9rem;
    margin: 1rem 0;
    border-radius: 3px;
}
.fixture-link .big-link {
    font-weight: bold;
    margin-right: 0.5rem;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.5rem 0 1rem;
    font-size: 0.95em;
}
th, td {
    text-align: left;
    padding: 0.4rem 0.6rem;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}
th {
    background: var(--code-bg);
    font-weight: 600;
}
tbody tr:nth-child(even) { background: var(--row-alt); }
tbody tr:hover { background: var(--hover); }

/* Oracle table — narrower */
table.oracle { max-width: 32rem; }

/* Assertion lists */
ul.assertions { list-style: square; }
ul.assertions li code { background: transparent; padding: 0; }

/* Section grid (browse index) */
.section-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.section-card {
    border: 1px solid var(--border);
    padding: 0.8rem 1rem;
    border-radius: 4px;
    background: var(--bg);
}
.section-card h2 {
    margin: 0 0 0.3rem;
    border-bottom: none;
    font-size: 1.05rem;
}
.section-card .samples {
    list-style: square;
    font-size: 0.9em;
    color: var(--muted);
}

/* Landing */
body.landing { max-width: 50rem; }
.hero { text-align: center; padding: 1.5rem 0; }
.hero h1 { font-size: 2rem; }
.hero .stats {
    background: var(--accent-bg);
    padding: 0.6rem 1rem;
    border-radius: 4px;
    display: inline-block;
    margin-top: 0.75rem;
}
.quicklinks ul { list-style: none; padding-left: 0; }
.quicklinks li { padding: 0.2rem 0; }
.findings { list-style: none; padding-left: 0; }
.findings li {
    padding: 0.5rem 0.8rem;
    border-left: 2px solid var(--border);
    margin-bottom: 0.5rem;
}

/* Severity badge — P0/P1/P2/P3 priority for kernel-grading. */
.severity-badge {
    display: inline-block;
    margin: 0.35rem 0 0.25rem;
    padding: 0.15rem 0.6rem;
    font-size: 0.85em;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-weight: 600;
    border-radius: 4px;
    border: 1px solid var(--border);
    background: var(--code-bg);
    color: var(--fg);
}
.severity-p0 { background: #fde2e2; color: #7a1a1a; border-color: #f0a5a5; }
.severity-p1 { background: #ffe4d2; color: #7a3b1a; border-color: #efb389; }
.severity-p2 { background: #fff2cc; color: #6b4f00; border-color: #e8d178; }
.severity-p3 { background: #e7f0ff; color: #1a3d7a; border-color: #a8c2ee; }
@media (prefers-color-scheme: dark) {
    .severity-p0 { background: #5a1f1f; color: #ffd0d0; border-color: #803333; }
    .severity-p1 { background: #5a341f; color: #ffd9bf; border-color: #80582b; }
    .severity-p2 { background: #5a4a1a; color: #ffe9a8; border-color: #806b33; }
    .severity-p3 { background: #1f3050; color: #cce0ff; border-color: #335080; }
}

/* Tag pills (taxonomy / defect-class) */
.tag-pills {
    margin: 0.5rem 0 0.25rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}
a.tag, span.tag {
    display: inline-block;
    padding: 0.1rem 0.5rem;
    font-size: 0.8em;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--code-bg);
    color: var(--fg);
    text-decoration: none;
    line-height: 1.6;
}
a.tag:hover { background: var(--hover); text-decoration: none; }
.tag-crash          { background: #fde2e2; color: #7a1a1a; border-color: #f0a5a5; }
.tag-silent-loss    { background: #fff2cc; color: #6b4f00; border-color: #e8d178; }
.tag-round-trip     { background: #e7f0ff; color: #1a3d7a; border-color: #a8c2ee; }
.tag-spec-violation { background: #f3e2ff; color: #4a1a7a; border-color: #c9a5ee; }
.tag-interop        { background: #e2f5ec; color: #1a5c3a; border-color: #a5d8be; }
.tag-performance    { background: #ffe4d2; color: #7a3b1a; border-color: #efb389; }
.tag-adversarial    { background: #fde2f0; color: #7a1a4d; border-color: #ee9bc7; }
.tag-geometry       { background: #e2efff; color: #1a4d7a; border-color: #a5c8ee; }
.tag-topology       { background: #e2faff; color: #1a5c70; border-color: #a5d6ee; }
.tag-pmi            { background: #f5e2ff; color: #4d1a7a; border-color: #ceaaee; }
.tag-assembly       { background: #e2f5e2; color: #1a5c1a; border-color: #a5d8a5; }
.tag-encoding       { background: #fff5e2; color: #6b4a1a; border-color: #eecba5; }
.tag-syntax         { background: #f5f5e2; color: #5c5c1a; border-color: #d8d8a5; }
.tag-units          { background: #e2f0e9; color: #1a5c3d; border-color: #a5cdba; }
.tag-writer         { background: #f0e2f0; color: #5c1a5c; border-color: #cda5cd; }
@media (prefers-color-scheme: dark) {
    a.tag, span.tag { background: #2a2f35; color: var(--fg); border-color: #3c424a; }
    a.tag:hover { background: #353b43; }
    .tag-crash          { background: #5a1f1f; color: #ffd0d0; border-color: #803333; }
    .tag-silent-loss    { background: #5a4a1a; color: #ffe9a8; border-color: #806b33; }
    .tag-round-trip     { background: #1f3050; color: #cce0ff; border-color: #335080; }
    .tag-spec-violation { background: #3d1f5a; color: #e6cdff; border-color: #663380; }
    .tag-interop        { background: #1f4a3a; color: #c9efd9; border-color: #336b50; }
    .tag-performance    { background: #5a341f; color: #ffd9bf; border-color: #80582b; }
    .tag-adversarial    { background: #5a1f3d; color: #ffcce0; border-color: #803366; }
    .tag-geometry       { background: #1f3d5a; color: #cce0ff; border-color: #335980; }
    .tag-topology       { background: #1f4a5a; color: #cce8ef; border-color: #336b80; }
    .tag-pmi            { background: #3d1f5a; color: #d9c0ee; border-color: #663380; }
    .tag-assembly       { background: #1f4a1f; color: #c9efc9; border-color: #336b33; }
    .tag-encoding       { background: #5a4a1f; color: #ffe5b3; border-color: #80683d; }
    .tag-syntax         { background: #4a4a1f; color: #efef99; border-color: #6b6b33; }
    .tag-units          { background: #1f4a3d; color: #c9efe5; border-color: #336b58; }
    .tag-writer         { background: #4a1f4a; color: #efc9ef; border-color: #6b336b; }
}

/* Tag grid (by-tag landing page) */
.tag-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.tag-card {
    border: 1px solid var(--border);
    padding: 0.8rem 1rem;
    border-radius: 4px;
    background: var(--bg);
}
.tag-card h2 { margin: 0 0 0.3rem; border-bottom: none; font-size: 1.05rem; }

.by-tag-cta {
    background: var(--accent-bg);
    border-left: 3px solid var(--accent);
    padding: 0.7rem 1rem;
    margin: 1rem 0 1.5rem;
    border-radius: 3px;
}

/* prev/next nav */
nav.prevnext {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    align-items: center;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 0.95em;
}
nav.prevnext .up { color: var(--muted); }

footer {
    margin-top: 3rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border);
}
footer .meta { font-size: 0.85em; }

/* Fixture-bytes block with inline defect highlighting */
.fixture-bytes {
    max-height: 60vh;
    overflow-y: auto;
    padding: 0.75em 1em;
    background: var(--code-bg);
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.85em;
    line-height: 1.4;
    white-space: pre;
}
.fixture-bytes mark {
    background: rgba(255, 220, 50, 0.5);
    color: inherit;
    padding: 0 1px;
    border-radius: 2px;
}
.fixture-bytes .lineno {
    display: inline-block;
    width: 4em;
    color: var(--muted);
    text-align: right;
    user-select: none;
    margin-right: 1em;
}
.fixture-bytes .truncation {
    color: var(--muted);
    font-style: italic;
}
@media (prefers-color-scheme: dark) {
    .fixture-bytes mark {
        background: rgba(255, 200, 0, 0.35);
    }
}
"""


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_all(out_root: Path, *, clean: bool = False) -> dict[str, int]:
    """Render the entire site under ``out_root``.

    ``out_root`` should be the research root: ``index.html`` is written
    directly into it; the rest goes under ``out_root/browse/``.

    Returns a counter dict of per-section page counts plus a few totals.
    """
    entries = catalog.load_catalog()
    by_section = _entries_by_section(entries)
    id_index = _fixture_id_index(entries)

    browse_root = out_root / "browse"
    if clean and browse_root.is_dir():
        # Preserve assets/, the .gitkeep, and .nojekyll. Easiest: nuke
        # everything except .gitkeep, then re-create assets/.
        for child in browse_root.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    counts: dict[str, int] = {"sections": 0, "fixtures": 0, "indexes": 0}

    # CSS
    css_path = browse_root / "assets" / "style.css"
    _write(css_path, CSS)

    # Per-fixture + per-section pages
    for section_dir, sec_entries in sorted(by_section.items()):
        section_root = browse_root / section_dir
        for idx, entry in enumerate(sec_entries):
            page = render_fixture_page(entry, sec_entries, idx, id_index)
            target = section_root / f"{entry['id']}.html"
            _write(target, page)
            counts["fixtures"] += 1
        sec_index = render_section_index(section_dir, sec_entries)
        _write(section_root / "index.html", sec_index)
        counts["sections"] += 1

    # Browse index
    _write(browse_root / "index.html", render_browse_index(by_section))
    counts["indexes"] += 1

    # By-tag (cross-cutting taxonomy) pages
    by_tag = _entries_by_tag(entries)
    by_tag_root = browse_root / "by-tag"
    _write(by_tag_root / "index.html", render_by_tag_index(by_tag))
    counts["indexes"] += 1
    for tag, tag_entries in by_tag.items():
        _write(
            by_tag_root / tag / "index.html",
            render_by_tag_section(tag, tag_entries, id_index),
        )
        counts["indexes"] += 1

    # Landing page
    _write(out_root / "index.html", render_landing(by_section, id_index))
    counts["indexes"] += 1

    return counts


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._render_pages")
    p.add_argument("--out-root", type=Path, default=_research_root(),
                   help="Repo root to render into "
                        "(default: research/ — sibling of validation/)")
    p.add_argument("--clean", action="store_true",
                   help="Remove browse/<section>/ before rendering")
    args = p.parse_args(argv)

    counts = render_all(args.out_root, clean=args.clean)
    print(f"Rendered {counts['fixtures']} fixture pages "
          f"in {counts['sections']} sections "
          f"+ {counts['indexes']} top-level pages "
          f"under {args.out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
