#!/bin/bash
# backend_id: slurm_gpu_multinode_torchrun
# runtime_status: stable
#SBATCH -p {cluster.partition}
#SBATCH -N {cluster.nodes}
#SBATCH --gres={cluster.gpu_type}:{cluster.gpus_per_node}
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

##### GPU backend module setup #####
{backend.module_setup}

{conda.activate_script}

##### CUDA backend env #####
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib

##### onescience datasets and models Launch env #####
export ONESCIENCE_DATASETS_DIR="{env_vars.ONESCIENCE_DATASETS_DIR}"
export ONESCIENCE_MODELS_DIR="{env_vars.ONESCIENCE_MODELS_DIR}"

##### Set accelerator visibility #####
{backend.device_visibility_export}

export OMP_NUM_THREADS={cluster.cpus_per_task}
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT={env_vars.MASTER_PORT}

torchrun \
  --nnodes={cluster.nodes} \
  --nproc_per_node={cluster.gpus_per_node} \
  --rdzv_backend=c10d \
  --rdzv_endpoint=${MASTER_ADDR}:${MASTER_PORT} \
  {script.code_path}
