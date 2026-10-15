#!/bin/bash
# Export a trained MACE model to a LAMMPS force field file.
# Use the SAME onescience copy that trained the weights.
set -e

MODEL="$1"                 # .../model/<name>_stagetwo.model
FORMAT="${2:-libtorch}"    # libtorch | mliap
DTYPE="${3:-float64}"

source "${CONDA_ROOT:-$HOME/miniconda3}/etc/profile.d/conda.sh"
conda activate "${ENV_NAME:-CuCO2-py311-Test}"
module purge
module load "compiler/dtk/${DTK_VER:-25.04.2}"
# installed copy -> no PYTHONPATH ; source tree -> export PYTHONPATH=<parent>

echo "=== model sanity ==="
python - "$MODEL" <<'PY'
import os, sys, torch
os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
m = torch.load(sys.argv[1], map_location="cpu")
print("class:", type(m).__module__, type(m).__name__)
print("heads:", getattr(m, "heads", None), "| cp_readout:", hasattr(m, "cp_readout"))
PY

echo "=== convert (${FORMAT}) ==="
python -m onescience.utils.mace.cli.create_lammps_model "$MODEL" --format "$FORMAT" --dtype "$DTYPE"

if [ "$FORMAT" = "mliap" ]; then OUT="${MODEL}-mliap_lammps.pt"; else OUT="${MODEL}-lammps.pt"; fi
echo "=== verify ==="
python -c "import torch; torch.jit.load('${OUT}', map_location='cpu'); print('loads OK')" || true
echo "output: ${OUT}"
