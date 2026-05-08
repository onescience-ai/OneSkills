#!/bin/bash
# backend_id: slurm_dcu
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
#SBATCH --exclusive

echo "START TIME: $(date)"
module purge

source /etc/profile  #不能删除
source /etc/profile.d/modules.sh #不能删除
module use /work2/share/sghpc_sdk/modulefiles/ #不能删除

##### DCU backend module setup #####
{backend.module_setup}

##### python always Launch Conda ENV #####
source ~/.bashrc
conda activate {conda.env_name}

source $ROCM_PATH/cuda/env.sh #不能删除
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib #不能删除

##### onescience datasets and models Launch env #####
export ONESCIENCE_DATASETS_DIR="{env_vars.ONESCIENCE_DATASETS_DIR}"
export ONESCIENCE_MODELS_DIR="{env_vars.ONESCIENCE_MODELS_DIR}"

##### Show env #####
which python

##### Set accelerator visibility #####
{backend.device_visibility_export}

export OMP_NUM_THREADS={cluster.cpus_per_task}
nodes=$(scontrol show hostnames $SLURM_JOB_NODELIST)
nodes_array=($nodes)

export MASTER_ADDR=$(hostname)

echo SLURM_NNODES=$SLURM_NNODES
echo "Nodes: ${nodes_array[*]}"
echo SLURM_NTASKS=$SLURM_NTASKS

python {script.code_path}
