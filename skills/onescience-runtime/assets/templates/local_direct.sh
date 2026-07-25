#!/bin/bash
set -euo pipefail

echo "START TIME: $(date)"
module purge || true

source /etc/profile
source /etc/profile.d/modules.sh

##### Project runtime module setup #####
{runtime.module_setup}

##### Local direct module setup #####
{backend.module_setup}

{conda.activate_script}

export ONESCIENCE_DATASETS_DIR="{env_vars.ONESCIENCE_DATASETS_DIR}"
export ONESCIENCE_MODELS_DIR="{env_vars.ONESCIENCE_MODELS_DIR}"

##### Show env #####
which python

# Deferred library check: log missing shared libs as warnings, do not block execution.
# Known login-node-unavailable libs (libmsgpackc.so.2, libcudnn*, libnccl*, etc.)
# are expected to be resolved on compute nodes during actual job execution.
echo "--- Shared library check (warnings only) ---"
ldd "$(which python)" 2>&1 | grep "not found" | while read -r line; do
  echo "[WARN] Missing shared library on this node (may be available on compute node): $line"
done || echo "[INFO] ldd check skipped or all libraries resolved"
echo "--- End shared library check ---"

cd "{script.work_dir}"
mkdir -p logs
python {script.code_path} > >(tee logs/stdout.log) 2> >(tee logs/stderr.log >&2)
