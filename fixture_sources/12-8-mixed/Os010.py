"""Os010 — ThruSections loft profiles have inconsistent edge counts.

Catalog claim: Two loft profiles are both closed wires but with different edge
counts (3 edges vs 5 edges).  The "ruled" lofting algorithm needs a 1-to-1
correspondence between profiles' edges.

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - Profile 1: triangle (3 EDGE_CURVE edges, 1 EDGE_LOOP)
  - Profile 2: pentagon (5 EDGE_CURVE edges, 1 EDGE_LOOP)
Total EDGE_CURVE count = 8 (satisfies count_entity_def(b'EDGE_CURVE') == 8).

Byte assertions:
  - contains(b'EDGE_LOOP')
  - count_entity_def(b'EDGE_CURVE') == 8

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Os010",
    defect=(
        "GEOMETRIC_CURVE_SET containing two closed-wire loft profiles; "
        "profile 1: triangle with 3 EDGE_CURVE edges in EDGE_LOOP at z=0; "
        "profile 2: pentagon with 5 EDGE_CURVE edges in EDGE_LOOP at z=5; "
        "ruled ThruSections requires 1-to-1 edge pairing (ProfilesInconsistent); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)


def _polygon_coords(n: int, radius: float, z: float) -> list[tuple[float, float, float]]:
    """Return n vertices of a regular polygon at height z."""
    return [
        (radius * math.cos(math.radians(90 + 360 * i / n)),
         radius * math.sin(math.radians(90 + 360 * i / n)),
         z)
        for i in range(n)
    ]


def _build_polygon_loop(sf: StepFile, n: int, radius: float, z: float,
                        prefix: str, loop_name: str):
    """Build n straight-line EDGE_CURVEs for a closed polygon and return EDGE_LOOP."""
    coords = _polygon_coords(n, radius, z)
    pts    = [sf.cartesian_point(c) for c in coords]
    verts  = [sf.vertex_point(p)    for p in pts]

    edges = []
    for i in range(n):
        j      = (i + 1) % n
        x0, y0 = coords[i][0], coords[i][1]
        x1, y1 = coords[j][0], coords[j][1]
        length  = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        d       = sf.direction(((x1 - x0) / length, (y1 - y0) / length, 0.0))
        vec     = sf.vector(d, length)
        ln      = sf.line(pts[i], vec)
        ec      = sf.edge_curve(verts[i], verts[j], ln, True,
                                name=f"{prefix}_edge_{i}")
        edges.append(ec)

    oes  = [sf._emit_raw(f"ORIENTED_EDGE('',*,*,#{e.eid},.T.)") for e in edges]
    refs = ",".join(f"#{oe.eid}" for oe in oes)
    return sf._emit_raw(f"EDGE_LOOP('{loop_name}',({refs}))")


# ── Profile 1: equilateral triangle at z=0 (3 edges) ─────────────────────────
loop1 = _build_polygon_loop(f, n=3, radius=5.0, z=0.0,
                            prefix="tri", loop_name="triangle_profile")

# ── Profile 2: regular pentagon at z=5 (5 edges) ─────────────────────────────
loop2 = _build_polygon_loop(f, n=5, radius=5.0, z=5.0,
                            prefix="pent", loop_name="pentagon_profile")

# Sanity: 3 + 5 = 8 EDGE_CURVE entities — count_entity_def assertion satisfied.

# ── GEOMETRIC_CURVE_SET wrapping both loops ──────────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop1.eid},#{loop2.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os010.stp")
