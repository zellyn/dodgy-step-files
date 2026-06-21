"""Xp041 — IfcOpenShell rejects valid IFC4X1 file due to lowercase 'x' in schema name."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp041",
             defect='IFC4x1 lowercase-x schema name rejected by IfcOpenShell strict whitelist')

# Override FILE_SCHEMA to emit IFC4x1 (lowercase x)
def _render_header_ifc4x1():
    return (
        "HEADER;\n"
        f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
        f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('IFC4x1'));\n"
        "ENDSEC;"
    )
f._render_header = _render_header_ifc4x1  # type: ignore[method-assign]

# Minimal IFC4x1-style data section (IFC entity names used as descriptors)
# IFCPROJECT, IFCGEOMETRICREPRESENTATIONCONTEXT, IFCAXIS2PLACEMENT3D, IFCCARTESIANPOINT
# These are IFC entity names but we just emit them as raw strings for the
# schema defect demonstration. The byte assertion only checks the FILE_SCHEMA line.

f._emit_raw("IFCCARTESIANPOINT((0.,0.,0.))")
f._emit_raw("IFCCARTESIANPOINT((0.,0.,1.))")
f._emit_raw("IFCAXIS2PLACEMENT3D(#1,#2,$)")
f._emit_raw("IFCDIRECTION((1.,0.,0.))")
f._emit_raw(
    "IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.0E-5,#3,#4)"
)
f._emit_raw("IFCPROJECT('xp041',#5,'Xp041 IFC4x1 lowercase-x schema test',$,$,$,$,(#6),$)")
