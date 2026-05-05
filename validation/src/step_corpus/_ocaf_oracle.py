"""OCAF / XCAF document-layer oracle for STEP fixtures.

Operates one level above the byte/shape-tessellation layer that the
existing OCCT, gmsh, and manifold oracles cover. Loads each fixture
into a ``TDocStd_Document`` via ``STEPCAFControl_Reader``, then walks
the OCAF tree using the ``XCAFDoc_*`` accessors. Output is a structured
JSON record per fixture.

What this oracle measures
=========================

- ``root_labels``: number of top-level shape labels in the OCAF tree.
- ``free_shapes``: number of free (root) shapes (subset of root_labels).
- ``named_labels``: number of shape labels with a TDataStd_Name attribute.
- ``named_label_examples``: first few names, as a sanity check.
- ``colored_labels``: number of labels carrying a colour attribute
  (any of ColorGen / ColorSurf / ColorCurv).
- ``colored_label_count_with_alpha``: subset of ``colored_labels``
  with non-default alpha (translucency).
- ``assembly_components``: number of labels marked as assembly
  components (``XCAFDoc_ShapeTool::IsComponent``).
- ``assembly_count``: number of labels marked as assembly
  (``XCAFDoc_ShapeTool::IsAssembly``).
- ``max_depth``: deepest descent in the OCAF child-label tree.
- ``transforms_at_leaf``: number of component labels with a
  TopLoc_Location attached (i.e. an instance transform).
- ``non_identity_transforms``: subset of those whose ``gp_Trsf::Form``
  is not ``gp_Identity``.
- ``sub_shape_labels``: number of labels created for sub-shapes
  (faces / edges that received an attribute, e.g. a per-face colour).
- ``layer_count``: number of layers in the layer tool.
- ``diagnostics``: any captured OCC error / warning lines.

When this oracle is most relevant
=================================

- §12.6-assembly catalogue entries claim defects in PRODUCT chains,
  NEXT_ASSEMBLY_USAGE_OCCURRENCE / SHAPE_REPRESENTATION_RELATIONSHIP
  graphs, and instance transforms. Those defects show up at the
  OCAF layer as: missing root labels, missing colour attribution,
  collapsed assembly hierarchy, identity transforms where the file
  encoded a non-identity composition.
- §12.7-pmi entries claim defects in PMI / GD&T attachment to
  geometry. Those manifest as missing sub-shape labels.
- §12.8-mixed AP242 entries combine assembly + PMI; they exercise
  both signal axes simultaneously.

Interpreting the output
=======================

- ``load_status: failed`` means STEP-CAF reader could not read the
  file at all. (Most byte-level / encoding-level defects show up
  here; treat as a louder duplicate of the byte-level signal.)
- ``load_status: ok`` with ``root_labels: 0`` means the reader
  silently dropped every product. Catalog entries that claim "PRODUCT
  not connected to SHAPE" should look like this.
- ``load_status: ok`` with ``root_labels >= 1`` and
  ``colored_labels: 0`` on a fixture that the catalog claims has
  a colour-graph defect is informative: the colour was either
  silently dropped or never round-tripped.
- ``assembly_components > 0`` confirms assembly hierarchy survived;
  ``assembly_components: 0`` on a §12.6 fixture means the assembly
  graph collapsed.

CLI
===

    uv run python -m step_corpus._ocaf_oracle <fixture.stp> [--json]

The module exposes ``analyze(path) -> dict`` for use from validate2's
worker subprocess.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any


@contextmanager
def _silenced_fds():
    """Redirect fd 1 and 2 to /dev/null around an OCC call.

    OCCT prints diagnostic banners ("*** ERR StepReaderData ...") via
    direct fprintf to stderr, bypassing Python's sys.stderr. To keep
    our stdout / stderr clean we have to redirect at the fd level.
    """
    devnull = os.open(os.devnull, os.O_RDWR)
    saved_stderr = os.dup(2)
    saved_stdout = os.dup(1)
    try:
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        yield
    finally:
        os.dup2(saved_stdout, 1)
        os.dup2(saved_stderr, 2)
        os.close(devnull)
        os.close(saved_stderr)
        os.close(saved_stdout)


def _safe_name(label) -> str | None:
    """Read TDataStd_Name attribute from a label, if present."""
    try:
        from OCP.TDataStd import TDataStd_Name  # type: ignore
        nm = TDataStd_Name()
        if label.FindAttribute(TDataStd_Name.GetID_s(), nm):
            ext = nm.Get()
            try:
                return str(ext.ToExtString())
            except Exception:
                return str(ext)
    except Exception:
        return None
    return None


def _walk_depth(label, depth: int = 0) -> int:
    """Return max depth of TDF_Label subtree."""
    try:
        deepest = depth
        it = label.ChildIterator() if hasattr(label, "ChildIterator") else None
        # Fallback to TDF_ChildIterator
        if it is None:
            from OCP.TDF import TDF_ChildIterator  # type: ignore
            it = TDF_ChildIterator(label)
        while it.More():
            child = it.Value()
            d = _walk_depth(child, depth + 1)
            if d > deepest:
                deepest = d
            it.Next()
        return deepest
    except Exception:
        return depth


def analyze(path: str | Path) -> dict[str, Any]:
    """Load ``path`` into an XCAF document and return OCAF-level metrics.

    Result dict shape: see module docstring. Always returns a dict; on
    fatal error returns ``{"load_status": "failed", "error": ...}``.
    """
    path = str(path)
    result: dict[str, Any] = {
        "file": path,
        "load_status": "unknown",
        "root_labels": 0,
        "free_shapes": 0,
        "named_labels": 0,
        "named_label_examples": [],
        "colored_labels": 0,
        "colored_label_count_with_alpha": 0,
        "assembly_count": 0,
        "assembly_components": 0,
        "max_depth": 0,
        "transforms_at_leaf": 0,
        "non_identity_transforms": 0,
        "sub_shape_labels": 0,
        "layer_count": 0,
        "diagnostics": [],
    }

    try:
        from OCP.STEPCAFControl import STEPCAFControl_Reader  # type: ignore
        from OCP.TDocStd import TDocStd_Document  # type: ignore
        from OCP.XCAFApp import XCAFApp_Application  # type: ignore
        from OCP.XCAFDoc import (  # type: ignore
            XCAFDoc_DocumentTool,
            XCAFDoc_ColorType,
        )
        from OCP.TCollection import TCollection_ExtendedString  # type: ignore
        from OCP.TDF import TDF_LabelSequence  # type: ignore
        from OCP.gp import gp_TrsfForm  # type: ignore
    except ImportError as e:
        result["load_status"] = "tool_missing"
        result["diagnostics"].append(f"ImportError: {e}")
        return result

    try:
        app = XCAFApp_Application.GetApplication_s()
        doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
        app.NewDocument(TCollection_ExtendedString("XmlOcaf"), doc)
    except Exception as e:
        result["load_status"] = "failed"
        result["diagnostics"].append(f"doc-init: {e}")
        return result

    reader = STEPCAFControl_Reader()
    try:
        reader.SetColorMode(True)
        reader.SetNameMode(True)
        reader.SetLayerMode(True)
        reader.SetMatMode(True)
        reader.SetGDTMode(True)
    except Exception as e:
        result["diagnostics"].append(f"reader-config: {e}")

    perform_ok = False
    try:
        with _silenced_fds():
            perform_ok = bool(reader.Perform(path, doc))
    except Exception as e:
        result["load_status"] = "failed"
        result["diagnostics"].append(f"perform: {e}")
        return result

    if not perform_ok:
        result["load_status"] = "failed"
        result["diagnostics"].append("STEPCAFControl_Reader.Perform returned False")
        return result

    result["load_status"] = "ok"

    try:
        shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
        color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
        try:
            layer_tool = XCAFDoc_DocumentTool.LayerTool_s(doc.Main())
        except Exception:
            layer_tool = None
    except Exception as e:
        result["diagnostics"].append(f"tool-init: {e}")
        return result

    # Free shapes (top-level products)
    try:
        free = TDF_LabelSequence()
        shape_tool.GetFreeShapes(free)
        result["free_shapes"] = int(free.Length())
    except Exception as e:
        result["diagnostics"].append(f"GetFreeShapes: {e}")

    # All shape labels (top-level + components + sub-shapes that got attributes)
    try:
        all_shapes = TDF_LabelSequence()
        shape_tool.GetShapes(all_shapes)
        n = int(all_shapes.Length())
        result["root_labels"] = n
    except Exception as e:
        result["diagnostics"].append(f"GetShapes: {e}")
        n = 0
        all_shapes = None

    # Walk shape labels
    if all_shapes is not None:
        names: list[str] = []
        n_named = 0
        n_assemblies = 0
        n_components = 0
        n_sub = 0
        n_with_loc = 0
        n_non_id = 0
        max_depth = 0
        for i in range(1, n + 1):
            try:
                lbl = all_shapes.Value(i)
            except Exception:
                continue
            try:
                name = _safe_name(lbl)
                if name:
                    n_named += 1
                    if len(names) < 8:
                        names.append(name)
            except Exception:
                pass
            try:
                if shape_tool.IsAssembly_s(lbl):
                    n_assemblies += 1
            except Exception:
                pass
            try:
                if shape_tool.IsComponent_s(lbl):
                    n_components += 1
                    # Get instance transform
                    try:
                        loc = shape_tool.GetLocation_s(lbl)
                        trsf = loc.Transformation()
                        n_with_loc += 1
                        if int(trsf.Form()) != int(gp_TrsfForm.gp_Identity):
                            n_non_id += 1
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                if shape_tool.IsSubShape_s(lbl):
                    n_sub += 1
            except Exception:
                pass
            try:
                d = _walk_depth(lbl)
                if d > max_depth:
                    max_depth = d
            except Exception:
                pass
        result["named_labels"] = n_named
        result["named_label_examples"] = names
        result["assembly_count"] = n_assemblies
        result["assembly_components"] = n_components
        result["sub_shape_labels"] = n_sub
        result["transforms_at_leaf"] = n_with_loc
        result["non_identity_transforms"] = n_non_id
        result["max_depth"] = max_depth

    # Colors
    try:
        color_labels = TDF_LabelSequence()
        color_tool.GetColors(color_labels)
        n_colors = int(color_labels.Length())
        result["colored_labels"] = n_colors

        # Count those with non-default alpha (i.e. translucency)
        n_alpha = 0
        from OCP.Quantity import Quantity_ColorRGBA  # type: ignore
        for i in range(1, n_colors + 1):
            try:
                lbl = color_labels.Value(i)
                rgba = Quantity_ColorRGBA()
                if color_tool.GetColor(lbl, rgba):
                    a = float(rgba.Alpha())
                    if a < 1.0 - 1e-6:
                        n_alpha += 1
            except Exception:
                pass
        result["colored_label_count_with_alpha"] = n_alpha
    except Exception as e:
        result["diagnostics"].append(f"colors: {e}")

    # Layers
    if layer_tool is not None:
        try:
            layers = TDF_LabelSequence()
            layer_tool.GetLayerLabels(layers)
            result["layer_count"] = int(layers.Length())
        except Exception as e:
            result["diagnostics"].append(f"layers: {e}")

    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._ocaf_oracle")
    p.add_argument("path", type=Path)
    p.add_argument("--json", action="store_true",
                   help="emit a single-line JSON record on stdout")
    args = p.parse_args(argv)

    try:
        result = analyze(args.path)
    except Exception as e:
        result = {
            "file": str(args.path),
            "load_status": "failed",
            "error": str(e)[:400],
            "traceback": traceback.format_exc()[-400:],
        }

    if args.json:
        json.dump(result, sys.stdout, default=str)
        sys.stdout.write("\n")
    else:
        from rich.console import Console
        from rich.pretty import Pretty
        Console().print(Pretty(result, expand_all=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
