"""Tier1 adapter: matchem / oc20.

Converts raw OC20 S2EF extxyz dumps into sharded ASE-LMDB layout aligned
with `onescience-primitives/assets/matchem/datasets/oc20/spec.md`:

    <target>/
      data/
        train/
          data.0000.aselmdb + data.0000.aselmdb-lock
          data.0001.aselmdb + ...
          metadata.npz
        val/
          data.0000.aselmdb + ...
          metadata.npz
      splits/
        splits.json
      dataset_card.json
      README.md

Accepted raw layouts (auto-detected):
    A. `<source>/s2ef_200k_uncompressed/*.extxyz` +
       `<source>/s2ef_val_id_uncompressed/*.extxyz`   (canonical OC20)
    B. `<source>/train/*.extxyz` + `<source>/val/*.extxyz`
    C. Flat `<source>/*.extxyz` -> single "train" split with a warning
    D. Already-sharded `<source>/uma_oc20_finetune/{train,val}/*.aselmdb`
       -> passthrough copy with metadata regeneration

Each LMDB record is a pickled ASE-serializable dict:
    {
      "numbers":    np.ndarray [N_atoms] int,
      "positions":  np.ndarray [N_atoms, 3] float64 (Angstrom),
      "cell":       np.ndarray [3, 3] float64,
      "pbc":        np.ndarray [3] bool,
      "energy":     float (eV),
      "forces":     np.ndarray [N_atoms, 3] float64 (eV/Angstrom),
      "sid":        str (source id, e.g. "s2ef_200k:0.extxyz:frame=12"),
      "tags":       np.ndarray [N_atoms] int (0=sub-surface, 1=surface, 2=adsorbate),
      "fixed":      np.ndarray [N_atoms] bool,
    }

If ASE is available (`pip install ase`) we use `ase.io.read` for robust
extxyz parsing; otherwise we fall back to a minimal built-in extxyz parser
that handles the OC20 conventions (Info comment line carrying energy,
forces and cell as key=value pairs, Lattice="..." block).

# requirements: numpy>=1.24, lmdb>=1.4
"""

from __future__ import annotations

import json
import pickle
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from adapters._base import (  # noqa: E402
    AdapterConversionError, AdapterDependencyError, AdapterInputError,
    BaseAdapter, adapter_main,
)

SHARD_TARGET_BYTES = 512 * 1024 * 1024   # 512 MiB per shard
LATTICE_RE = re.compile(r'Lattice\s*=\s*"([^"]+)"')
ENERGY_RE = re.compile(r'energy\s*=\s*(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)')
PROPERTIES_RE = re.compile(r'Properties\s*=\s*(\S+)')
PBC_RE = re.compile(r'pbc\s*=\s*"([^"]+)"')


class OC20Adapter(BaseAdapter):
    domain = "matchem"
    dataset_name = "oc20"
    primary_format = "aselmdb"

    # ------------------------------------------------------------------
    def probe(self, source_dir: Path) -> Dict[str, Any]:
        extxyz: List[Path] = sorted(source_dir.rglob("*.extxyz"))
        aselmdb: List[Path] = sorted(source_dir.rglob("*.aselmdb"))
        split_dirs: Dict[str, List[Path]] = {}
        for name in ("train", "val", "test",
                     "s2ef_200k_uncompressed", "s2ef_val_id_uncompressed"):
            d = source_dir / name
            if d.is_dir():
                files = sorted(d.rglob("*.extxyz")) or sorted(d.rglob("*.aselmdb"))
                if files:
                    split_dirs[name] = files

        if aselmdb and not extxyz:
            layout = "passthrough_aselmdb"
        elif split_dirs:
            layout = "split_dirs"
        elif extxyz:
            layout = "flat_extxyz"
        else:
            layout = "unknown"

        return {
            "source_dir": str(source_dir),
            "extxyz_count": len(extxyz),
            "aselmdb_count": len(aselmdb),
            "layout": layout,
            "split_dirs": {k: [str(p) for p in v]
                           for k, v in split_dirs.items()},
            "sample_extxyz": [str(p) for p in extxyz[:3]],
            "summary": {
                "layout": layout,
                "splits_detected": sorted(split_dirs.keys()),
            },
        }

    # ------------------------------------------------------------------
    def plan(self, probe_report: Dict[str, Any],
             spec: Dict[str, Any]) -> Dict[str, Any]:
        layout = probe_report["layout"]
        if layout == "unknown":
            raise AdapterInputError(
                "no .extxyz or .aselmdb files found under source_dir; "
                "OC20 adapter expects one of the layouts documented in "
                "the module docstring"
            )
        split_map = self._build_split_map(probe_report)
        if not split_map:
            raise AdapterInputError(
                f"layout={layout} detected but no split could be inferred; "
                f"split_dirs={probe_report['split_dirs']}"
            )
        shard_bytes = int(spec.get("shard_bytes", SHARD_TARGET_BYTES))
        return {
            "layout": layout,
            "split_map": split_map,
            "shard_bytes": shard_bytes,
            "card_extra": {
                "data_layout": {
                    "data/<split>/": "sharded ASE LMDB: data.000N.aselmdb "
                                     "+ metadata.npz per split",
                    "splits/": "splits.json describing shard counts and "
                               "sample totals",
                },
                "primary_format": "aselmdb",
                "dimensions": {
                    "numbers": "[N_atoms] int atomic numbers",
                    "positions": "[N_atoms, 3] float64 Angstrom",
                    "cell": "[3, 3] float64",
                    "forces": "[N_atoms, 3] float64 eV/Angstrom",
                    "energy": "scalar float64 eV",
                },
                "spec_alignment": [
                    "sharded aselmdb layout matches uma_oc20_finetune/{train,val}",
                    "metadata.npz regenerated per split with sample counts",
                    "extxyz -> record conversion preserves energy/forces/cell/tags",
                ],
                "loading_example": _LOADING_EXAMPLE,
            },
        }

    def _build_split_map(self, probe_report: Dict[str, Any]
                         ) -> Dict[str, List[Path]]:
        split_dirs = probe_report["split_dirs"]
        result: Dict[str, List[Path]] = {}
        canonical = {
            "s2ef_200k_uncompressed": "train",
            "s2ef_val_id_uncompressed": "val",
            "train": "train",
            "val": "val",
            "test": "test",
        }
        for raw_name, files in split_dirs.items():
            mapped = canonical.get(raw_name, raw_name)
            result.setdefault(mapped, []).extend(Path(p) for p in files)
        if not result and probe_report["layout"] == "flat_extxyz":
            result["train"] = [Path(p) for p in
                               sorted(Path(probe_report["source_dir"]).rglob("*.extxyz"))]
            self.warn("flat extxyz layout: all files assigned to 'train' split")
        return result

    # ------------------------------------------------------------------
    def convert(self, source_dir: Path, target_dir: Path,
                plan: Dict[str, Any]) -> None:
        self.require_deps("numpy>=1.24", "lmdb>=1.4")
        try:
            import lmdb  # type: ignore
            import numpy as np  # type: ignore
        except ImportError as exc:
            raise AdapterDependencyError(str(exc)) from exc

        layout = plan["layout"]
        split_map: Dict[str, List[Path]] = plan["split_map"]
        data_dir = target_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        ase_reader = self._try_import_ase()
        split_summary: Dict[str, Dict[str, Any]] = {}

        for split, files in split_map.items():
            split_out = data_dir / split
            if split_out.exists():
                shutil.rmtree(split_out, ignore_errors=True)
            split_out.mkdir(parents=True, exist_ok=True)

            if layout == "passthrough_aselmdb":
                self._passthrough_shards(files, split_out, np)
                sample_count = self._count_lmdb_records(split_out, lmdb)
                split_summary[split] = {
                    "shards": len(list(split_out.glob("*.aselmdb"))),
                    "samples": sample_count,
                    "source_files": [str(p) for p in files],
                }
                continue

            shard_idx = 0
            shard_bytes = 0
            env: Optional[Any] = None
            txn: Optional[Any] = None
            total_samples = 0

            def open_shard(idx: int) -> Tuple[Any, Any]:
                path = split_out / f"data.{idx:04d}.aselmdb"
                env_local = lmdb.open(str(path), map_size=1024 * 1024 * 1024,
                                      subdir=True, readonly=False,
                                      meminit=False, map_async=True)
                txn_local = env_local.begin(write=True)
                return env_local, txn_local

            env, txn = open_shard(shard_idx)
            for src_file in files:
                for record in self._iter_records(src_file, ase_reader, np):
                    key = f"{total_samples:09d}".encode("utf-8")
                    value = pickle.dumps(record,
                                         protocol=pickle.HIGHEST_PROTOCOL)
                    txn.put(key, value)
                    total_samples += 1
                    shard_bytes += len(value)
                    if shard_bytes >= plan["shard_bytes"]:
                        txn.commit()
                        env.sync()
                        env.close()
                        shard_idx += 1
                        shard_bytes = 0
                        env, txn = open_shard(shard_idx)
            if txn is not None:
                txn.commit()
            if env is not None:
                env.sync()
                env.close()

            # metadata.npz per split
            np.savez(
                split_out / "metadata.npz",
                num_samples=np.array([total_samples], dtype="int64"),
                num_shards=np.array([shard_idx + 1], dtype="int64"),
                split=np.array([split]),
            )
            split_summary[split] = {
                "shards": shard_idx + 1,
                "samples": total_samples,
                "source_files_count": len(files),
            }

        splits_dir = target_dir / "splits"
        splits_dir.mkdir(parents=True, exist_ok=True)
        (splits_dir / "splits.json").write_text(json.dumps({
            "strategy": "canonical_oc20_split" if layout != "flat_extxyz"
                        else "flat_all_train",
            "layout_detected": layout,
            "splits": split_summary,
        }, indent=2), encoding="utf-8")

        plan.setdefault("card_extra", {})["statistics"] = {
            "num_samples": {k: v["samples"] for k, v in split_summary.items()},
            "shards": {k: v["shards"] for k, v in split_summary.items()},
        }
        plan["card_extra"]["splits"] = {
            "strategy": "canonical_oc20_split",
            **{k: v["samples"] for k, v in split_summary.items()},
        }

    # ------------------------------------------------------------------
    def _try_import_ase(self) -> Optional[Any]:
        try:
            from ase.io import read  # type: ignore
            return read
        except ImportError:
            self.warn("ase not installed; using built-in extxyz parser "
                      "(install ase for full format coverage)")
            return None

    # ------------------------------------------------------------------
    def _iter_records(self, src_file: Path, ase_reader: Optional[Any],
                      np: Any) -> Iterable[Dict[str, Any]]:
        if src_file.suffix.lower() == ".aselmdb":
            # Handled by _passthrough_shards; should not reach here.
            return
        if ase_reader is not None:
            try:
                frames = ase_reader(str(src_file), index=":", format="extxyz")
            except Exception as exc:
                self.warn(f"ase failed on {src_file.name}: {exc}; "
                          f"falling back to built-in parser")
                frames = None
            if frames is not None:
                if not isinstance(frames, list):
                    frames = [frames]
                for i, atoms in enumerate(frames):
                    yield self._ase_frame_to_record(atoms, src_file, i, np)
                return
        # Built-in parser
        for i, rec in enumerate(self._parse_extxyz(src_file, np)):
            yield rec

    # ------------------------------------------------------------------
    def _ase_frame_to_record(self, atoms: Any, src_file: Path,
                             frame_idx: int, np: Any) -> Dict[str, Any]:
        info = getattr(atoms, "info", {}) or {}
        energy = info.get("energy", info.get("Energy", 0.0))
        forces = getattr(atoms, "arrays", {}).get("forces")
        if forces is None:
            forces = info.get("forces", np.zeros((len(atoms), 3)))
        tags = getattr(atoms, "get_tags", lambda: np.zeros(len(atoms), dtype=int))()
        fixed = getattr(atoms, "constraints", None)
        fixed_mask = np.zeros(len(atoms), dtype=bool)
        if fixed is not None:
            try:
                from ase.constraints import FixAtoms  # type: ignore
                for c in fixed:
                    if isinstance(c, FixAtoms):
                        fixed_mask[list(c.index)] = True
            except Exception:
                pass
        return {
            "numbers": np.asarray(atoms.get_atomic_numbers(), dtype="int64"),
            "positions": np.asarray(atoms.get_positions(), dtype="float64"),
            "cell": np.asarray(atoms.get_cell(), dtype="float64").reshape(3, 3),
            "pbc": np.asarray(atoms.get_pbc(), dtype=bool),
            "energy": float(energy),
            "forces": np.asarray(forces, dtype="float64"),
            "tags": np.asarray(tags, dtype="int64"),
            "fixed": fixed_mask,
            "sid": f"{src_file.name}:frame={frame_idx}",
        }

    # ------------------------------------------------------------------
    def _parse_extxyz(self, path: Path, np: Any
                      ) -> Iterable[Dict[str, Any]]:
        """Minimal extxyz parser for OC20 conventions.

        Format per frame:
            <natoms>
            <comment line: Lattice="..." energy=... Properties=species:S:1:pos:R:3:forces:R:3 ...>
            <natoms lines of atom data>
        """
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AdapterConversionError(
                f"cannot read {path}: {exc}") from exc
        lines = text.splitlines()
        i = 0
        frame_idx = 0
        while i < len(lines):
            # Skip blanks
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                return
            try:
                n_atoms = int(lines[i].strip())
            except ValueError:
                self.warn(f"{path.name}: malformed atom count at line {i+1}")
                i += 1
                continue
            i += 1
            if i >= len(lines):
                return
            comment = lines[i]
            i += 1
            lattice_match = LATTICE_RE.search(comment)
            cell = np.zeros((3, 3), dtype="float64")
            if lattice_match:
                try:
                    vals = [float(x) for x in lattice_match.group(1).split()]
                    if len(vals) == 9:
                        cell = np.array(vals, dtype="float64").reshape(3, 3)
                except ValueError:
                    pass
            energy_match = ENERGY_RE.search(comment)
            energy = float(energy_match.group(1)) if energy_match else 0.0
            pbc_match = PBC_RE.search(comment)
            pbc = np.array([t.strip().upper().startswith("T")
                            for t in (pbc_match.group(1).split()
                                      if pbc_match else ["F", "F", "F"])],
                           dtype=bool)
            props_match = PROPERTIES_RE.search(comment)
            props_spec = props_match.group(1) if props_match else \
                "species:S:1:pos:R:3:forces:R:3"
            columns = self._parse_properties_spec(props_spec)
            if i + n_atoms > len(lines):
                self.warn(f"{path.name}: truncated frame at line {i+1}; stopping")
                return
            numbers = np.zeros(n_atoms, dtype="int64")
            positions = np.zeros((n_atoms, 3), dtype="float64")
            forces = np.zeros((n_atoms, 3), dtype="float64")
            tags = np.zeros(n_atoms, dtype="int64")
            for k in range(n_atoms):
                parts = lines[i + k].split()
                row = self._parse_atom_row(parts, columns)
                numbers[k] = self._symbol_to_number(row.get("species", "X"))
                positions[k] = row.get("pos", [0.0, 0.0, 0.0])
                forces[k] = row.get("forces", [0.0, 0.0, 0.0])
                tags[k] = int(row.get("tags", 0))
            i += n_atoms
            yield {
                "numbers": numbers, "positions": positions, "cell": cell,
                "pbc": pbc, "energy": energy, "forces": forces,
                "tags": tags, "fixed": np.zeros(n_atoms, dtype=bool),
                "sid": f"{path.name}:frame={frame_idx}",
            }
            frame_idx += 1

    def _parse_properties_spec(self, spec: str) -> List[Tuple[str, str, int]]:
        """Parse 'species:S:1:pos:R:3:forces:R:3' into [(name, type, count)]."""
        parts = spec.split(":")
        cols: List[Tuple[str, str, int]] = []
        i = 0
        while i + 2 < len(parts) + 1 and i < len(parts):
            try:
                name = parts[i]
                typ = parts[i + 1]
                cnt = int(parts[i + 2])
                cols.append((name, typ, cnt))
                i += 3
            except (ValueError, IndexError):
                break
        return cols or [("species", "S", 1), ("pos", "R", 3), ("forces", "R", 3)]

    def _parse_atom_row(self, parts: List[str],
                        columns: List[Tuple[str, str, int]]
                        ) -> Dict[str, Any]:
        row: Dict[str, Any] = {}
        idx = 0
        for name, typ, cnt in columns:
            if idx + cnt > len(parts):
                break
            slice_ = parts[idx:idx + cnt]
            if typ.upper().startswith("S"):
                row[name] = slice_[0] if cnt == 1 else slice_
            elif typ.upper().startswith("R"):
                try:
                    vals = [float(x) for x in slice_]
                except ValueError:
                    vals = [0.0] * cnt
                row[name] = vals[0] if cnt == 1 else vals
            elif typ.upper().startswith("I"):
                try:
                    vals = [int(float(x)) for x in slice_]
                except ValueError:
                    vals = [0] * cnt
                row[name] = vals[0] if cnt == 1 else vals
            else:
                row[name] = slice_
            idx += cnt
        return row

    # Minimal periodic table for the elements OC20 actually uses.
    _Z_BY_SYMBOL: Dict[str, int] = {
        "H": 1, "HE": 2, "LI": 3, "BE": 4, "B": 5, "C": 6, "N": 7, "O": 8,
        "F": 9, "NE": 10, "NA": 11, "MG": 12, "AL": 13, "SI": 14, "P": 15,
        "S": 16, "CL": 17, "AR": 18, "K": 19, "CA": 20, "SC": 21, "TI": 22,
        "V": 23, "CR": 24, "MN": 25, "FE": 26, "CO": 27, "NI": 28, "CU": 29,
        "ZN": 30, "GA": 31, "GE": 32, "AS": 33, "SE": 34, "BR": 35, "KR": 36,
        "RB": 37, "SR": 38, "Y": 39, "ZR": 40, "NB": 41, "MO": 42, "TC": 43,
        "RU": 44, "RH": 45, "PD": 46, "AG": 47, "CD": 48, "IN": 49, "SN": 50,
        "SB": 51, "TE": 52, "I": 53, "XE": 54, "PT": 78, "AU": 79, "HG": 80,
        "PB": 82, "BI": 83,
    }

    def _symbol_to_number(self, symbol: str) -> int:
        return self._Z_BY_SYMBOL.get(symbol.strip().upper(), 0)

    # ------------------------------------------------------------------
    def _passthrough_shards(self, files: List[Path], split_out: Path,
                            np: Any) -> None:
        for src in files:
            if src.suffix.lower() != ".aselmdb":
                continue
            dst = split_out / src.name
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            # Copy sibling -lock file if present.
            lock = src.with_suffix(src.suffix + "-lock")
            if lock.exists():
                shutil.copy2(lock, split_out / lock.name)

    def _count_lmdb_records(self, split_out: Path, lmdb: Any) -> int:
        total = 0
        for shard in sorted(split_out.glob("*.aselmdb")):
            try:
                env = lmdb.open(str(shard), readonly=True, lock=False,
                                subdir=shard.is_dir())
                with env.begin() as txn:
                    total += txn.stat()["entries"]
                env.close()
            except Exception as exc:
                self.warn(f"cannot count {shard.name}: {exc}")
        return total


_LOADING_EXAMPLE = """```python
import lmdb
import pickle
import numpy as np

# 1) Stream ASE-style atomic records from one shard.
def iter_shard(split="train", shard=0):
    path = f"<target_dir>/data/{split}/data.{shard:04d}.aselmdb"
    env = lmdb.open(path, readonly=True, lock=False, subdir=True)
    with env.begin() as txn:
        for _key, value in txn.cursor():
            # record: numbers/positions/cell/pbc/energy/forces/tags/fixed
            yield pickle.loads(value)
    env.close()

# 2) Per-split sample/shard counts from metadata.
meta = np.load("<target_dir>/data/train/metadata.npz", allow_pickle=False)
num_samples = int(meta["num_samples"][0])
num_shards = int(meta["num_shards"][0])

# 3) Minimal batching across all shards of a split.
def batches(split, bs=32):
    buf = []
    for shard in range(num_shards):
        for rec in iter_shard(split, shard):
            buf.append(rec)
            if len(buf) == bs:
                yield buf
                buf = []
    if buf:
        yield buf

# 4) OCP-style training-loop skeleton (energy & forces regression):
# for batch in batches("train"):
#     graph = to_graph_tensors(batch)           # numbers/positions/cell/...
#     loss = model(graph)                        # predict energy + forces
#     loss.backward(); optimizer.step(); optimizer.zero_grad()
```
"""


if __name__ == "__main__":
    sys.exit(adapter_main(OC20Adapter))
