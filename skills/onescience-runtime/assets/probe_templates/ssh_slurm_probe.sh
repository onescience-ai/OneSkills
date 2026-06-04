#!/bin/sh
# Safe SSH/SLURM probe signal collector for onescience-runtime.
#
# Intended usage:
#   ONE_PROBE_PARTITION=<partition> \
#   ONE_PROBE_MODULES="sghpcdas/25.6 sghpc-mpi-gcc/26.3" \
#   ONE_PROBE_CONDA_ENV=<env_name> \
#   ONE_PROBE_PRESERVE_CONDA_PYTHON=true \
#   ONE_PROBE_WORK_DIR=<remote_dir> \
#   sh ssh_slurm_probe.sh
#
# This script emits key=value facts for runtime normalization. It must not submit
# jobs, install packages, modify runtime config, or assume that user text is a
# confirmed environment fact.

set -eu

emit() {
  printf '%s=%s\n' "$1" "$2"
}

emit_cmd_available() {
  key="$1"
  cmd="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    emit "$key" true
  else
    emit "$key" false
  fi
}

emit ssh_connectivity true
emit host "$(hostname 2>/dev/null || printf unknown)"
emit kernel "$(uname -s 2>/dev/null || printf unknown)"
emit cpu_arch "$(uname -m 2>/dev/null || printf unknown)"

emit_cmd_available sbatch_available sbatch
emit_cmd_available sinfo_available sinfo
emit_cmd_available squeue_available squeue
emit_cmd_available python3_available python3
emit_cmd_available conda_available conda

if ! type module >/dev/null 2>&1; then
  for init_script in \
    /usr/share/Modules/init/sh \
    /usr/share/Modules/init/profile.sh \
    /etc/profile.d/modules.sh \
    /usr/share/lmod/lmod/init/sh
  do
    if [ -f "$init_script" ]; then
      . "$init_script" >/dev/null 2>&1 || true
      break
    fi
  done
fi

if type module >/dev/null 2>&1; then
  emit module_cmd_available true
else
  emit module_cmd_available false
fi

saved_python_bin=""
preserve_conda_python="${ONE_PROBE_PRESERVE_CONDA_PYTHON:-false}"
emit preserve_conda_python "$preserve_conda_python"
if [ -n "${ONE_PROBE_CONDA_ENV:-}" ]; then
  emit conda_env "$ONE_PROBE_CONDA_ENV"
  if command -v conda >/dev/null 2>&1; then
    eval "$(conda shell.posix hook 2>/dev/null)" >/dev/null 2>&1 || true
    if conda activate "$ONE_PROBE_CONDA_ENV" >/dev/null 2>&1; then
      emit conda_env_activated true
    else
      emit conda_env_activated false
    fi
  else
    emit conda_env_activated false
  fi
else
  emit conda_env none
  emit conda_env_activated not_requested
fi

emit conda_prefix "${CONDA_PREFIX:-}"
if [ "$preserve_conda_python" = "true" ] && [ -n "${CONDA_PREFIX:-}" ] && [ -x "${CONDA_PREFIX}/bin/python3" ]; then
  saved_python_bin="${CONDA_PREFIX}/bin/python3"
  emit saved_python_from_conda true
else
  emit saved_python_from_conda false
fi

if [ -n "${ONE_PROBE_MODULES:-}" ]; then
  emit module_sequence "$ONE_PROBE_MODULES"
  if type module >/dev/null 2>&1; then
    module_load_success=true
    for module_name in $ONE_PROBE_MODULES; do
      if ! module load "$module_name" >/dev/null 2>&1; then
        module_load_success=false
      fi
    done
    emit module_load_success "$module_load_success"
  else
    emit module_load_success false
  fi
else
  emit module_sequence none
  emit module_load_success not_requested
fi

if command -v hipcc >/dev/null 2>&1; then
  emit dtk_runtime_ready true
  emit dtk_runtime_evidence hipcc
  dcu_user_space_ready=true
elif printf '%s\n' "${LD_LIBRARY_PATH:-}" | grep -Eiq 'dtk|sghpc|hpc_sdk|galaxy|hip'; then
  emit dtk_runtime_ready true
  emit dtk_runtime_evidence LD_LIBRARY_PATH
  dcu_user_space_ready=true
else
  emit dtk_runtime_ready false
  emit dtk_runtime_evidence not_detected
  dcu_user_space_ready=false
fi

if [ "${LD_LIBRARY_PATH:-}" != "" ] && printf '%s\n' "${LD_LIBRARY_PATH:-}" | grep -Eiq 'sghpc|hpc_sdk'; then
  emit sghpc_runtime_ready true
  dcu_user_space_ready=true
else
  emit sghpc_runtime_ready false
fi

emit dcu_user_space_ready "$dcu_user_space_ready"

if command -v sbatch >/dev/null 2>&1; then
  emit sbatch_version "$(sbatch --version 2>/dev/null | head -n 1 || printf unknown)"
fi

if [ -n "${ONE_PROBE_PARTITION:-}" ]; then
  if command -v sinfo >/dev/null 2>&1; then
    if sinfo -h -p "$ONE_PROBE_PARTITION" >/dev/null 2>&1; then
      emit partition_accessible true
    else
      emit partition_accessible false
    fi
  else
    emit partition_accessible unknown
  fi
fi

if command -v rocm-smi >/dev/null 2>&1; then
  emit accelerator_vendor amd
  emit accelerator_kind dcu
  emit visibility_env HIP_VISIBLE_DEVICES
elif command -v nvidia-smi >/dev/null 2>&1; then
  emit accelerator_vendor nvidia
  emit accelerator_kind gpu
  emit visibility_env CUDA_VISIBLE_DEVICES
else
  emit accelerator_vendor none
  emit accelerator_kind cpu
  emit visibility_env none
fi

emit_cmd_available python_after_env_available python3

python_bin="$saved_python_bin"
if [ -z "$python_bin" ] && command -v python3 >/dev/null 2>&1; then
  python_bin="$(command -v python3)"
elif [ -z "$python_bin" ] && command -v python >/dev/null 2>&1; then
  python_bin="$(command -v python)"
fi

if [ -n "$python_bin" ]; then
  emit python_ready true
  emit python_bin "$python_bin"
  if "$python_bin" - <<'PY' >/dev/null 2>&1
import torch
PY
  then
    emit torch_ready true
    "$python_bin" - <<'PY' 2>/dev/null || true
import torch
hip_ready = bool(getattr(torch, "version", None) and getattr(torch.version, "hip", None))
print("torch_import_ok=true")
print(f"torch_hip_runtime_ready={str(hip_ready).lower()}")
PY
  else
    emit torch_ready false
    emit torch_import_ok false
    emit torch_hip_runtime_ready false
  fi
else
  emit python_ready false
  emit python_bin not_available
  emit torch_ready false
  emit torch_import_ok false
  emit torch_hip_runtime_ready false
fi

if [ -n "${ONE_PROBE_WORK_DIR:-}" ]; then
  if [ -d "$ONE_PROBE_WORK_DIR" ] && [ -w "$ONE_PROBE_WORK_DIR" ]; then
    probe_file="$ONE_PROBE_WORK_DIR/.onescience_probe_$$"
    if : > "$probe_file" 2>/dev/null; then
      rm -f "$probe_file" 2>/dev/null || true
      emit work_dir_writable true
    else
      emit work_dir_writable false
    fi
  else
    emit work_dir_writable false
  fi
fi

emit submitted_job false
emit modified_runtime_config false
