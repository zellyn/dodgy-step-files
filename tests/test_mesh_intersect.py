"""Unit tests for `_triangles_intersect` — pure-Python Möller tri-tri intersect.

The function is the new pure-Python replacement for the previous "needs
CGAL" stub in `_mesh_oracle.py`. These tests pin down the geometric
contract so future edits don't quietly regress.
"""
from __future__ import annotations

from step_corpus._mesh_oracle import _triangles_intersect


def test_disjoint_triangles_no_intersect():
    a = ([0, 0, 0], [1, 0, 0], [0, 1, 0])
    b = ([10, 10, 0], [11, 10, 0], [10, 11, 0])
    assert _triangles_intersect(*a, *b) is False


def test_me005_xy_xz_crossing_pair():
    """The Me005 fixture geometry: XY-plane triangle and XZ-plane triangle
    share vertex (0,0,0) and cross along the line x=t, y=0, z=0."""
    a = ([0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, -1.0, 0.0])
    b = ([0.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 0.0, -1.0])
    assert _triangles_intersect(*a, *b) is True


def test_shared_vertex_only_no_cross():
    """Two triangles meeting at one vertex but otherwise pointing away
    must NOT register as intersecting (real geometry: a fan)."""
    a = ([0, 0, 0], [1, 0, 0], [0, 1, 0])
    b = ([0, 0, 0], [-1, 0, 0], [0, -1, 0])
    # Both triangles in z=0 plane, sharing only the origin.
    # Coplanar — the 2D SAT test should accept (origin is a shared
    # point), but we expect the planar-overlap test to declare them
    # non-overlapping because their interiors are disjoint. This pins
    # the coplanar fallback's strictness.
    assert _triangles_intersect(*a, *b) is False


def test_parallel_planes_no_intersect():
    a = ([0, 0, 0], [1, 0, 0], [0, 1, 0])
    b = ([0, 0, 1], [1, 0, 1], [0, 1, 1])
    assert _triangles_intersect(*a, *b) is False


def test_coplanar_overlap():
    """Two coplanar triangles whose interiors overlap with positive area."""
    a = ([0, 0, 0], [4, 0, 0], [0, 4, 0])
    b = ([1, 1, 0], [3, 1, 0], [1, 3, 0])
    assert _triangles_intersect(*a, *b) is True


def test_coplanar_corner_touch_only():
    """Coplanar pair meeting at a single corner — not positive overlap."""
    a = ([0, 0, 0], [2, 0, 0], [0, 2, 0])
    b = ([1, 1, 0], [3, 1, 0], [1, 3, 0])
    # B's corner (1,1) lies on A's edge x+y=2; intersection is one point.
    assert _triangles_intersect(*a, *b) is False


def test_one_vertex_pierces_other_triangle():
    """Triangle B pierces triangle A through its interior."""
    a = ([0, 0, 0], [2, 0, 0], [0, 2, 0])  # z=0 triangle
    # B's edge B0-B1 crosses A's interior at (0.5, 0.5, 0).
    b = ([0.5, 0.5, -1], [0.5, 0.5, 1], [3, 3, 0])
    assert _triangles_intersect(*a, *b) is True
