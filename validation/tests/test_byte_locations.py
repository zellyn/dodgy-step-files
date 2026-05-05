"""Tests for ``step_corpus._byte_locations``.

Each test exercises one byte-assertion form against a synthetic body and
checks that the returned ``(start, end)`` offsets match exactly what we'd
expect from a manual ``body.find(...)``.
"""
from __future__ import annotations

import pytest

from step_corpus import _byte_locations
from step_corpus._byte_locations import (
    find_all_match_locations,
    find_match_locations,
    merge_ranges,
)


# ---------------------------------------------------------------------------
# Per-form behaviour
# ---------------------------------------------------------------------------

def test_contains_single_match() -> None:
    body = b"hello world"
    locs = find_match_locations(body, "contains(b'world')")
    assert locs == [(6, 11)]
    assert body[6:11] == b"world"


def test_contains_multiple_matches() -> None:
    body = b"foo bar foo baz foo"
    locs = find_match_locations(body, "contains(b'foo')")
    # Three occurrences at offsets 0, 8, 16.
    assert locs == [(0, 3), (8, 11), (16, 19)]


def test_contains_missing_returns_empty() -> None:
    body = b"hello world"
    assert find_match_locations(body, "contains(b'xyz')") == []


def test_matches_regex() -> None:
    body = b"id=#42 and #100 and #7"
    locs = find_match_locations(body, "matches(rb'#\\d+')")
    assert locs == [(3, 6), (11, 15), (20, 22)]
    assert body[3:6] == b"#42"
    assert body[11:15] == b"#100"


def test_bytes_starts_with_present() -> None:
    body = b"\xef\xbb\xbfISO-10303-21;"
    locs = find_match_locations(body, "bytes_starts_with(b'\\xef\\xbb\\xbf')")
    assert locs == [(0, 3)]


def test_bytes_starts_with_absent() -> None:
    body = b"ISO-10303-21;"
    assert find_match_locations(body, "bytes_starts_with(b'\\xef\\xbb\\xbf')") == []


def test_bytes_ends_with_present() -> None:
    body = b"hello\nEND-ISO-10303-21;\n"
    locs = find_match_locations(body, "bytes_ends_with(b'END-ISO-10303-21;')")
    # rstrip() removes the trailing newline, so the suffix sits at offsets 6..23.
    assert locs == [(6, 23)]
    assert body[locs[0][0]:locs[0][1]] == b"END-ISO-10303-21;"


def test_count_returns_all_occurrences() -> None:
    body = b"##a##b##c"
    # `count(b'##') >= 3` -> three occurrences at 0,3,6.
    locs = find_match_locations(body, "count(b'##') >= 3")
    assert locs == [(0, 2), (3, 5), (6, 8)]


def test_count_entity_def_returns_each_def_head() -> None:
    body = b"#1=CARTESIAN_POINT('',(0.,0.,0.));\n#2=CARTESIAN_POINT('',(1.,1.,1.));"
    locs = find_match_locations(
        body, "count_entity_def(b'CARTESIAN_POINT') >= 2"
    )
    assert len(locs) == 2
    # Each match should start with '#' and span up to the opening '('.
    for s, e in locs:
        assert body[s:s + 1] == b"#"
        assert body[e - 1:e] == b"("


def test_not_contains_returns_empty() -> None:
    body = b"hello world"
    # not_contains is a *negative* assertion -- no positive match location.
    assert find_match_locations(body, "not_contains(b'X')") == []


def test_structural_assertions_return_empty() -> None:
    body = b"abcdef"
    for expr in (
        "length > 1024",
        "max_paren_depth > 50",
        "max_string_literal_length > 32768",
        "declared_schema == b'AUTOMOTIVE_DESIGN'",
    ):
        assert find_match_locations(body, expr) == [], expr


def test_unparseable_expression_returns_empty() -> None:
    assert find_match_locations(b"abc", "this is not python(") == []
    assert find_match_locations(b"abc", "unknown_fn(b'x')") == []


# ---------------------------------------------------------------------------
# Range merging
# ---------------------------------------------------------------------------

def test_merge_ranges_disjoint() -> None:
    assert merge_ranges([(0, 5), (10, 20)]) == [(0, 5), (10, 20)]


def test_merge_ranges_overlap() -> None:
    assert merge_ranges([(0, 5), (3, 8), (7, 10)]) == [(0, 10)]


def test_merge_ranges_adjacent_gets_merged() -> None:
    # Half-open: (0,5) and (5,10) touch at 5 but don't overlap -- but the
    # merge implementation collapses touching ranges since `s <= le`.
    assert merge_ranges([(0, 5), (5, 10)]) == [(0, 10)]


def test_merge_ranges_unsorted_input() -> None:
    assert merge_ranges([(20, 25), (0, 5), (3, 8)]) == [(0, 8), (20, 25)]


def test_merge_ranges_empty_and_zero_length() -> None:
    assert merge_ranges([]) == []
    assert merge_ranges([(5, 5)]) == []


def test_find_all_match_locations_unions_and_merges() -> None:
    body = b"aaa bbb aaa"
    locs = find_all_match_locations(
        body, ["contains(b'aaa')", "contains(b'bbb')"]
    )
    # Three a-runs and one b-run; they don't overlap so we get four ranges.
    assert locs == [(0, 3), (4, 7), (8, 11)]


# ---------------------------------------------------------------------------
# Highlight rendering correctness (uses the renderer, but at the byte level)
# ---------------------------------------------------------------------------

def test_highlighting_offsets_remain_correct_after_mark_insertion() -> None:
    """Insert <mark> tags by hand at the offsets returned and verify the
    content between them matches the original needle bytes.
    """
    body = b"prefix XYZ middle XYZ suffix"
    locs = find_match_locations(body, "contains(b'XYZ')")
    pieces: list[bytes] = []
    cursor = 0
    for s, e in locs:
        pieces.append(body[cursor:s])
        pieces.append(b"<mark>")
        pieces.append(body[s:e])
        pieces.append(b"</mark>")
        cursor = e
    pieces.append(body[cursor:])
    result = b"".join(pieces)
    assert result == b"prefix <mark>XYZ</mark> middle <mark>XYZ</mark> suffix"


@pytest.mark.parametrize("assertion", [
    "contains(b'\\xef\\xbb\\xbf')",
    "bytes_starts_with(b'\\xef\\xbb\\xbf')",
    "matches(rb'\\xef\\xbb\\xbf')",
])
def test_bom_assertions_all_locate_the_bom(assertion: str) -> None:
    body = b"\xef\xbb\xbfISO-10303-21;\n"
    locs = find_match_locations(body, assertion)
    assert locs == [(0, 3)], (assertion, locs)
