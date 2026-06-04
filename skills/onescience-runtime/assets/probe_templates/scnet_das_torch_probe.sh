#!/bin/bash
# Safe SCnet DAS software-environment probe for onescience-runtime.
#
# Intended usage through scnet_mcp after region, queue, and remote path are
# confirmed:
#   bash scnet_das_torch_probe.sh
#
# This is a lightweight environment probe task. It must not run training or
# inference, install packages, or modify user runtime configuration.

emit() {
  printf '%s=%s\n' "$1" "$2"
}

emit scnet_probe_kind das_torch
emit submitted_training_job false
emit modified_runtime_config false

if [ -f /etc/profile ]; then
  # shellcheck disable=SC1091
  source /etc/profile >/dev/null 2>&1 || true
fi
if [ -f "$HOME/.bashrc" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.bashrc" >/dev/null 2>&1 || true
fi

if command -v conda >/dev/null 2>&1; then
  conda_env_name="${ONE_PROBE_CONDA_ENV:-onescience311}"
  emit conda_env "$conda_env_name"
  eval "$(conda shell.bash hook 2>/dev/null)" >/dev/null 2>&1 || true
  if conda activate "$conda_env_name" >/dev/null 2>&1; then
    emit conda_env_activated true
  else
    emit conda_env_activated false
  fi
else
  emit conda_env "${ONE_PROBE_CONDA_ENV:-onescience311}"
  emit conda_env_activated false
fi

emit conda_prefix "${CONDA_PREFIX:-}"
saved_python_bin=""
if [ -n "${CONDA_PREFIX:-}" ] && [ -x "${CONDA_PREFIX}/bin/python3" ]; then
  saved_python_bin="${CONDA_PREFIX}/bin/python3"
  emit saved_python_from_conda true
else
  emit saved_python_from_conda false
fi

if ! type module >/dev/null 2>&1; then
  for init_script in \
    /usr/share/Modules/init/bash \
    /etc/profile.d/modules.sh \
    /usr/share/lmod/lmod/init/bash
  do
    if [ -f "$init_script" ]; then
      # shellcheck disable=SC1090
      source "$init_script" >/dev/null 2>&1 || true
      break
    fi
  done
fi

if type module >/dev/null 2>&1; then
  emit module_cmd_available true
  module purge >/dev/null 2>&1 || true
  if [ -d /work2/share/sghpc_sdk/modulefiles ]; then
    module use /work2/share/sghpc_sdk/modulefiles >/dev/null 2>&1 || true
    emit sghpc_modulefiles_available true
  else
    emit sghpc_modulefiles_available false
  fi
  if module load sghpcdas/25.6 >/dev/null 2>&1; then
    emit das_module_loaded true
    emit das_module sghpcdas/25.6
  else
    emit das_module_loaded false
    emit das_module sghpcdas/25.6
  fi
  if module load sghpc-mpi-gcc/26.3 >/dev/null 2>&1; then
    emit hpcsdk_module_loaded true
    emit hpcsdk_module sghpc-mpi-gcc/26.3
  else
    emit hpcsdk_module_loaded false
    emit hpcsdk_module sghpc-mpi-gcc/26.3
  fi
else
  emit module_cmd_available false
  emit das_module_loaded false
  emit das_module sghpcdas/25.6
  emit hpcsdk_module_loaded false
  emit hpcsdk_module sghpc-mpi-gcc/26.3
  emit sghpc_modulefiles_available false
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

python_bin="$saved_python_bin"
if [ -z "$python_bin" ]; then
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      python_bin="$(command -v "$candidate")"
      break
    fi
  done
fi

if [ -n "$python_bin" ]; then
  emit python_ready true
  emit python_bin "$python_bin"
  emit python_executable "$python_bin"
  "$python_bin" - <<'PY'
import json
payload = {
    "torch_ready": False,
    "torch_version": "not_imported",
    "dcu_runtime_ready": False,
    "torch_hip_runtime_ready": False,
    "torch_import_ok": False,
}
try:
    import torch
    payload["torch_ready"] = True
    payload["torch_import_ok"] = True
    payload["torch_version"] = getattr(torch, "__version__", "unknown")
    payload["torch_hip_runtime_ready"] = bool(getattr(torch, "version", None) and getattr(torch.version, "hip", None))
    payload["dcu_runtime_ready"] = payload["torch_hip_runtime_ready"]
except Exception as exc:
    payload["torch_error"] = type(exc).__name__ + ": " + str(exc)
for key, value in payload.items():
    print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
PY
else
  emit python_ready false
  emit python_bin not_available
  emit python_executable not_available
  emit torch_ready false
  emit torch_version not_available
  emit torch_import_ok false
  emit torch_hip_runtime_ready false
  emit dcu_runtime_ready false
fi
