"""Tier1 adapter: bio / targetdiff.

Converts a raw TargetDiff-style pocket-ligand collection into an LMDB graph
cache aligned with `onescience-primitives/assets/bio/datasets/targetdiff`:

    <target>/
      data/
        train.lmdb / train.lmdb-lock
        val.lmdb   / val.lmdb-lock
        test.lmdb  / test.lmdb-lock
      splits/
        train.txt / val.txt / test.txt   (complex IDs per split)
        splits.json
      static/
        index.json                       (id -> source pdb/sdf paths)
      dataset_card.json
      README.md

Accepted raw layouts:
    A. Flat: <source>/<id>/<id>_pocket.pdb + <source>/<id>/<id>_ligand.sdf
    B. Nested: <source>/<id>/pocket.pdb + <source>/<id>/ligand.sdf(.mol2)
    C. Index-driven: <source>/index.pkl listing {id: (pocket_fn, ligand_fn)}

Each LMDB record is a pickled dict:
    {
      "id": str,
      "pocket_atoms": [{"element": str, "xyz": [x,y,z], ...}, ...],
      "ligand_atoms":   [{"element": str, "xyz": [x,y,z], ...}, ...],
      "ligand_bonds":   [[i, j, order], ...],
      "pocket_source": str,
      "ligand_source": str,
    }

Graph construction (bond perception, featurization) is intentionally left to
downstream datapipes; this adapter only guarantees a **stable, indexable,
random-access cache** of parsed atom/bond tables. That matches the TargetDiff
spec's "PocketLigandPairDataset with pocket_fn / ligand_fn as index" contract
without hard-coding a specific featurization.

# requirements: numpy>=1.24, lmdb>=1.4
"""

from __future__ import annotations

import json
import pickle
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from adapters._base import (  # noqa: E402
    AdapterConversionError, AdapterDependencyError, AdapterInputError,
    BaseAdapter, adapter_main,
)

PDB_SUFFIXES = (".pdb", ".ent")
LIGAND_SUFFIXES = (".sdf", ".mol", ".mol2")
SPLIT_RATIO_DEFAULT = (0.80, 0.10, 0.10)


class TargetDiffAdapter(BaseAdapter):
    domain = "bio"
    dataset_name = "targetdiff"
    primary_format = "lmdb"

    # ------------------------------------------------------------------
    def probe(self, source_dir: Path) -> Dict[str, Any]:
        pdbs: List[Path] = []
        ligands: List[Path] = []
        for p in sorted(source_dir.rglob("*")):
            if not p.is_file():
                continue
            suf = p.suffix.lower()
            if suf in PDB_SUFFIXES:
                pdbs.append(p)
            elif suf in LIGAND_SUFFIXES:
                ligands.append(p)
        index_pkl = next(iter(source_dir.rglob("index.pkl")), None)

        # Try to pair by parent directory name.
        pairs: Dict[str, Dict[str, Path]] = {}
        for p in pdbs:
            key = self._pair_key(p)
            pairs.setdefault(key, {})["pocket"] = p
        for l in ligands:
            key = self._pair_key(l)
            pairs.setdefault(key, {})["ligand"] = l
        complete = {k: v for k, v in pairs.items()
                    if "pocket" in v and "ligand" in v}
        incomplete = {k: v for k, v in pairs.items() if k not in complete}

        return {
            "source_dir": str(source_dir),
            "pdb_count": len(pdbs),
            "ligand_count": len(ligands),
            "index_pkl": str(index_pkl) if index_pkl else None,
            "pairs_complete": sorted(complete.keys()),
            "pairs_incomplete": sorted(incomplete.keys()),
            "sample_pair": {
                k: {kk: str(vv) for kk, vv in v.items()}
                for k, v in list(complete.items())[:3]
            },
            "summary": {
                "n_pairs": len(complete),
                "n_incomplete": len(incomplete),
                "index_driven": bool(index_pkl),
            },
        }

    def _pair_key(self, path: Path) -> str:
        """Derive a stable pairing key from a file path.

        Prefer parent-directory name; fall back to filename stem stripped of
        common suffixes like `_pocket`, `_ligand`, `_pocket10`.
        """
        parent = path.parent.name
        if parent and parent not in (".", path.name):
            # If the parent directory itself is the sample id, use it.
            # Guard against generic parents like "data" or "pockets".
            if parent.lower() not in ("data", "pockets", "ligands",
                                      "structures", "raw"):
                return parent
        stem = path.stem
        stem = re.sub(r"_(pocket\d*|ligand|pocket)$", "", stem,
                      flags=re.IGNORECASE)
        return stem

    # ------------------------------------------------------------------
    def plan(self, probe_report: Dict[str, Any],
             spec: Dict[str, Any]) -> Dict[str, Any]:
        n_pairs = probe_report["summary"]["n_pairs"]
        if n_pairs == 0:
            raise AdapterInputError(
                "no complete pocket+ligand pairs found under source_dir; "
                f"detected {probe_report['pdb_count']} PDB and "
                f"{probe_report['ligand_count']} ligand files but none paired"
            )
        ratios = tuple(spec.get("split_ratio", SPLIT_RATIO_DEFAULT))
        if len(ratios) != 3 or abs(sum(ratios) - 1.0) > 1e-6:
            self.warn(f"invalid split_ratio {ratios}; falling back to default")
            ratios = SPLIT_RATIO_DEFAULT
        seed = int(spec.get("seed", 42))
        return {
            "pairs": probe_report["pairs_complete"],
            "split_ratio": ratios,
            "seed": seed,
            "index_driven": probe_report["summary"]["index_driven"],
            "card_extra": {
                "data_layout": {
                    "data/": "LMDB per split; each record is a pickled dict "
                             "with pocket_atoms / ligand_atoms / ligand_bonds",
                    "splits/": "train.txt / val.txt / test.txt (complex IDs) "
                               "+ splits.json",
                    "static/": "index.json mapping id -> source file paths",
                },
                "primary_format": "lmdb",
                "dimensions": {
                    "id": "complex identifier (parent dir or file stem)",
                    "pocket_atoms": "list of atom dicts (element, xyz, name, resname)",
                    "ligand_atoms": "list of atom dicts (element, xyz)",
                    "ligand_bonds": "list of [i, j, order] triples",
                },
                "spec_alignment": [
                    "LMDB random-access cache matches targetdiff PocketLigandPairDataset",
                    "graph featurization deferred to downstream datapipe (no hard-coded features)",
                    "deterministic split with fixed seed",
                ],
                "loading_example": _LOADING_EXAMPLE,
            },
        }

    # ------------------------------------------------------------------
    def convert(self, source_dir: Path, target_dir: Path,
                plan: Dict[str, Any]) -> None:
        self.require_deps("numpy>=1.24", "lmdb>=1.4")
        try:
            import lmdb  # type: ignore
            import numpy as np  # type: ignore
        except ImportError as exc:
            raise AdapterDependencyError(str(exc)) from exc

        pairs: List[str] = list(plan["pairs"])
        rng = np.random.default_rng(plan["seed"])
        perm = rng.permutation(len(pairs))
        ratios = plan["split_ratio"]
        n = len(pairs)
        n_train = int(round(n * ratios[0]))
        n_val = int(round(n * ratios[1]))
        n_test = n - n_train - n_val

        # Small-dataset safeguard: guarantee at least 1 record per split
        # when n >= 3, so downstream training pipelines always see a
        # non-empty train/val/test. Only applies when rounding collapsed
        # a split to zero.
        if n >= 3:
            if n_val == 0 and n_train > 1:
                n_train -= 1
                n_val = 1
                n_test = n - n_train - n_val
            if n_test == 0 and n_train > 1:
                n_train -= 1
                n_test = 1
                n_val = n - n_train - n_test
            if n_val < 0:
                n_val = 0
            if n_test < 0:
                n_test = 0
            # Re-derive train from the remainder to keep the total == n.
            n_train = n - n_val - n_test

        splits: Dict[str, List[str]] = {
            "train": [pairs[i] for i in perm[:n_train]],
            "val": [pairs[i] for i in perm[n_train:n_train + n_val]],
            "test": [pairs[i] for i in perm[n_train + n_val:]],
        }
        # Drop genuinely empty splits (n < 3 cases) with a warning instead
        # of aborting — the dataset is still usable for train-only workflows.
        for empty_name in [k for k, v in splits.items() if not v]:
            if empty_name != "train":
                self.warn(
                    f"split '{empty_name}' is empty (n={n} too small for "
                    f"ratio {ratios}); skipping this split"
                )
                splits.pop(empty_name)

        data_dir = target_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        splits_dir = target_dir / "splits"
        splits_dir.mkdir(parents=True, exist_ok=True)
        static_dir = target_dir / "static"
        static_dir.mkdir(parents=True, exist_ok=True)

        index_map: Dict[str, Dict[str, str]] = {}
        map_size = 1024 * 1024 * 1024  # 1 GiB per LMDB env; grow on demand

        for split_name, ids in splits.items():
            lmdb_path = data_dir / f"{split_name}.lmdb"
            if lmdb_path.exists():
                # Remove stale env to avoid mixing old records.
                import shutil
                shutil.rmtree(lmdb_path, ignore_errors=True)
            env = lmdb.open(str(lmdb_path), map_size=map_size, subdir=True,
                            readonly=False, meminit=False, map_async=True)
            written = 0
            with env.begin(write=True) as txn:
                for cid in ids:
                    pocket_path, ligand_path = self._locate_pair(source_dir, cid)
                    if pocket_path is None or ligand_path is None:
                        self.warn(f"pair {cid} vanished during conversion; skipped")
                        continue
                    record = {
                        "id": cid,
                        "pocket_atoms": self._parse_pdb(pocket_path),
                        "ligand_atoms": [],
                        "ligand_bonds": [],
                        "pocket_source": str(pocket_path),
                        "ligand_source": str(ligand_path),
                    }
                    lig_atoms, lig_bonds = self._parse_ligand(ligand_path)
                    record["ligand_atoms"] = lig_atoms
                    record["ligand_bonds"] = lig_bonds
                    txn.put(cid.encode("utf-8"),
                            pickle.dumps(record, protocol=pickle.HIGHEST_PROTOCOL))
                    index_map[cid] = {
                        "pocket": str(pocket_path),
                        "ligand": str(ligand_path),
                        "split": split_name,
                    }
                    written += 1
            env.sync()
            env.close()
            if written == 0:
                # Only abort if TRAIN is empty — val/test emptiness is
                # acceptable for small datasets and already warned above.
                if split_name == "train":
                    raise AdapterConversionError(
                        f"split {split_name} produced 0 records; aborting"
                    )
                self.warn(
                    f"split '{split_name}' wrote 0 records; removing empty LMDB"
                )
                import shutil
                shutil.rmtree(lmdb_path, ignore_errors=True)
                continue
            (splits_dir / f"{split_name}.txt").write_text(
                "\n".join(ids) + "\n", encoding="utf-8")

        (splits_dir / "splits.json").write_text(json.dumps({
            "strategy": "random_permutation_fixed_seed",
            "seed": plan["seed"],
            "split_ratio": list(plan["split_ratio"]),
            "counts": {k: len(v) for k, v in splits.items()},
        }, indent=2), encoding="utf-8")
        (static_dir / "index.json").write_text(
            json.dumps(index_map, indent=2, ensure_ascii=False),
            encoding="utf-8")

        plan.setdefault("card_extra", {})["statistics"] = {
            "num_samples": {k: len(v) for k, v in splits.items()},
            "total_pairs": n,
        }
        plan["card_extra"]["splits"] = {
            "strategy": "random_permutation_fixed_seed",
            **{k: len(v) for k, v in splits.items()},
        }

    # ------------------------------------------------------------------
    def _locate_pair(self, source_dir: Path,
                     cid: str) -> Tuple[Optional[Path], Optional[Path]]:
        # Fast path: <source>/<cid>/<cid>_pocket.pdb + <cid>_ligand.sdf
        sub = source_dir / cid
        if sub.is_dir():
            pocket = next(
                (p for p in sub.iterdir()
                 if p.suffix.lower() in PDB_SUFFIXES), None)
            ligand = next(
                (p for p in sub.iterdir()
                 if p.suffix.lower() in LIGAND_SUFFIXES), None)
            if pocket and ligand:
                return pocket, ligand
        # Fallback: global search for matching stems.
        pocket = None
        ligand = None
        for p in source_dir.rglob("*"):
            if not p.is_file():
                continue
            stem_key = self._pair_key(p)
            if stem_key != cid:
                continue
            suf = p.suffix.lower()
            if suf in PDB_SUFFIXES and pocket is None:
                pocket = p
            elif suf in LIGAND_SUFFIXES and ligand is None:
                ligand = p
        return pocket, ligand

    # ------------------------------------------------------------------
    def _parse_pdb(self, path: Path) -> List[Dict[str, Any]]:
        """Minimal PDB ATOM/HETATM parser; no external deps required."""
        atoms: List[Dict[str, Any]] = []
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AdapterConversionError(f"cannot read {path}: {exc}") from exc
        for line in text.splitlines():
            rec = line[:6].strip()
            if rec not in ("ATOM", "HETATM"):
                continue
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue
            name = line[12:16].strip()
            resname = line[17:20].strip()
            chain = line[21:22].strip()
            resi = line[22:26].strip()
            element = line[76:78].strip() or self._guess_element(name)
            atoms.append({
                "name": name, "resname": resname, "chain": chain,
                "resi": resi, "element": element, "xyz": [x, y, z],
            })
        if not atoms:
            self.warn(f"{path.name}: no ATOM/HETATM records parsed")
        return atoms

    def _guess_element(self, atom_name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z]", "", atom_name)
        if not cleaned:
            return "X"
        if len(cleaned) >= 2 and cleaned[:2].upper() in (
                "CL", "BR", "NA", "MG", "CA", "FE", "ZN", "CU", "MN", "NI"):
            return cleaned[:2].upper()
        return cleaned[0].upper()

    # ------------------------------------------------------------------
    def _parse_ligand(self, path: Path
                      ) -> Tuple[List[Dict[str, Any]], List[List[int]]]:
        suf = path.suffix.lower()
        if suf in (".sdf", ".mol"):
            return self._parse_sdf(path)
        if suf == ".mol2":
            return self._parse_mol2(path)
        raise AdapterConversionError(
            f"unsupported ligand format: {path.name} (expected .sdf/.mol/.mol2)"
        )

    def _parse_sdf(self, path: Path
                   ) -> Tuple[List[Dict[str, Any]], List[List[int]]]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AdapterConversionError(f"cannot read {path}: {exc}") from exc
        lines = text.splitlines()
        # Find the counts line (usually line 4 of the first molecule block).
        counts_idx = None
        for i, line in enumerate(lines[:10]):
            if len(line) >= 6 and line[0:3].strip().isdigit() \
                    and line[3:6].strip().isdigit():
                counts_idx = i
                break
        if counts_idx is None:
            self.warn(f"{path.name}: cannot locate SDF counts line")
            return [], []
        try:
            n_atoms = int(lines[counts_idx][0:3])
            n_bonds = int(lines[counts_idx][3:6])
        except ValueError:
            self.warn(f"{path.name}: malformed counts line")
            return [], []
        atoms: List[Dict[str, Any]] = []
        for j in range(n_atoms):
            line = lines[counts_idx + 1 + j]
            try:
                x = float(line[0:10]); y = float(line[10:20])
                z = float(line[20:30])
                element = line[31:34].strip()
            except (ValueError, IndexError):
                continue
            atoms.append({"element": element, "xyz": [x, y, z]})
        bonds: List[List[int]] = []
        bond_start = counts_idx + 1 + n_atoms
        for j in range(n_bonds):
            if bond_start + j >= len(lines):
                break
            line = lines[bond_start + j]
            try:
                a = int(line[0:3]) - 1
                b = int(line[3:6]) - 1
                order = int(line[6:9])
            except (ValueError, IndexError):
                continue
            bonds.append([a, b, order])
        return atoms, bonds

    def _parse_mol2(self, path: Path
                    ) -> Tuple[List[Dict[str, Any]], List[List[int]]]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AdapterConversionError(f"cannot read {path}: {exc}") from exc
        atoms: List[Dict[str, Any]] = []
        bonds: List[List[int]] = []
        section = None
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("@<TRIPOS>"):
                section = stripped.split("@<TRIPOS>")[-1].strip()
                continue
            if not stripped or stripped.startswith("#"):
                continue
            if section == "ATOM":
                parts = stripped.split()
                if len(parts) < 6:
                    continue
                try:
                    x = float(parts[2]); y = float(parts[3]); z = float(parts[4])
                except ValueError:
                    continue
                sybyl = parts[5]
                element = sybyl.split(".")[0]
                atoms.append({"element": element, "xyz": [x, y, z],
                              "name": parts[1], "sybyl_type": sybyl})
            elif section == "BOND":
                parts = stripped.split()
                if len(parts) < 4:
                    continue
                try:
                    a = int(parts[1]) - 1
                    b = int(parts[2]) - 1
                except ValueError:
                    continue
                order_raw = parts[3]
                order = {"1": 1, "2": 2, "3": 3, "ar": 1, "am": 1}.get(
                    order_raw.lower(), 1)
                bonds.append([a, b, order])
        return atoms, bonds


_LOADING_EXAMPLE = """```python
import lmdb
import pickle

# 1) Iterate one split as a stream of graph records.
def iter_split(split="train"):
    env = lmdb.open(f"<target_dir>/data/{split}.lmdb",
                    readonly=True, lock=False)
    with env.begin() as txn:
        for _key, value in txn.cursor():
            # record keys: id / pocket_atoms / ligand_atoms / ligand_bonds
            yield pickle.loads(value)
    env.close()

# 2) Collate a batch (replace with your GNN / diffusion batching).
def collate(records):
    return records

# 3) Pull a batch of 32 and train (skeleton).
batch = collate([r for _, r in zip(range(32), iter_split("train"))])
# for step in range(num_steps):
#     batch = collate(next_n(iter_split("train"), 32))
#     loss = model(batch)                       # e.g. denoising / diffusion
#     loss.backward(); optimizer.step(); optimizer.zero_grad()
```
"""


if __name__ == "__main__":
    sys.exit(adapter_main(TargetDiffAdapter))
