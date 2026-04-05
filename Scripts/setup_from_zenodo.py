"""
Restore pkl files from the Zenodo zip so the notebooks can run as-is.

Usage:
    python Scripts/setup_from_zenodo.py [path/to/FeMo_TCP_dataset.zip]

If no path is given, the script looks for FeMo_TCP_dataset.zip in zenodo_upload/
inside the repository root.

What it does:
  1. Extracts BOP pkl files directly to their repo locations.
  2. Converts each JSON file back to a .pkl file in the same directory:
     - Plain DataFrames: read with pd.read_json(orient='split') → to_pickle
     - AtomsObjects DataFrames: reconstruct ASE Atoms objects from JSON → to_pickle
     - inchulldft BriefSummary: save as .pkl.gz (gzip-compressed) as expected by notebooks
"""

import sys
import types
import json
import zipfile
import gzip
import pickle
from pathlib import Path

import numpy

# ---------------------------------------------------------------------------
# numpy 2.x -> 1.x compatibility shim
# pkl files were saved with numpy 2.x which uses numpy._core instead of
# numpy.core. Only apply the shim when running under numpy 1.x; numpy 2.x
# already has numpy._core as a real module and does not need the shim.
# ---------------------------------------------------------------------------
if tuple(int(x) for x in numpy.__version__.split(".")[:2]) < (2, 0):
    _core_mod = types.ModuleType("numpy._core")
    for _attr in ("numeric", "multiarray", "fromnumeric", "umath", "shape_base",
                  "function_base", "arrayprint", "defchararray", "records",
                  "memmap", "einsumfunc", "overrides"):
        if hasattr(numpy.core, _attr):
            setattr(_core_mod, _attr, getattr(numpy.core, _attr))
            sys.modules[f"numpy._core.{_attr}"] = getattr(numpy.core, _attr)
    sys.modules["numpy._core"] = _core_mod

import pandas as pd
from ase.io.jsonio import decode as ase_decode


REPO_ROOT = Path(__file__).resolve().parent.parent

# Map: zip_path_in_archive -> (output_pkl_path_relative_to_repo, kind)
# kind: "df"        plain DataFrame (to_pickle)
#       "df_gz"     plain DataFrame (gzip pickle, for inchulldft)
#       "atoms"     AtomsObjects DataFrame with ASE Atoms column
JSON_FILES = {
    "Fe-Mo/FullyCuratedParsedBriefSummary.json": (
        "Fe-Mo/FullyCuratedParsedBriefSummary.pkl", "df"),
    "Fe-Mo/validation_data/BriefSummary.json": (
        "Fe-Mo/validation_data/BriefSummary.pkl", "df"),
    "Fe-Mo/validation_data/ParsedBriefsummary.json": (
        "Fe-Mo/validation_data/ParsedBriefsummary.pkl", "df"),
    "Fe-Mo/inchulldft/inchulldft_BriefSummary.json": (
        "Fe-Mo/inchulldft/BriefSummary.pkl.gz", "df_gz"),
    "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.json": (
        "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.pkl", "atoms"),
    "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.json": (
        "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.pkl", "atoms"),
    "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-initial.json": (
        "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-initial.pkl", "df"),
    "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-relaxed-all.json": (
        "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-relaxed-all.pkl", "df"),
}


def _json_to_df(json_bytes: bytes) -> pd.DataFrame:
    import io
    text = json_bytes.decode()
    # Series serialized with orient='split' include a 'name' key; DataFrames do not
    data = json.loads(text)
    typ = "series" if "name" in data else "frame"
    return pd.read_json(io.StringIO(text), orient="split", typ=typ)


def _json_to_atomsdf(json_bytes: bytes) -> pd.DataFrame:
    records = json.loads(json_bytes.decode())
    rows = []
    for rec in records:
        atoms = ase_decode(json.dumps(rec["atoms"]))
        rows.append({"index": rec["index"], "file": rec.get("file", ""), "atoms": atoms})
    df = pd.DataFrame(rows).set_index("index")
    df.index.name = None
    return df


def main(zip_path: Path):
    if not zip_path.exists():
        print(f"ERROR: zip not found: {zip_path}")
        sys.exit(1)

    print(f"Reading {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        names_in_zip = set(zf.namelist())

        # --- JSON → pkl ---
        for zip_name, (rel_out, kind) in JSON_FILES.items():
            if zip_name not in names_in_zip:
                print(f"  ! MISSING in zip: {zip_name}")
                continue

            out_path = REPO_ROOT / rel_out
            out_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"  {zip_name} -> {rel_out} ...")
            json_bytes = zf.read(zip_name)

            if kind == "atoms":
                df = _json_to_atomsdf(json_bytes)
                df.to_pickle(out_path)
            elif kind == "df_gz":
                df = _json_to_df(json_bytes)
                with gzip.open(out_path, "wb") as fh:
                    pickle.dump(df, fh)
            else:
                df = _json_to_df(json_bytes)
                df.to_pickle(out_path)

            print(f"    OK ({len(df)} rows)")

        # --- BOP pkl → extract directly ---
        # Also handles all other non-JSON files in the zip (CSVs, pkls)
        direct_entries = [n for n in names_in_zip if not n.endswith(".json")]
        for zip_name in sorted(direct_entries):
            out_path = REPO_ROOT / zip_name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if out_path.exists():
                print(f"  (skip, exists) {zip_name}")
                continue
            print(f"  Extracting {zip_name} ...")
            data = zf.read(zip_name)
            out_path.write_bytes(data)
            size_mb = len(data) / 1024 / 1024
            print(f"    OK ({size_mb:.1f} MB)")

    print("\nDone. All files restored to their repository locations.")
    _precompile_dscribe()


def _precompile_dscribe():
    """Pre-compile dscribe so its .pyc files are clean before the Jupyter kernel first sees them.

    IPython 8.x escalates SyntaxWarning to SyntaxError during cell execution when
    dscribe's source files are compiled on-the-fly (they contain LaTeX escape sequences
    such as ``\\lvert`` and ``\\eta`` in docstrings).  Importing SOAP here, outside the
    kernel, with the warning suppressed creates valid .pyc files that the kernel reuses.
    """
    import warnings
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            from dscribe.descriptors import SOAP  # noqa: F401 — compiles all dscribe .pyc files
        print("dscribe pre-compiled OK")
    except Exception as exc:
        print(f"  (dscribe not available or pre-compile failed: {exc})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        zip_path = Path(sys.argv[1])
    else:
        zip_path = REPO_ROOT / "zenodo_upload" / "FeMo_TCP_dataset.zip"
    main(zip_path)
