"""
Convert curated DFT data and Atoms objects pkl files to json.tar.gz for Zenodo upload.

Usage:
    python Scripts/convert_pkl_to_json_targz.py

Output files are written to zenodo_upload/ at the repository root.
"""

import sys
import types
import pickle
import json
import tarfile
import io
from pathlib import Path

import numpy

# ---------------------------------------------------------------------------
# numpy 2.x -> 1.x compatibility shim (pkl files were saved with numpy 2.x)
# ---------------------------------------------------------------------------
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


def make_targz(json_bytes: bytes, json_filename: str, output_path: Path) -> None:
    """Wrap json_bytes in a tar.gz archive at output_path."""
    buf = io.BytesIO(json_bytes)
    buf.seek(0)
    with tarfile.open(output_path, "w:gz") as tar:
        info = tarfile.TarInfo(name=json_filename)
        info.size = len(json_bytes)
        tar.addfile(info, buf)
    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"  -> {output_path.name}  ({size_mb:.2f} MB)")


FILES = [
    {
        "pkl": "Fe-Mo/FullyCuratedParsedBriefSummary.pkl",
        "json_name": "FullyCuratedParsedBriefSummary.json",
        "out": "FullyCuratedParsedBriefSummary.json.tar.gz",
        "atoms": False,
    },
    {
        "pkl": "Fe-Mo/validation_data/ValidationFullyCuratedParsedBriefSummary.pkl",
        "json_name": "ValidationFullyCuratedParsedBriefSummary.json",
        "out": "ValidationFullyCuratedParsedBriefSummary.json.tar.gz",
        "atoms": False,
    },
    {
        "pkl": "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.pkl",
        "json_name": "Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.json",
        "out": "Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.json.tar.gz",
        "atoms": True,
    },
    {
        "pkl": "Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.pkl",
        "json_name": "Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.json",
        "out": "Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.json.tar.gz",
        "atoms": True,
    },
]


def main():
    for entry in FILES:
        pkl_path = REPO_ROOT / entry["pkl"]
        out_path = OUTPUT_DIR / entry["out"]

        print(f"Processing {pkl_path.name} ...")
        with open(pkl_path, "rb") as fh:
            df = pickle.load(fh)

        if entry["atoms"]:
            json_bytes = atomsdf_to_json_bytes(df)
        else:
            json_bytes = df_to_json_bytes(df)

        make_targz(json_bytes, entry["json_name"], out_path)

    print(f"\nAll files written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
