#!/bin/bash
# backend_id: slurm_cpu
# runtime_status: planned
#SBATCH -p {cluster.partition}
#SBATCH -N {cluster.nodes}
#SBATCH --cpus-per-task={cluster.cpus_per_task}
#SBATCH --ntasks-per-node={cluster.ntasks_per_node}
#SBATCH -J {script.job_name}
#SBATCH --time={cluster.time_limit}
#SBATCH --mem={cluster.memory}
#SBATCH -o logs/%j.out

echo "START TIME: $(date)"
module purge

source /etc/profile
source /etc/profile.d/modules.sh

##### CPU backend module setup #####
{backend.module_setup}

##### python always Launch Conda ENV #####
source ~/.bashrc
conda activate {conda.env_name}

##### onescience datasets and models Launch env #####
export ONESCIENCE_DATASETS_DIR="{env_vars.ONESCIENCE_DATASETS_DIR}"
export ONESCIENCE_MODELS_DIR="{env_vars.ONESCIENCE_MODELS_DIR}"

##### Show env #####
which python

##### CPU backend does not need accelerator visibility #####
{backend.device_visibility_export}

export OMP_NUM_THREADS={cluster.cpus_per_task}

python {script.code_path}
