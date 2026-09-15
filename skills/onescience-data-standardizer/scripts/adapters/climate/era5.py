"""Tier1 adapter: climate / ERA5.

Converts raw ERA5 reanalysis data (NetCDF or GRIB, typically organized as
one file per month or per year, or as a flat pile of variable files) into
the AI-Ready layout defined by
`skills/onescience-primitives/assets/climate/datasets/ERA5/spec.md`:

    <target>/
      data/YYYY.h5         # per-year HDF5 with datasets:
                           #   fields       [T, C, H, W] float32
                           #   global_means [1, C, 1, 1] float32
                           #   global_stds  [1, C, 1, 1] float32
                           #   attrs: variables (list[str]), time_step (=6)
      static/              # time-invariant fields (geopotential, masks, ...)
      stats/               # global_means.npy / global_stds.npy (aggregated)
      splits/              # train.txt / val.txt / test.txt by year
      dataset_card.json
      README.md

This adapter is intentionally permissive about the raw layout: it accepts
either per-year NetCDF files (`YYYY.nc`), per-month NetCDF files
(`YYYY-MM.nc` or `YYYYMM.nc`), or a single monolithic NetCDF. When the
raw layout is ambiguous, it records a warning in the dataset card rather
than failing hard, so that downstream validation can decide.

# requirements: h5py>=3.0, numpy>=1.24, netCDF4>=1.6
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from adapters._base import (  # noqa: E402
    AdapterConversionError, AdapterDependencyError, AdapterInputError,
    BaseAdapter, adapter_main,
)

YEAR_RE = re.compile(r"(19|20)\d{2}")
YEAR_MONTH_RE = re.compile(r"^((?:19|20)\d{2})[-_]?((?:0[1-9])|(?:1[0-2]))")

DEFAULT_VARIABLES: Tuple[str, ...] = (
    "10m_u_component_of_wind", "10m_v_component_of_wind", "2m_temperature",
    "total_precipitation", "mean_sea_level_pressure", "surface_pressure",
    "geopotential", "temperature", "u_component_of_wind",
    "v_component_of_wind", "specific_humidity", "relative_humidity",
)

# ERA5 variable name aliases: long CDS-API name <-> short GRIB/compact name.
# Real-world ERA5 downloads vary: the CDS API returns long names, while
# many reformatted / operational archives use short names. The adapter
# accepts either by expanding each requested variable to its alias set.
VARIABLE_ALIASES: Dict[str, Tuple[str, ...]] = {
    "2m_temperature": ("t2m", "temp2m", "temperature_2m"),
    "t2m": ("2m_temperature", "temp2m", "temperature_2m"),
    "10m_u_component_of_wind": ("u10", "u10m", "wind_u_10m"),
    "u10": ("10m_u_component_of_wind", "u10m", "wind_u_10m"),
    "10m_v_component_of_wind": ("v10", "v10m", "wind_v_10m"),
    "v10": ("10m_v_component_of_wind", "v10m", "wind_v_10m"),
    "total_precipitation": ("tp", "precip", "precipitation"),
    "tp": ("total_precipitation", "precip", "precipitation"),
    "mean_sea_level_pressure": ("msl", "mslp", "pressure_msl"),
    "msl": ("mean_sea_level_pressure", "mslp", "pressure_msl"),
    "surface_pressure": ("sp", "surf_pres"),
    "sp": ("surface_pressure", "surf_pres"),
    "geopotential": ("z", "geo", "geopot"),
    "z": ("geopotential", "geo", "geopot"),
    "temperature": ("t", "temp"),
    "t": ("temperature", "temp"),
    "u_component_of_wind": ("u", "wind_u"),
    "u": ("u_component_of_wind", "wind_u"),
    "v_component_of_wind": ("v", "wind_v"),
    "v": ("v_component_of_wind", "wind_v"),
    "specific_humidity": ("q", "sh", "humidity"),
    "q": ("specific_humidity", "sh", "humidity"),
    "relative_humidity": ("r", "rh"),
    "r": ("relative_humidity", "rh"),
}


def _expand_variable_aliases(variables: List[str]) -> List[str]:
    """Return ``variables`` plus all known aliases, order-preserving."""
    out: List[str] = []
    seen = set()
    for v in variables:
        for cand in (v,) + VARIABLE_ALIASES.get(v, ()):
            if cand not in seen:
                seen.add(cand)
                out.append(cand)
    return out


class ERA5Adapter(BaseAdapter):
    domain = "climate"
    dataset_name = "ERA5"
    primary_format = "hdf5"

    # ------------------------------------------------------------------
    def probe(self, source_dir: Path) -> Dict[str, Any]:
        nc_files: List[Path] = []
        grib_files: List[Path] = []
        h5_files: List[Path] = []
        static_candidates: List[Path] = []
        for p in sorted(source_dir.rglob("*")):
            if not p.is_file():
                continue
            suffix = p.suffix.lower()
            if suffix in (".nc", ".nc4", ".netcdf"):
                nc_files.append(p)
                if any(k in p.name.lower() for k in
                       ("geopotential", "static", "mask", "topography",
                        "land_sea", "soil_type")):
                    static_candidates.append(p)
            elif suffix in (".grib", ".grib2", ".grb", ".grb2"):
                grib_files.append(p)
            elif suffix in (".h5", ".hdf5"):
                h5_files.append(p)
        years_detected = sorted({
            int(m.group(0)) for p in nc_files + h5_files
            for m in [YEAR_RE.search(p.name)] if m
        })
        return {
            "source_dir": str(source_dir),
            "netcdf_files": [str(p) for p in nc_files],
            "grib_files": [str(p) for p in grib_files],
            "hdf5_files": [str(p) for p in h5_files],
            "static_candidates": [str(p) for p in static_candidates],
            "years_detected": years_detected,
            "counts": {
                "netcdf": len(nc_files),
                "grib": len(grib_files),
                "hdf5": len(h5_files),
                "static": len(static_candidates),
            },
            "summary": {
                "primary_input": "netcdf" if nc_files else
                                 ("hdf5" if h5_files else
                                  ("grib" if grib_files else "unknown")),
                "year_span": (years_detected[0], years_detected[-1])
                             if years_detected else None,
            },
        }

    # ------------------------------------------------------------------
    def plan(self, probe_report: Dict[str, Any],
             spec: Dict[str, Any]) -> Dict[str, Any]:
        primary = probe_report["summary"]["primary_input"]
        if primary == "grib":
            raise AdapterInputError(
                "GRIB input requires cfgrib which is not a hard dependency; "
                "convert GRIB -> NetCDF first (e.g. cdo -f nc copy) or extend "
                "this adapter with cfgrib support"
            )
        if primary == "unknown":
            raise AdapterInputError(
                "no NetCDF/HDF5 files found under source_dir; "
                "ERA5 adapter expects .nc or pre-converted .h5 inputs"
            )
        years: List[int] = probe_report["years_detected"] or []
        if not years and primary == "hdf5":
            # If the raw is already HDF5 but without year in filename, treat
            # the whole set as a single "unknown-year" bucket.
            years = [0]
        variables = list(spec.get("variables") or DEFAULT_VARIABLES)
        # Expand each requested variable to include known short/long aliases
        # so the adapter works with both CDS-API-style and compact archives.
        variables_expanded = _expand_variable_aliases(variables)
        return {
            "years": years,
            "variables": variables,
            "variables_expanded": variables_expanded,
            "primary_input": primary,
            "static_files": probe_report["static_candidates"],
            "time_step_hours": int(spec.get("time_step", 6)),
            "card_extra": {
                "data_layout": {
                    "data/": "HDF5 per year: fields[T,C,H,W] float32 + "
                             "global_means/global_stds + attrs.variables",
                    "static/": "time-invariant NetCDF/npy copied from raw",
                    "stats/": "global_means.npy / global_stds.npy aggregated "
                              "across all years",
                    "splits/": "train.txt / val.txt / test.txt by year "
                               "(causal split: earliest 70% train, next 15% "
                               "val, latest 15% test)",
                },
                "primary_format": "hdf5",
                "tensor_shape": "[T, C, H, W]",
                "dtype": "float32",
                "dimensions": {
                    "T": "time steps within a year (6-hourly => ~1460)",
                    "C": "variable channels",
                    "H": "latitude grid points",
                    "W": "longitude grid points",
                },
                "spec_alignment": [
                    "per-year HDF5 layout matches ERA5 spec.md data_schema",
                    "attrs.variables preserved for channel-index lookup",
                    "causal year-based split per spec.md split_strategy",
                ],
                "loading_example": _LOADING_EXAMPLE,
            },
        }

    # ------------------------------------------------------------------
    def convert(self, source_dir: Path, target_dir: Path,
                plan: Dict[str, Any]) -> None:
        self.require_deps("h5py>=3.0", "numpy>=1.24")
        try:
            import h5py  # type: ignore
            import numpy as np  # type: ignore
        except ImportError as exc:
            raise AdapterDependencyError(str(exc)) from exc

        years: List[int] = plan["years"]
        variables: List[str] = plan.get("variables_expanded") or plan["variables"]
        primary = plan["primary_input"]
        data_dir = target_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        if primary == "hdf5":
            self._passthrough_hdf5(source_dir, data_dir, h5py, np)
        else:
            self._convert_netcdf(source_dir, data_dir, years, variables,
                                 h5py, np)

        # Static files: copy raw static candidates as-is.
        static_dir = target_dir / "static"
        static_files = plan.get("static_files") or []
        if static_files:
            static_dir.mkdir(parents=True, exist_ok=True)
            for src in static_files:
                dst = static_dir / Path(src).name
                if not dst.exists():
                    dst.write_bytes(Path(src).read_bytes())

        # Aggregate stats across all produced year files.
        self._aggregate_stats(data_dir, target_dir / "stats", np, h5py)

        # Causal split by year.
        self._write_splits(years, target_dir / "splits")

    # ------------------------------------------------------------------
    def _convert_netcdf(self, source_dir: Path, data_dir: Path,
                        years: List[int], variables: List[str],
                        h5py: Any, np: Any) -> None:
        try:
            import netCDF4  # type: ignore
        except ImportError as exc:
            raise AdapterDependencyError(
                f"netCDF4 not installed: {exc}; install with: pip install netCDF4"
            ) from exc

        # Group raw NetCDF files by year.
        by_year: Dict[int, List[Path]] = defaultdict(list)
        for p in sorted(source_dir.rglob("*.nc")):
            m = YEAR_MONTH_RE.match(p.name) or YEAR_RE.search(p.name)
            if not m:
                continue
            year = int(m.group(1) if m.re is YEAR_MONTH_RE else m.group(0))
            by_year[year].append(p)

        if not by_year:
            raise AdapterConversionError(
                "no NetCDF files with a recognizable year token in filename; "
                "cannot bucket by year"
            )

        for year, files in sorted(by_year.items()):
            out_path = data_dir / f"{year}.h5"
            if out_path.exists():
                self.warn(f"{out_path.name} already exists; overwriting")
            stacks, present_vars = self._read_year(files, variables, netCDF4, np)
            if stacks is None:
                self.warn(f"year {year}: no readable variables; skipping")
                continue
            fields = stacks  # [T, C, H, W]
            means = fields.mean(axis=(0, 2, 3), keepdims=True).astype("float32")
            stds = fields.std(axis=(0, 2, 3), keepdims=True).astype("float32")
            with h5py.File(out_path, "w") as fh:
                fh.create_dataset("fields", data=fields,
                                  chunks=True, compression="gzip",
                                  compression_opts=4)
                fh.create_dataset("global_means", data=means)
                fh.create_dataset("global_stds", data=stds)
                fh["fields"].attrs["variables"] = np.array(
                    present_vars, dtype=h5py.string_dtype())
                fh["fields"].attrs["time_step"] = 6

    def _read_year(self, files: List[Path], variables: List[str],
                   netCDF4: Any, np: Any
                   ) -> Tuple[Optional[Any], List[str]]:
        """Concatenate all files for one year into [T, C, H, W] float32.

        ``variables`` may contain aliases (e.g. both ``2m_temperature`` and
        ``t2m``). We build a reverse map alias -> canonical group so that
        only one match per logical variable is kept, preferring the first
        alias that actually exists in the file.
        """
        # Build canonical group for each requested variable name.
        # Two names belong to the same group if one is an alias of the other.
        canonical_of: Dict[str, str] = {}
        for v in variables:
            group = v
            # If v is an alias of some long name, use the long name as group.
            for long_name, aliases in VARIABLE_ALIASES.items():
                if v == long_name or v in aliases:
                    # Prefer the long CDS-API name as canonical group key.
                    group = long_name
                    break
            canonical_of[v] = group

        per_var: Dict[str, List[Any]] = defaultdict(list)
        present: List[str] = []
        seen_groups: set = set()
        for f in files:
            try:
                ds = netCDF4.Dataset(str(f), "r")
            except Exception as exc:
                self.warn(f"cannot open {f.name}: {exc}")
                continue
            with ds:
                for v in variables:
                    group = canonical_of[v]
                    if group in seen_groups:
                        continue  # already captured this logical variable
                    if v in ds.variables:
                        arr = ds.variables[v][:]
                        per_var[v].append(np.asarray(arr, dtype="float32"))
                        if v not in present:
                            present.append(v)
                        seen_groups.add(group)
        if not per_var:
            return None, []
        # Each var: concat along time -> [T, H, W]
        stacked_vars = []
        for v in present:
            chunks = per_var[v]
            arr = np.concatenate(chunks, axis=0) if len(chunks) > 1 else chunks[0]
            if arr.ndim == 2:  # single time step flattened
                arr = arr[None, ...]
            stacked_vars.append(arr)
        # Ensure identical shapes; drop mismatched vars with a warning.
        ref_shape = stacked_vars[0].shape
        kept: List[Any] = []
        kept_names: List[str] = []
        for name, arr in zip(present, stacked_vars):
            if arr.shape == ref_shape:
                kept.append(arr)
                kept_names.append(name)
            else:
                self.warn(f"variable {name} shape {arr.shape} != {ref_shape}; dropped")
        if not kept:
            return None, []
        fields = np.stack(kept, axis=1).astype("float32")  # [T, C, H, W]
        return fields, kept_names

    # ------------------------------------------------------------------
    def _passthrough_hdf5(self, source_dir: Path, data_dir: Path,
                          h5py: Any, np: Any) -> None:
        """When raw is already per-year HDF5, copy with validation."""
        copied = 0
        for p in sorted(source_dir.rglob("*.h5")) + sorted(source_dir.rglob("*.hdf5")):
            dst = data_dir / p.name
            try:
                with h5py.File(p, "r") as fh:
                    keys = list(fh.keys())
                if "fields" not in keys:
                    self.warn(f"{p.name}: no 'fields' dataset; copying as-is")
                dst.write_bytes(p.read_bytes())
                copied += 1
            except Exception as exc:
                self.warn(f"cannot process {p.name}: {exc}")
        if copied == 0:
            raise AdapterConversionError(
                "no HDF5 files could be copied from source_dir"
            )

    # ------------------------------------------------------------------
    def _aggregate_stats(self, data_dir: Path, stats_dir: Path,
                         np: Any, h5py: Any) -> None:
        year_files = sorted(data_dir.glob("*.h5"))
        if not year_files:
            return
        stats_dir.mkdir(parents=True, exist_ok=True)
        all_means: List[Any] = []
        all_stds: List[Any] = []
        for yf in year_files:
            try:
                with h5py.File(yf, "r") as fh:
                    if "global_means" in fh:
                        all_means.append(np.asarray(fh["global_means"]))
                    if "global_stds" in fh:
                        all_stds.append(np.asarray(fh["global_stds"]))
            except Exception as exc:
                self.warn(f"cannot read stats from {yf.name}: {exc}")
        if all_means:
            stacked = np.concatenate(all_means, axis=0)
            np.save(stats_dir / "global_means.npy",
                    stacked.mean(axis=0, keepdims=True).astype("float32"))
        if all_stds:
            stacked = np.concatenate(all_stds, axis=0)
            np.save(stats_dir / "global_stds.npy",
                    stacked.mean(axis=0, keepdims=True).astype("float32"))

    # ------------------------------------------------------------------
    def _write_splits(self, years: List[int], splits_dir: Path) -> None:
        if not years or years == [0]:
            return
        splits_dir.mkdir(parents=True, exist_ok=True)
        ys = sorted(years)
        n = len(ys)
        n_train = max(1, int(round(n * 0.70)))
        n_val = max(1, int(round(n * 0.15))) if n > 2 else 0
        train = ys[:n_train]
        val = ys[n_train:n_train + n_val]
        test = ys[n_train + n_val:]
        (splits_dir / "train.txt").write_text(
            "\n".join(str(y) for y in train) + "\n", encoding="utf-8")
        (splits_dir / "val.txt").write_text(
            "\n".join(str(y) for y in val) + ("\n" if val else ""),
            encoding="utf-8")
        (splits_dir / "test.txt").write_text(
            "\n".join(str(y) for y in test) + ("\n" if test else ""),
            encoding="utf-8")
        (splits_dir / "splits.json").write_text(json.dumps(
            {"strategy": "causal_by_year",
             "train": train, "val": val, "test": test},
            indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    def post_process(self, target_dir: Path) -> None:
        # Nothing extra; stats and splits are produced inside convert().
        return None


_LOADING_EXAMPLE = """```python
import h5py
import numpy as np

# 1) Open one year of gridded fields + stored normalization.
with h5py.File("<target_dir>/data/1979.h5", "r") as f:
    fields = f["fields"]                       # [T, C, H, W] float32
    variables = [v.decode() if isinstance(v, bytes) else str(v)
                 for v in fields.attrs["variables"]]
    means = f["global_means"][:]               # [1, C, 1, 1]
    stds = f["global_stds"][:]                 # [1, C, 1, 1]

    # 2) Build (past-window -> next-step) samples for a forecast/surrogate.
    window = 4
    target_var = variables.index("2m_temperature")
    T = fields.shape[0]
    for t in range(window, T):
        x = fields[t - window:t, :, :, :]      # [window, C, H, W]
        x_norm = (x - means) / stds            # apply stored normalization
        y = fields[t, target_var, :, :]        # [H, W] target field
        # 3) feed x_norm -> model -> predict y (skeleton below)
        break

# 4) Training-loop skeleton (iterate years, stack windows, batch):
# for year_file in sorted(glob("<target_dir>/data/*.h5")):
#     for x_norm, y in windowed_samples(year_file, window):
#         pred = model(x_norm); loss = criterion(pred, y)
#         loss.backward(); optimizer.step(); optimizer.zero_grad()
```
"""


if __name__ == "__main__":
    sys.exit(adapter_main(ERA5Adapter))
