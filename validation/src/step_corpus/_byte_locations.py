"""Locate byte ranges in a fixture matched by catalog ``byte_assertions``.

Companion to :mod:`step_corpus._byte_assertions`: where that module returns a
boolean pass/fail for each assertion expression, this one returns the
``(start, end)`` byte offsets of the *positive* matches inside the fixture
body. Used by the static-site renderer to draw inline ``<mark>`` highlights
on each per-fixture page so a reader can see the defect without grepping.

Supported expression forms (others are treated as structural and yield no
positional information):

- ``contains(b'…')`` -- every occurrence of the literal substring
- ``matches(rb'…')`` -- every regex match
- ``bytes_starts_with(b'…')`` -- a single match at offset 0 if the
  prefix is present
- ``bytes_ends_with(b'…')`` -- a single match at the trailing position
  if the suffix is present (after rstrip(), as the assertion does)
- ``count(b'…')`` -- every occurrence of the substring (regardless of the
  comparison's right-hand side)
- ``count_entity_def(b'TYPE')`` -- every ``#N=TYPE(`` definition
- ``not_contains`` / ``length`` / ``max_paren_depth`` / ``max_string_literal_length``
  / ``declared_schema`` -- structural, no positional matches; returns ``[]``

The parser is intentionally limited to the literal-argument forms used by
the corpus catalog. Unknown expression shapes degrade safely to ``[]``.
"""
from __future__ import annotations

import ast
import re
from typing import Iterable

from step_corpus._byte_assertions import _RE_INSTANCE_DEF


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _literal_bytes_arg(call: ast.Call) -> bytes | None:
    """Return the single bytes literal arg of a Call, or None."""
    if len(call.args) != 1 or call.keywords:
        return None
    arg = call.args[0]
    try:
        value = ast.literal_eval(arg)
    except Exception:
        return None
    if isinstance(value, bytes):
        return value
    return None


def _toplevel_call(expr_ast: ast.AST) -> ast.Call | None:
    """Find the top-level Call node in an expression. For ``count(b'#') >= 100``
    that is ``count(b'#')``; for ``contains(b'X')`` it is the call itself.
    """
    if isinstance(expr_ast, ast.Expression):
        expr_ast = expr_ast.body
    if isinstance(expr_ast, ast.Call):
        return expr_ast
    if isinstance(expr_ast, ast.Compare):
        # left is a Call for `count(...) >= N` style assertions
        if isinstance(expr_ast.left, ast.Call):
            return expr_ast.left
    return None


# ---------------------------------------------------------------------------
# Per-form locators
# ---------------------------------------------------------------------------

def _locate_contains(body: bytes, needle: bytes) -> list[tuple[int, int]]:
    if not needle:
        return []
    out: list[tuple[int, int]] = []
    start = 0
    n = len(needle)
    while True:
        idx = body.find(needle, start)
        if idx < 0:
            break
        out.append((idx, idx + n))
        # Advance by 1 to find overlapping matches; this is fine for our
        # usage (e.g. count(b'##') across ##abc##abc) and avoids missing
        # overlapping occurrences. Patterns are typically distinct enough
        # that overlap is rare, but cheap to handle.
        start = idx + 1
    return out


def _locate_regex(body: bytes, pattern: bytes) -> list[tuple[int, int]]:
    try:
        rx = re.compile(pattern, re.DOTALL)
    except re.error:
        return []
    out: list[tuple[int, int]] = []
    for m in rx.finditer(body):
        s, e = m.span()
        if e > s:
            out.append((s, e))
    return out


def _locate_starts_with(body: bytes, prefix: bytes) -> list[tuple[int, int]]:
    if prefix and body.startswith(prefix):
        return [(0, len(prefix))]
    return []


def _locate_ends_with(body: bytes, suffix: bytes) -> list[tuple[int, int]]:
    stripped = body.rstrip()
    if suffix and stripped.endswith(suffix):
        end = len(stripped)
        return [(end - len(suffix), end)]
    return []


def _locate_count_entity_def(body: bytes, type_name: bytes) -> list[tuple[int, int]]:
    target = type_name.upper()
    out: list[tuple[int, int]] = []
    for m in _RE_INSTANCE_DEF.finditer(body):
        if m.group(1).upper() == target:
            # Highlight the whole "#N=TYPE(" head so the reader can see
            # each definition. m.span() includes leading ';' or BOL anchor;
            # tighten to start at '#' to avoid eating the preceding char.
            s, e = m.span()
            # Skip over the leading ';' or whitespace to start at '#'.
            while s < e and body[s:s + 1] != b"#":
                s += 1
            if s < e:
                out.append((s, e))
    return out


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------

def find_match_locations(body: bytes, assertion: str) -> list[tuple[int, int]]:
    """Return the ``(start, end)`` byte offsets matched by ``assertion`` in ``body``.

    Returns ``[]`` when the assertion has no positional meaning (structural
    checks like ``length > N`` or negative checks like ``not_contains``), or
    when the expression cannot be parsed.
    """
    try:
        tree = ast.parse(assertion, mode="eval")
    except SyntaxError:
        return []
    call = _toplevel_call(tree)
    if call is None or not isinstance(call.func, ast.Name):
        return []
    fn = call.func.id

    # Negative / structural assertions: no positive location.
    if fn in {"not_contains", "length", "max_paren_depth",
              "max_string_literal_length", "declared_schema",
              "bytes_ends_with"}:
        # bytes_ends_with technically does have a position, but in practice
        # the trailing token is rarely interesting; still expose it below.
        if fn == "bytes_ends_with":
            arg = _literal_bytes_arg(call)
            if arg is None:
                return []
            return _locate_ends_with(body, arg)
        return []

    arg = _literal_bytes_arg(call)
    if arg is None:
        return []

    if fn == "contains":
        return _locate_contains(body, arg)
    if fn == "matches":
        return _locate_regex(body, arg)
    if fn == "bytes_starts_with":
        return _locate_starts_with(body, arg)
    if fn == "count":
        return _locate_contains(body, arg)
    if fn == "count_entity_def":
        return _locate_count_entity_def(body, arg)

    # Unknown function name -- treat as structural / no location.
    return []


# ---------------------------------------------------------------------------
# Range merging
# ---------------------------------------------------------------------------

def merge_ranges(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Sort and merge overlapping/adjacent ``(start, end)`` half-open ranges."""
    items = sorted((s, e) for s, e in ranges if e > s)
    if not items:
        return []
    out: list[tuple[int, int]] = [items[0]]
    for s, e in items[1:]:
        ls, le = out[-1]
        if s <= le:
            if e > le:
                out[-1] = (ls, e)
        else:
            out.append((s, e))
    return out


def find_all_match_locations(body: bytes,
                             assertions: Iterable[str]) -> list[tuple[int, int]]:
    """Convenience: union of locations over an iterable of assertions, merged."""
    all_ranges: list[tuple[int, int]] = []
    for a in assertions:
        all_ranges.extend(find_match_locations(body, a))
    return merge_ranges(all_ranges)
