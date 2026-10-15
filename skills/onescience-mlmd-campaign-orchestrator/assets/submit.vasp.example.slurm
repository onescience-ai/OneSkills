#!/bin/bash
# Template: submit a DCU/GPU VASP job (relax or AIMD).
# Keep site-specific constants in onescience.json / runsite config; placeholders below.
#SBATCH -J <jobname>
#SBATCH -N 1
#SBATCH --ntasks-per-node=<NRANKS>        # = number of accelerators used
#SBATCH -c <CPUS_PER_RANK>
#SBATCH --gres=dcu:<NRANKS>               # or --gpus=<NRANKS> on NVIDIA sites
#SBATCH -p <partition>
#SBATCH --time=<HH:MM:SS>
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# --- environment (from site config, NOT hardcoded in the skill) ---
module purge
source <VASP_ENV_SH>                       # e.g. .../vasp-<ver>/scripts/env.sh

ulimit -s unlimited
ulimit -l unlimited

cd "${SLURM_SUBMIT_DIR}"
VASP_EXE=vasp_std
config="config.${SLURM_JOB_ID}"

# Intel MPI -configfile: the -genv globals MUST share the line with the first
# "-host ... -n 1 <exe>" entry (a newline here -> "no executable specified", exit 127).
printf '%s' "-genv OMP_NUM_THREADS <OMP> " > "${config}"
for host in $(scontrol show hostnames "${SLURM_NODELIST}"); do
    for ((dev=0; dev<NRANKS; dev++)); do
        echo "-host ${host} -env HIP_VISIBLE_DEVICES ${dev} -n 1 ${VASP_EXE}" >> "${config}"
    done
done

export OMP_NUM_THREADS=<OMP>
mpirun -configfile "${config}"
