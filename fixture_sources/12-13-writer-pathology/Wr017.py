"""Wr017 — Tessellation re-emitted from B-rep input (silent precision loss).

Catalog claim: a file that carried MANIFOLD_SOLID_BREP geometry is
re-exported as TESSELLATED_SHELL_REPRESENTATION with triangle list.
Analytical surfaces are gone; the file is well-formed but has silently
become a mesh.

Reproducer recipe: a STEP file that contains only
TESSELLATED_SHELL_REPRESENTATION with a triangle list, claiming to
represent what was originally a CYLINDRICAL_SURFACE.

Byte assertions:
  contains(b'TESSELLATED_SHELL') or contains(b'TRIANGULATED_FACE')
  count_entity_def(b'TESSELLATED_SHELL_REPRESENTATION') >= 1 or count_entity_def(b'TRIANGULATED_FACE') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr017",
    defect=(
        "Tessellation re-emitted from B-rep input (silent precision loss); "
        "file carried MANIFOLD_SOLID_BREP with CYLINDRICAL_SURFACE on import; "
        "lightweight viewer tessellated internally and exported TESSELLATED_SHELL_REPRESENTATION; "
        "analytical surfaces are gone; file is well-formed but now mesh-only; "
        "cylinder became 8 facets instead of exact CYLINDRICAL_SURFACE; "
        "downstream boolean/offset operations produce stairstepped results; "
        "expected kernel behavior: warn and accept; "
        "detect tessellation-only content and emit a warning that round-trip "
        "from this file forward will be mesh-quality only; "
        "do not auto-fit surfaces back from triangles unless explicitly requested; "
        "synonyms: STEP went from B-rep to mesh, lost analytical surfaces on round-trip, "
        "cylinder became 36 facets, STEP file is now triangulated"
    ),
)


def _render_wr017() -> str:
    """Render a Part-21 with TESSELLATED_SHELL_REPRESENTATION approximating a cylinder."""
    import math

    # 8-sided triangulated cylinder approximation (what a lossy writer would emit)
    # Original was a CYLINDRICAL_SURFACE r=1, h=2.
    n = 8
    r = 1.0
    h = 2.0
    # Bottom ring: nodes 1..n, top ring: nodes n+1..2n, then bottom center + top center
    nodes = []
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        nodes.append((round(x, 6), round(y, 6), 0.0))
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        nodes.append((round(x, 6), round(y, 6), h))
    nodes.append((0.0, 0.0, 0.0))   # bottom cap center, index 2n+1
    nodes.append((0.0, 0.0, h))     # top cap center,    index 2n+2

    node_str = ",".join(f"({x},{y},{z})" for x, y, z in nodes)
    coords_line = f"COORDINATES_LIST('cyl_nodes',3,({node_str}))"

    # Side triangles: quad per segment → 2 triangles
    # node indices are 1-based
    tris = []
    for i in range(n):
        b1 = i + 1
        b2 = (i + 1) % n + 1
        t1 = b1 + n
        t2 = b2 + n
        tris.append((b1, b2, t2))
        tris.append((b1, t2, t1))
    # Bottom cap triangles
    bc = 2 * n + 1
    for i in range(n):
        b1 = i + 1
        b2 = (i + 1) % n + 1
        tris.append((bc, b2, b1))  # inward normal
    # Top cap triangles
    tc = 2 * n + 2
    for i in range(n):
        t1 = i + n + 1
        t2 = (i + 1) % n + n + 1
        tris.append((tc, t1, t2))

    tri_str = ",".join(f"({a},{b},{c})" for a, b, c in tris)
    ntri = len(tris)

    lines = [
        "ISO-10303-21;",
        "/* Wr017: B-rep cylinder re-exported as tessellated mesh (silent precision loss) */",
        "/* Original: MANIFOLD_SOLID_BREP with CYLINDRICAL_SURFACE r=1 h=2 */",
        "/* Writer tessellated to 8-sided polygon; CYLINDRICAL_SURFACE is gone */",
        "HEADER;",
        "FILE_DESCRIPTION(('Wr017 - tessellation re-emitted from B-rep input'),'2;1');",
        "FILE_NAME('Wr017.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');",
        "FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'));",
        "ENDSEC;",
        "DATA;",
        f"#1={coords_line};",
        f"#2=TRIANGULATED_FACE('cyl_tess',#1,.F.,{ntri},({tri_str}));",
        "#3=TESSELLATED_SHELL_REPRESENTATION('cylinder_approx',(#2),#1);",
        "ENDSEC;",
        "END-ISO-10303-21;",
        "",
    ]
    return "\n".join(lines)


def _write_wr017(path) -> None:
    Path(path).write_text(_render_wr017())


f.render = _render_wr017  # type: ignore[method-assign]
f.write = _write_wr017    # type: ignore[method-assign]
