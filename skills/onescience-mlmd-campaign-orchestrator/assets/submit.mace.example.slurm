#!/bin/bash
# Template: train MACE (onescience bundled) on a single accelerator.
#SBATCH -J mace_train
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c <CPUS>=8
#SBATCH --gres=dcu:1
#SBATCH -p <partition>
#SBATCH --time=48:00:00
#SBATCH --output=slurm-mace-%j.out
#SBATCH --error=slurm-mace-%j.err

source <CONDA_ROOT>/etc/profile.d/conda.sh
conda activate <ENV_NAME>
module purge
module load compiler/dtk/<DTK_VER>        # must match the torch build in the env
# Use the SAME onescience copy that will later export the model:
#   installed copy -> export PYTHONPATH=""
#   source tree    -> export PYTHONPATH=<parent-of-onescience>
export PYTHONPATH=<ONESCIENCE_PARENT or empty>
export OMP_NUM_THREADS=8
ulimit -s unlimited
cd "${SLURM_SUBMIT_DIR}"

echo "=== device check ==="
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.device_count())"

echo "=== train ==="
python -m onescience.utils.mace.cli.run_train \
  --name <name> \
  --work_dir "${SLURM_SUBMIT_DIR}" \
  --train_file <prefix>_train.extxyz \
  --valid_file <prefix>_valid.extxyz \
  --E0s average \
  --device cuda \
  --default_dtype float32 \
  --r_max <r_max> \
  --num_interactions 2 \
  --hidden_irreps "128x0e + 128x1o" \
  --batch_size 2 \
  --max_num_epochs 500 \
  --forces_weight 1000 \
  --energy_weight 10 \
  --seed 2026
