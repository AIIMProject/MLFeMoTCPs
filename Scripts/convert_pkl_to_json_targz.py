"""
Convert curated DFT data and Atoms objects pkl files to JSON, then package everything
(JSON files + BOP pkl files) into a single zip archive that preserves the repository
directory structure, ready for upload to Zenodo.

Usage:
    python Scripts/convert_pkl_to_json_targz.py

Output:
    zenodo_upload/FeMo_TCP_dataset.zip  single archive for Zenodo upload
"""

import sys
import types
import pickle
import json
import zipfile
from pathlib import Path

import numpy

# ---------------------------------------------------------------------------
# numpy 2.x -> 1.x compatibility shim (pkl files were saved with numpy 2.x)
# Only needed under numpy 1.x; numpy 2.x already has numpy._core natively.
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
from ase.io.jsonio import encode as ase_encode  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "zenodo_upload"
OUTPUT_DIR.mkdir(exist_ok=True)


def df_to_json_bytes(df: pd.DataFrame) -> bytes:
    """Serialise a plain DataFrame (no ASE objects) to JSON bytes."""
    return df.to_json(orient="split", indent=2, default_handler=str).encode()


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        if isinstance(obj, (numpy.integer,)):
            return int(obj)
        if isinstance(obj, (numpy.floating,)):
            return float(obj)
        return super().default(obj)


def atomsdf_to_json_bytes(df: pd.DataFrame) -> bytes:
    """Serialise a DataFrame whose 'atoms' column contains ASE Atoms objects."""
    records = []
    for idx, row in df.iterrows():
        record = {"index": idx, "file": row.get("file", "")}
        record["atoms"] = json.loads(ase_encode(row["atoms"]))
        records.append(record)
    return json.dumps(records, indent=2, cls=_NumpyEncoder).encode()


FILES = [
    {
        "pkl": "Fe-Mo/FullyCuratedParsedBriefSummary.pkl",
        "zip_path": "Fe-Mo/FullyCuratedParsedBriefSummary.json",
        "atoms": False,
    },
    {
        "pkl": "Fe-Mo/validation_data/ValidationFullyCuratedParsedBriefSummary.pkl",
        "zip_path": "Fe-Mo/validation_data/ValidationFullyCuratedParsedBriefSummary.json",
        "atoms": False,
    },
    {
        "pkl": "Fe-Mo/inchulldft/BriefSummary.pkl.gz",
        "zip_path": "Fe-Mo/inchulldft/inchulldft_BriefSummary.json",
        "atoms": False,
        "gzipped": True,
    },
    {
        "pkl": "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.pkl",
        "zip_path": "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.json",
        "atoms": True,
    },
    {
        "pkl": "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.pkl",
        "zip_path": "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.json",
        "atoms": True,
    },
    {
        "pkl": "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-initial.pkl",
        "zip_path": "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-initial.json",
        "atoms": False,
    },
    {
        "pkl": "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-relaxed-all.pkl",
        "zip_path": "Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-relaxed-all.json",
        "atoms": False,
    },
]

# BOP descriptor pkl files added directly to the zip (no conversion needed)
BOP_PKLS = [
    "Fe-Mo/Descriptors/parallel_Fe-Mo_initial_0.7projections_0.5os_table_WUBIND_20.pkl",
    "Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_0.7projections_0.5os_table_WUBIND_20.pkl",
    "Fe-Mo/Descriptors/PREDICTION_Fe-Mo_R_0.7dprojections_0.5os_table_WUBIND_16.pkl",
    "Fe-Mo/Descriptors/PREDICTION_Fe-Mo_M_0.7dprojections_0.5os_table_WUBIND_16.pkl",
    "Fe-Mo/Descriptors/PREDICTION_Fe-Mo_P_0.7dprojections_0.5os_table_WUBIND_16.pkl",
    "Fe-Mo/Descriptors/PREDICTION_Fe-Mo_delta_0.7dprojections_0.5os_table_WUBIND_16.pkl",
]


def main():
    import gzip as _gzip

    zip_path = OUTPUT_DIR / "FeMo_TCP_dataset.zip"
    print(f"Building {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:

        # JSON files converted from pkl
        for entry in FILES:
            pkl_path = REPO_ROOT / entry["pkl"]
            print(f"  Converting {pkl_path.name} ...")
            opener = _gzip.open if entry.get("gzipped") else open
            with opener(pkl_path, "rb") as fh:
                df = pickle.load(fh)

            if entry["atoms"]:
                json_bytes = atomsdf_to_json_bytes(df)
            else:
                json_bytes = df_to_json_bytes(df)

            zf.writestr(entry["zip_path"], json_bytes)
            size_kb = len(json_bytes) / 1024
            print(f"    + {entry['zip_path']}  ({size_kb:.0f} kB uncompressed)")

        # BOP pkl files stored as-is (already dense binary; compression gives minimal benefit)
        for rel_path in BOP_PKLS:
            src = REPO_ROOT / rel_path
            if src.exists():
                zf.write(src, arcname=rel_path, compress_type=zipfile.ZIP_STORED)
                size_mb = src.stat().st_size / 1024 / 1024
                print(f"  + {rel_path}  ({size_mb:.0f} MB)")
            else:
                print(f"  ! MISSING: {rel_path}")

    total_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"\nDone. {zip_path.name}: {total_mb:.1f} MB")


if __name__ == "__main__":
    main()
