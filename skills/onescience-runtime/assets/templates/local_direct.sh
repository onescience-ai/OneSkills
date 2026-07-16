#!/bin/bash
set -euo pipefail

mkdir -p logs

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

cd "{script.work_dir}"
python {script.code_path}
