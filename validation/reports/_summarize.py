"""Compact summary of validation results for adversarial review."""
import json
import sys
from pathlib import Path


def summarize(path):
    data = json.loads(Path(path).read_text())
    out = []
    for fname, r in data.items():
        be = r.get("byte_entity", {})
        be_d = be.get("data", {}) if be.get("_status") == "ok" else {}
        bs = be_d.get("byte_signature", {})
        es = be_d.get("entity_summary", {})
        ifc = r.get("ifcopenshell", {})
        ifc_d = ifc.get("data", {}) if ifc.get("_status") == "ok" else {}
        ohon = r.get("occt_heal_on", {})
        ohon_d = ohon.get("data", {}) if ohon.get("_status") == "ok" else {}
        ohoff = r.get("occt_heal_off", {})
        ohoff_d = ohoff.get("data", {}) if ohoff.get("_status") == "ok" else {}
        t3 = r.get("tier3", {})
        t3_d = t3.get("data", {}) if t3.get("_status") == "ok" else {}
        line = {
            "file": fname,
            "size": bs.get("size"),
            "schema": bs.get("file_schema"),
            "iso_open": bs.get("starts_with_iso_token"),
            "iso_close": bs.get("ends_with_close_token"),
            "n_entities": es.get("total_entity_definitions"),
            "top_types": list((es.get("top_types") or {}).keys())[:8],
            "ifc_status": ifc.get("_status") + (":" + ifc_d.get("status", "") if ifc_d else ""),
            "occt_on": ohon.get("_status") + (
                ":" + str(ohon_d.get("status", "")) if ohon.get("_status") == "ok" else ""
            ),
            "occt_on_shape_null": ohon_d.get("shape_null"),
            "occt_on_n_roots": ohon_d.get("n_roots"),
            "occt_off": ohoff.get("_status") + (
                ":" + str(ohoff_d.get("status", "")) if ohoff.get("_status") == "ok" else ""
            ),
            "occt_off_shape_null": ohoff_d.get("shape_null"),
            "tier3": t3.get("_status"),
        }
        # Tier3 specifics
        if t3_d:
            line["t3_load"] = t3_d.get("load")
            line["t3_n_faces"] = len(t3_d.get("faces") or [])
            line["t3_n_edges"] = t3_d.get("n_edges_total", 0)
            line["t3_n_verts"] = t3_d.get("n_vertices_total", 0)
            line["t3_brepcheck_valid"] = (t3_d.get("brepcheck") or {}).get("is_valid")
            faces = t3_d.get("faces") or []
            if faces:
                line["t3_face_areas"] = [round(f.get("area", 0), 6) for f in faces]
                line["t3_face_types"] = [f.get("surface_type") for f in faces]
            par = t3_d.get("parametric") or {}
            if par.get("bsplines"):
                line["t3_bsplines"] = par["bsplines"][:4]
            if par.get("weights_groups"):
                line["t3_weights"] = par["weights_groups"][:3]
        out.append(line)
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(f"=== {p} ===")
        for line in summarize(p):
            print(json.dumps(line, default=str))
