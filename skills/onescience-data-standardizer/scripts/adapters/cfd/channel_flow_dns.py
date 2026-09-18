"""Tier1 adapter: cfd / channel_flow_dns.

Normalizes a raw channel_flow_dns-style directory into the AI-Ready format.

Accepted raw layouts:
    A. Directory with .npy files and dataset_manifest.json
    B. Directory with .json files and .npy files

# requirements: numpy>=1.24
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from adapters._base import (  # noqa: E402
    AdapterConversionError, AdapterInputError, BaseAdapter, adapter_main,
)


class ChannelFlowDNSAdapter(BaseAdapter):
    domain = "cfd"
    dataset_name = "channel_flow_dns"
    primary_format = "numpy"

    # ------------------------------------------------------------------
    def probe(self, source_dir: Path) -> Dict[str, Any]:
        """Probe the source directory and return a probe report."""
        npy_files = sorted(source_dir.rglob("*.npy"))
        json_files = sorted(source_dir.rglob("*.json"))
        
        # Check for dataset_manifest.json
        manifest_file = source_dir / "dataset_manifest.json"
        has_manifest = manifest_file.exists()
        
        # Check for grid_info.json
        grid_info_file = source_dir / "grid_info.json"
        has_grid_info = grid_info_file.exists()
        
        # Categorize files
        data_files = []
        metadata_files = []
        
        for f in npy_files:
            data_files.append({
                "path": str(f.relative_to(source_dir)),
                "size_bytes": f.stat().st_size,
                "format": "numpy"
            })
        
        for f in json_files:
            if f.name in ["dataset_manifest.json", "grid_info.json"]:
                metadata_files.append({
                    "path": str(f.relative_to(source_dir)),
                    "size_bytes": f.stat().st_size,
                    "format": "json"
                })
        
        return {
            "source_dir": str(source_dir),
            "has_manifest": has_manifest,
            "has_grid_info": has_grid_info,
            "data_files": data_files,
            "metadata_files": metadata_files,
            "total_files": len(data_files) + len(metadata_files)
        }

    # ------------------------------------------------------------------
    def plan(self, probe_report: Dict[str, Any], spec: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a conversion plan based on probe report and spec."""
        if not probe_report["has_manifest"]:
            raise AdapterInputError(
                "dataset_manifest.json not found in source directory. "
                "Expected a dataset_manifest.json file with metadata."
            )
        
        # Read manifest
        source_dir = Path(probe_report["source_dir"])
        manifest_file = source_dir / "dataset_manifest.json"
        
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        # Read grid info if available
        grid_info = {}
        if probe_report["has_grid_info"]:
            grid_info_file = source_dir / "grid_info.json"
            with open(grid_info_file, 'r') as f:
                grid_info = json.load(f)
        
        # Generate conversion plan
        plan = {
            "manifest": manifest,
            "grid_info": grid_info,
            "data_files": probe_report["data_files"],
            "metadata_files": probe_report["metadata_files"]
        }
        
        return plan

    # ------------------------------------------------------------------
    def convert(self, source_dir: Path, target_dir: Path, plan: Dict[str, Any]) -> None:
        """Execute the conversion plan and write to target_dir."""
        import numpy as np
        
        # Create target directory structure
        target_dir.mkdir(parents=True, exist_ok=True)
        data_dir = target_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Copy and convert data files
        for file_info in plan["data_files"]:
            source_file = source_dir / file_info["path"]
            target_file = data_dir / file_info["path"]
            
            # Load numpy array
            data = np.load(source_file)
            
            # Save as numpy array (could convert to other formats if needed)
            np.save(target_file, data)
        
        # Write dataset_card.json
        dataset_card = {
            "name": plan["manifest"].get("name", "channel_flow_dns"),
            "domain": "cfd",
            "description": plan["manifest"].get("description", "Channel flow DNS data"),
            "version": plan["manifest"].get("version", "1.0.0"),
            "variables": plan["manifest"].get("variables", {}),
            "units": plan["manifest"].get("units", {}),
            "coordinate_system": plan["manifest"].get("coordinate_system", "cartesian"),
            "grid_info": plan["grid_info"],
            "data_files": [f["path"] for f in plan["data_files"]],
            "metadata_files": [f["path"] for f in plan["metadata_files"]]
        }
        
        with open(target_dir / "dataset_card.json", 'w') as f:
            json.dump(dataset_card, f, indent=2)
        
        # Write README.md
        readme_content = f"""# {dataset_card['name']}

{dataset_card['description']}

## Variables

"""
        for var_name, var_info in dataset_card['variables'].items():
            readme_content += f"- **{var_name}**: {var_info}\n"
        
        readme_content += f"""
## Grid Information

- Channel height: {plan['grid_info'].get('channel_height', 'N/A')} m
- Channel length: {plan['grid_info'].get('channel_length', 'N/A')} m
- Channel width: {plan['grid_info'].get('channel_width', 'N/A')} m
- Reynolds number: {plan['grid_info'].get('reynolds_number', 'N/A')}

## Data Format

Data is stored as NumPy arrays (.npy files).

## License

{plan['manifest'].get('license', 'Unknown')}
"""
        
        with open(target_dir / "README.md", 'w') as f:
            f.write(readme_content)
        
        # Create splits directory (empty for now)
        splits_dir = target_dir / "splits"
        splits_dir.mkdir(exist_ok=True)
        
        # Create stats directory (empty for now)
        stats_dir = target_dir / "stats"
        stats_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    def validate(self, target_dir: Path) -> Dict[str, Any]:
        """Validate the converted dataset."""
        issues = []
        
        # Check required files
        required_files = ["dataset_card.json", "README.md", "data"]
        for required in required_files:
            if not (target_dir / required).exists():
                issues.append(f"Missing required file/directory: {required}")
        
        # Check dataset_card.json is valid JSON
        dataset_card_file = target_dir / "dataset_card.json"
        if dataset_card_file.exists():
            try:
                with open(dataset_card_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                issues.append(f"Invalid JSON in dataset_card.json: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


if __name__ == "__main__":
    adapter_main(ChannelFlowDNSAdapter)