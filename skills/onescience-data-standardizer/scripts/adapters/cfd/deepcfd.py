"""Tier1 adapter: cfd / DeepCFD.

Normalizes a raw DeepCFD-style directory into the paired pickle layout
expected by `onescience-primitives/assets/cfd/datapipes/deepcfd`:

    <target>/
      data/dataX.pkl       # input regular-grid tensors  [N, Cin, H, W]
      data/dataY.pkl       # output regular-grid tensors [N, Cout, H, W]
      stats/               # per-channel RMS weights for loss balancing
      splits/              # deterministic train/test index split
      dataset_card.json
      README.md

Accepted raw layouts:
    A. Already paired: contains `dataX.pkl` + `dataY.pkl` at any depth.
    B. Per-case directories: each subdir contains `X.pkl` + `Y.pkl` (or
       `input.pkl` + `output.pkl`); adapter stacks them along axis 0.
    C. Single monolithic pickle containing a dict {"x": ..., "y": ...} or
       {"input": ..., "output": ...}.

Layouts outside A/B/C raise AdapterInputError with a diagnostic message.

# requirements: numpy>=1.24
"""

from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from adapters._base import (  # noqa: E402
    AdapterConversionError, AdapterInputError, BaseAdapter, adapter_main,
)

X_NAMES = ("dataX.pkl", "X.pkl", "input.pkl", "x.pkl", "inputs.pkl")
Y_NAMES = ("dataY.pkl", "Y.pkl", "output.pkl", "y.pkl", "targets.pkl")


class DeepCFDAdapter(BaseAdapter):
    domain = "cfd"
    dataset_name = "DeepCFD"
    primary_format = "pickle"

    # ------------------------------------------------------------------
    def probe(self, source_dir: Path) -> Dict[str, Any]:
        pkl_files: List[Path] = sorted(source_dir.rglob("*.pkl"))
        layout = "unknown"
        paired_root: Optional[Tuple[Path, Path]] = None
        case_dirs: List[Path] = []
        monolithic: Optional[Path] = None

        # Layout A: paired at any depth (prefer shallowest).
        for p in pkl_files:
            if p.name in X_NAMES:
                for q in pkl_files:
                    if q.parent == p.parent and q.name in Y_NAMES:
                        paired_root = (p, q)
                        layout = "paired"
                        break
            if paired_root:
                break

        # Layout B: per-case directories.
        if layout == "unknown":
            for sub in sorted(source_dir.iterdir()):
                if not sub.is_dir():
                    continue
                xs = [p for p in sub.glob("*.pkl") if p.name in X_NAMES]
                ys = [p for p in sub.glob("*.pkl") if p.name in Y_NAMES]
                if xs and ys:
                    case_dirs.append(sub)
            if case_dirs:
                layout = "per_case"

        # Layout C: monolithic dict pickle.
        if layout == "unknown" and len(pkl_files) == 1:
            monolithic = pkl_files[0]
            layout = "monolithic"

        return {
            "source_dir": str(source_dir),
            "pickle_files": [str(p) for p in pkl_files],
            "layout": layout,
            "paired_root": [str(paired_root[0]), str(paired_root[1])]
                           if paired_root else None,
            "case_dirs": [str(p) for p in case_dirs],
            "monolithic": str(monolithic) if monolithic else None,
            "summary": {
                "layout": layout,
                "pickle_count": len(pkl_files),
                "case_count": len(case_dirs),
            },
        }

    # ------------------------------------------------------------------
    def plan(self, probe_report: Dict[str, Any],
             spec: Dict[str, Any]) -> Dict[str, Any]:
        layout = probe_report["layout"]
        if layout == "unknown":
            raise AdapterInputError(
                "cannot identify DeepCFD raw layout; expected one of: "
                "(A) paired dataX.pkl+dataY.pkl, "
                "(B) per-case subdirs each with X.pkl+Y.pkl, "
                "(C) a single monolithic pickle containing {'x','y'} dict. "
                f"Found {probe_report['summary']['pickle_count']} pickle files "
                "with no recognizable pairing."
            )
        split_ratio = float(spec.get("split_ratio", 0.8))
        seed = int(spec.get("seed", 42))
        return {
            "layout": layout,
            "split_ratio": split_ratio,
            "seed": seed,
            "card_extra": {
                "data_layout": {
                    "data/": "paired pickle arrays: dataX.pkl [N,Cin,H,W] "
                             "float32, dataY.pkl [N,Cout,H,W] float32",
                    "stats/": "loss_weights.json (per-output-channel RMS "
                              "weights computed on train split)",
                    "splits/": "train_indices.npy / test_indices.npy "
                               "(deterministic, seed=42, ratio=0.8)",
                },
                "primary_format": "pickle",
                "tensor_shape": "[N, C, H, W]",
                "dtype": "float32",
                "dimensions": {
                    "N": "sample count",
                    "C": "channel count (Cin for X, Cout for Y)",
                    "H": "grid height",
                    "W": "grid width",
                },
                "spec_alignment": [
                    "dataX/dataY sample count parity enforced",
                    "channel-major layout matches deepcfd datapipe expectation",
                    "deterministic split with fixed seed",
                ],
                "loading_example": _LOADING_EXAMPLE,
            },
        }

    # ------------------------------------------------------------------
    def convert(self, source_dir: Path, target_dir: Path,
                plan: Dict[str, Any]) -> None:
        self.require_deps("numpy>=1.24")
        import numpy as np  # type: ignore

        layout = plan["layout"]
        if layout == "paired":
            x_path, y_path = [Path(p) for p in
                              self._latest_probe()["paired_root"]]  # type: ignore
            X = self._load_pickle(x_path)
            Y = self._load_pickle(y_path)
        elif layout == "per_case":
            X, Y = self._stack_cases(source_dir, np)
        elif layout == "monolithic":
            X, Y = self._load_monolithic(source_dir, np)
        else:
            raise AdapterConversionError(f"unsupported layout: {layout}")

        X = np.asarray(X, dtype="float32")
        Y = np.asarray(Y, dtype="float32")
        if X.ndim != 4 or Y.ndim != 4:
            raise AdapterConversionError(
                f"expected 4-D arrays [N,C,H,W]; got X.shape={X.shape}, "
                f"Y.shape={Y.shape}"
            )
        if X.shape[0] != Y.shape[0]:
            raise AdapterConversionError(
                f"sample count mismatch: X={X.shape[0]} vs Y={Y.shape[0]}"
            )

        data_dir = target_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(data_dir / "dataX.pkl", "wb") as fh:
            pickle.dump(X, fh, protocol=pickle.HIGHEST_PROTOCOL)
        with open(data_dir / "dataY.pkl", "wb") as fh:
            pickle.dump(Y, fh, protocol=pickle.HIGHEST_PROTOCOL)

        # Deterministic split.
        n = X.shape[0]
        rng = np.random.default_rng(plan["seed"])
        perm = rng.permutation(n)
        n_train = int(round(n * plan["split_ratio"]))
        train_idx = np.sort(perm[:n_train]).astype("int64")
        test_idx = np.sort(perm[n_train:]).astype("int64")
        splits_dir = target_dir / "splits"
        splits_dir.mkdir(parents=True, exist_ok=True)
        np.save(splits_dir / "train_indices.npy", train_idx)
        np.save(splits_dir / "test_indices.npy", test_idx)
        (splits_dir / "splits.json").write_text(json.dumps({
            "strategy": "random_permutation_fixed_seed",
            "seed": plan["seed"],
            "split_ratio": plan["split_ratio"],
            "n_total": int(n),
            "n_train": int(len(train_idx)),
            "n_test": int(len(test_idx)),
        }, indent=2), encoding="utf-8")

        # Per-output-channel RMS weights on train split.
        y_train = Y[train_idx] if len(train_idx) else Y
        rms = np.sqrt((y_train.astype("float64") ** 2).mean(axis=(0, 2, 3)))
        rms = np.where(rms < 1e-8, 1.0, rms)
        weights = (1.0 / rms).astype("float32")
        weights = weights / weights.sum() * len(weights)
        stats_dir = target_dir / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        (stats_dir / "loss_weights.json").write_text(json.dumps({
            "per_channel_rms": rms.astype("float32").tolist(),
            "loss_weights": weights.tolist(),
            "note": "weights inversely proportional to per-channel RMS, "
                    "normalized to sum=Cout",
        }, indent=2), encoding="utf-8")
        np.save(stats_dir / "loss_weights.npy", weights)

        # Store shapes for downstream introspection.
        self._plan_summary = {  # type: ignore[attr-defined]
            "n_samples": int(n),
            "x_shape": list(X.shape),
            "y_shape": list(Y.shape),
            "layout": layout,
        }
        plan.setdefault("card_extra", {})["statistics"] = {
            "num_samples": int(n),
            "x_shape": list(X.shape),
            "y_shape": list(Y.shape),
        }
        plan["card_extra"]["splits"] = {
            "strategy": "random_permutation_fixed_seed",
            "train": int(len(train_idx)),
            "test": int(len(test_idx)),
        }

    # ------------------------------------------------------------------
    def _latest_probe(self) -> Dict[str, Any]:
        # Re-run probe cheaply; adapters are single-shot so this is safe.
        return self.probe(self.source_dir)

    def _load_pickle(self, path: Path) -> Any:
        try:
            with open(path, "rb") as fh:
                return pickle.load(fh)
        except Exception as exc:
            raise AdapterConversionError(
                f"cannot unpickle {path}: {exc}"
            ) from exc

    def _stack_cases(self, source_dir: Path, np: Any
                     ) -> Tuple[Any, Any]:
        xs: List[Any] = []
        ys: List[Any] = []
        for sub in sorted(source_dir.iterdir()):
            if not sub.is_dir():
                continue
            x_file = next((p for p in sub.glob("*.pkl")
                           if p.name in X_NAMES), None)
            y_file = next((p for p in sub.glob("*.pkl")
                           if p.name in Y_NAMES), None)
            if not (x_file and y_file):
                continue
            x = np.asarray(self._load_pickle(x_file), dtype="float32")
            y = np.asarray(self._load_pickle(y_file), dtype="float32")
            if x.ndim == 3:
                x = x[None, ...]
            if y.ndim == 3:
                y = y[None, ...]
            xs.append(x)
            ys.append(y)
        if not xs:
            raise AdapterConversionError(
                "per_case layout detected but no case directory contained "
                "both X and Y pickles"
            )
        ref_x, ref_y = xs[0].shape[1:], ys[0].shape[1:]
        for i, (x, y) in enumerate(zip(xs, ys)):
            if x.shape[1:] != ref_x or y.shape[1:] != ref_y:
                raise AdapterConversionError(
                    f"case {i} shape mismatch: x{x.shape} y{y.shape} vs "
                    f"reference x{(ref_x,)} y{(ref_y,)}"
                )
        return np.concatenate(xs, axis=0), np.concatenate(ys, axis=0)

    def _load_monolithic(self, source_dir: Path, np: Any
                         ) -> Tuple[Any, Any]:
        candidates = sorted(source_dir.rglob("*.pkl"))
        if len(candidates) != 1:
            raise AdapterConversionError(
                f"monolithic layout expects exactly 1 pickle; found {len(candidates)}"
            )
        obj = self._load_pickle(candidates[0])
        if isinstance(obj, dict):
            for xk in ("x", "X", "input", "inputs", "dataX"):
                for yk in ("y", "Y", "output", "outputs", "targets", "dataY"):
                    if xk in obj and yk in obj:
                        return (np.asarray(obj[xk], dtype="float32"),
                                np.asarray(obj[yk], dtype="float32"))
        if isinstance(obj, (list, tuple)) and len(obj) == 2:
            return (np.asarray(obj[0], dtype="float32"),
                    np.asarray(obj[1], dtype="float32"))
        raise AdapterConversionError(
            "monolithic pickle must be a dict with x/y keys or a 2-tuple; "
            f"got {type(obj).__name__}"
        )


_LOADING_EXAMPLE = """```python
import json
import pickle
import numpy as np

# 1) Load paired regular-grid tensors.
with open("<target_dir>/data/dataX.pkl", "rb") as f:
    X = pickle.load(f)          # [N, Cin, H, W] float32
with open("<target_dir>/data/dataY.pkl", "rb") as f:
    Y = pickle.load(f)          # [N, Cout, H, W] float32

# 2) Deterministic split indices.
train_idx = np.load("<target_dir>/splits/train_indices.npy")
test_idx = np.load("<target_dir>/splits/test_indices.npy")
X_train, Y_train = X[train_idx], Y[train_idx]

# 3) Per-output-channel loss weights (balanced regression).
weights = np.array(
    json.load(open("<target_dir>/stats/loss_weights.json"))["loss_weights"],
    dtype="float32")

# 4) Minimal batch iterator -> feed straight into a UNet/CNN surrogate.
def batches(Xa, Ya, bs=16, shuffle=True):
    n = len(Xa)
    order = np.random.permutation(n) if shuffle else np.arange(n)
    for s in range(0, n, bs):
        sel = order[s:s + bs]
        yield Xa[sel], Ya[sel]

# 5) Training-loop skeleton (model/optimizer are your own; numpy->torch
#    conversion omitted for brevity).
# for xb, yb in batches(X_train, Y_train):
#     pred = model(xb)                          # [B, Cout, H, W]
#     loss = (weights * (pred - yb) ** 2).mean()
#     loss.backward(); optimizer.step(); optimizer.zero_grad()
```
"""


if __name__ == "__main__":
    sys.exit(adapter_main(DeepCFDAdapter))
