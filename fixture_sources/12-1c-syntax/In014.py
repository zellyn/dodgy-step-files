"""In014 — LoadONBrep virtual-dispatch fall-through umbrella (BRL-CAD step-g).

Catalog claim: BRL-CAD step-g virtual-dispatches every subtype through
LoadONBrep; the base implementation prints to stderr and returns false.
A SEAM_CURVE referenced from a cylinder host demonstrates the pattern:
step-g's SeamCurve::LoadONBrep stub returns false and the seam geometry
is lost without propagating an error code to the caller.

Byte assertions:
  contains(b'SEAM_CURVE')
  contains(b'CYLINDRICAL_SURFACE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="In014",
    defect=(
        "LoadONBrep virtual-dispatch fall-through umbrella (BRL-CAD step-g); "
        "BRL-CAD src/conv/step/step-g/Curve.cpp base stub: "
        "std::cerr << Error: ::LoadONBrep(..) not implemented for << entityname; return false; "
        "same pattern in SeamCurve.cpp, CompositeCurve.cpp, CompositeCurveOnSurface.cpp, "
        "CurveBoundedSurface.cpp, RectangularCompositeSurface.cpp, SurfacePatch.cpp, "
        "CartesianTransformationOperator.cpp; "
        "defect: SEAM_CURVE referenced from a CYLINDRICAL_SURFACE cylinder host; "
        "step-g SeamCurve::LoadONBrep stub returns false and the seam geometry is lost; "
        "the diagnostic prints to stderr only and never propagates as an error code; "
        "callers cannot distinguish full success from partial geometry drop; "
        "receiver must reject: every stubbed dispatch must escalate to STEP_LOAD_ERROR; "
        "converter must exit non-zero when any subgraph reachable from "
        "ADVANCED_BREP_SHAPE_REPRESENTATION returned false; "
        "distinct from In013: here the actor exists but is a stub, not absent; "
        "bug-reporter synonyms: step-g LoadONBrep not implemented umbrella, "
        "virtual-dispatch fall-through silently drops geometry, "
        "stderr-only diagnostic for missing subtype, "
        "BRL-CAD step-g cannot escalate stub-misses to error; "
        "GEOMETRIC_CURVE_SET IS NOT used — SEAM_CURVE defect is the carrier"
    ),
)

# Override render() to emit a CYLINDRICAL_SURFACE with a SEAM_CURVE.
# The SEAM_CURVE is the entity that triggers the BRL-CAD LoadONBrep stub.
# SEAM_CURVE is a complex entity: it is a curve that lies on the seam of
# a periodic surface. In Part-21 it is typically encoded as a complex instance
# combining SEAM_CURVE + PCurve attributes.

_original_render = f.render


def _render_seam_curve() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Cylinder geometry */\n"
        f"#10=CARTESIAN_POINT('origin',(0.0,0.0,0.0));\n"
        f"#11=DIRECTION('z_axis',(0.0,0.0,1.0));\n"
        f"#12=DIRECTION('x_axis',(1.0,0.0,0.0));\n"
        f"#13=AXIS2_PLACEMENT_3D('cyl_placement',#10,#11,#12);\n"
        f"#14=CYLINDRICAL_SURFACE('cylinder',#13,5.0);\n"
        f"/* Seam line: the 3D edge curve along the seam of the cylinder */\n"
        f"#20=CARTESIAN_POINT('seam_start',(5.0,0.0,0.0));\n"
        f"#21=CARTESIAN_POINT('seam_end',(5.0,0.0,10.0));\n"
        f"#22=DIRECTION('seam_dir',(0.0,0.0,1.0));\n"
        f"#23=VECTOR('seam_vec',#22,10.0);\n"
        f"#24=LINE('seam_3d',#20,#23);\n"
        f"/* Parameter space: 2D line on cylinder surface (u=0 seam line) */\n"
        f"#30=CARTESIAN_POINT('seam_2d_start',(0.0,0.0));\n"
        f"#31=DIRECTION('seam_2d_dir',(0.0,1.0));\n"
        f"#32=VECTOR('seam_2d_vec',#31,10.0);\n"
        f"#33=LINE('seam_2d',#30,#32);\n"
        f"/* DEFINITIONAL_REPRESENTATION for pcurve */\n"
        f"#40=DEFINITIONAL_REPRESENTATION('',(#33),#50);\n"
        f"/* GEOMETRIC_REPRESENTATION_CONTEXT (2D) */\n"
        f"#50=GEOMETRIC_REPRESENTATION_CONTEXT(2);\n"
        f"/* PCURVE: associates 3D host surface with 2D parameter curve */\n"
        f"#41=PCURVE('',#14,#40);\n"
        f"/* SEAM_CURVE: the defect entity — triggers BRL-CAD LoadONBrep stub */\n"
        f"/* SEAM_CURVE(name, edge_geometry, associated_geometry, master_representation) */\n"
        f"#42=SEAM_CURVE('seam',#24,(#41),.PCURVE_S1.);\n"
        f"/* Topology referencing the seam curve */\n"
        f"#51=VERTEX_POINT('v_bot',#20);\n"
        f"#52=VERTEX_POINT('v_top',#21);\n"
        f"#53=EDGE_CURVE('seam_edge',#51,#52,#42,.T.);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_seam_curve  # type: ignore[method-assign]
