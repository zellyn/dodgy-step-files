"""Tests for the static-site generator (`step_corpus._render_pages`).

These tests render the entire site into a `tmp_path` so they don't pollute
the actual ``browse/`` directory, then spot-check that:

- the driver returns clean exit code 0
- the expected files exist for a sample of catalog entries
- the rendered HTML is well-formed (matching ``<html>``/``</html>``)
- the landing, browse index, and section index pages exist
- per-fixture pages link back to the correct fixture path
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from step_corpus import _render_pages, catalog


@pytest.fixture(scope="module")
def rendered(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Render the whole site once, share across this module."""
    out_root = tmp_path_factory.mktemp("site_root")
    counts = _render_pages.render_all(out_root, clean=False)
    assert counts["fixtures"] >= 1000
    assert counts["sections"] >= 10
    # 2 top-level (browse + landing) + 1 by-tag landing + 15 per-tag pages.
    assert counts["indexes"] == 18
    return out_root


def test_main_runs_without_error(tmp_path: Path) -> None:
    rc = _render_pages.main(["--out-root", str(tmp_path)])
    assert rc == 0


def test_landing_page_exists(rendered: Path) -> None:
    p = rendered / "index.html"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "<html" in text and "</html>" in text
    assert "STEP Defect Catalog" in text
    # Quick links should link into the browse hierarchy
    assert 'href="browse/index.html"' in text


def test_browse_index_exists(rendered: Path) -> None:
    p = rendered / "browse" / "index.html"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "<html" in text and "</html>" in text
    # Should mention every section_dir
    sections = {e["section_dir"] for e in catalog.load_catalog()}
    for s in sections:
        assert s in text, f"browse index missing section: {s}"


def test_section_index_exists_for_every_section(rendered: Path) -> None:
    sections = {e["section_dir"] for e in catalog.load_catalog()}
    for section_dir in sections:
        p = rendered / "browse" / section_dir / "index.html"
        assert p.is_file(), f"missing section index for {section_dir}"
        text = p.read_text(encoding="utf-8")
        assert "<html" in text and "</html>" in text


def test_css_is_written(rendered: Path) -> None:
    p = rendered / "browse" / "assets" / "style.css"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    # A few sanity sentinels for our stylesheet
    assert "prefers-color-scheme" in text
    assert "ui-monospace" in text


# Spot-check a handful of representative fixtures across different sections.
SPOT_CHECK_IDS = [
    "Le001",   # 12-1a-encoding
    "Le002",   # 12-1a-encoding
    "Pf001",   # 12-10-perf
    "Tsh001",  # 12-3a-shells (best-effort; existence not guaranteed)
    "Gn001",   # 12-2b-nurbs (best-effort)
]


def test_spot_check_fixture_pages(rendered: Path) -> None:
    entries_by_id = {e["id"]: e for e in catalog.load_catalog()}
    found = 0
    for eid in SPOT_CHECK_IDS:
        entry = entries_by_id.get(eid)
        if entry is None:
            continue
        p = rendered / "browse" / entry["section_dir"] / f"{eid}.html"
        assert p.is_file(), f"expected {p} to exist"
        text = p.read_text(encoding="utf-8")
        # Well-formedness sentinels
        assert "<html" in text and "</html>" in text
        assert "<body" in text and "</body>" in text
        # Title must include the entry id
        assert eid in text
        # Fixture link must point at the correct relative .stp path
        assert f"../../{entry['fixture_path']}" in text
        found += 1
    assert found >= 3, "spot check needs at least 3 known entries"


def test_html_is_well_formed_for_sample(rendered: Path) -> None:
    """Sample 10 fixtures and check matching <html>/<body> tags."""
    entries = catalog.load_catalog()
    # Take 10 evenly spaced samples
    step = max(1, len(entries) // 10)
    sample = entries[::step][:10]
    for entry in sample:
        p = rendered / "browse" / entry["section_dir"] / f"{entry['id']}.html"
        assert p.is_file()
        text = p.read_text(encoding="utf-8")
        # Single <html>... </html> wrapper
        assert text.count("<html") == 1
        assert text.count("</html>") == 1
        assert text.count("<body") == 1
        assert text.count("</body>") == 1
        # Should not have leaked unsubstituted Python format markers
        assert "{" + "_h(" not in text


def test_xref_links_use_relative_paths(rendered: Path) -> None:
    """Catalog entries that name see-also ids should produce <a href> links."""
    entries = catalog.load_catalog()
    # Find one entry with see_also entries that resolve to a known id
    valid_ids = {e["id"] for e in entries}
    target = None
    for entry in entries:
        sa = [x for x in (entry.get("see_also") or []) if x in valid_ids]
        if sa:
            target = (entry, sa[0])
            break
    if target is None:
        pytest.skip("no entry with resolvable see_also found")
    entry, ref = target
    p = rendered / "browse" / entry["section_dir"] / f"{entry['id']}.html"
    text = p.read_text(encoding="utf-8")
    # The referenced id must appear as either a same-section link or
    # a cross-section link (relative path beginning with ../).
    same = f'href="{ref}.html"'
    cross = re.compile(rf'href="\.\./[^"]+/{re.escape(ref)}\.html"')
    assert same in text or cross.search(text), (
        f"expected cross-ref link to {ref} in {p}"
    )


def test_fixture_content_block_present_on_per_fixture_pages(rendered: Path) -> None:
    """Per-fixture pages should embed a <details> block with the fixture bytes."""
    entries_by_id = {e["id"]: e for e in catalog.load_catalog()}
    # Le001 always has a UTF-8 BOM byte assertion -> we expect a <mark> tag.
    entry = entries_by_id.get("Le001")
    assert entry is not None, "Le001 missing from catalog"
    p = rendered / "browse" / entry["section_dir"] / "Le001.html"
    text = p.read_text(encoding="utf-8")
    assert "<h2>Fixture content</h2>" in text
    assert '<pre class="fixture-bytes">' in text
    # The BOM (EF BB BF) should be wrapped in a <mark> tag.
    assert "<mark>" in text and "</mark>" in text
    # Line numbers must be present.
    assert '<span class="lineno">' in text


def test_fixture_bytes_block_uses_details_collapsed_by_default(rendered: Path) -> None:
    """The Fixture content section uses a <details> wrapper so the page weight
    stays low until the reader expands it."""
    entries_by_id = {e["id"]: e for e in catalog.load_catalog()}
    entry = entries_by_id.get("Le001")
    assert entry is not None
    p = rendered / "browse" / entry["section_dir"] / "Le001.html"
    text = p.read_text(encoding="utf-8")
    # Find the section and ensure it contains a <details> with no `open` attr.
    section_start = text.find("<h2>Fixture content</h2>")
    assert section_start >= 0
    section_end = text.find("</section>", section_start)
    section_html = text[section_start:section_end]
    assert "<details>" in section_html
    assert "open" not in section_html.split("<details>", 1)[1].split(">", 1)[0]


def test_count_of_rendered_pages_matches_catalog(rendered: Path) -> None:
    entries = catalog.load_catalog()
    rendered_pages = list((rendered / "browse").rglob("*.html"))
    # Should have at least one page per entry plus per-section indexes
    # plus the browse/index.html top-level.
    sections = {e["section_dir"] for e in entries}
    expected_min = len(entries) + len(sections) + 1
    assert len(rendered_pages) >= expected_min, (
        f"rendered {len(rendered_pages)} pages, expected >= {expected_min}"
    )
