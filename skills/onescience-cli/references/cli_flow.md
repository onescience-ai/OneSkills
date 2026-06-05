# CLI Flow — 命令模板

本文件只放可渲染、可拷贝执行的命令模板。流程裁决与阶段细则见 `./cli_rules.md`；门禁与阶段轮廓见 `../SKILL.md`。

## 占位符

| 占位符 | 来源 |
|--------|------|
| `{ssh_host_alias}` | 来自 `~/.ssh/config` 的 Host 条目（优先使用） |
| `{ssh_options}` | 固定为 `-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null` |
| `{ssh_port}` | `onescience.json` 或 `~/.ssh/config` |
| `{ssh_identity}` | SSH identity file |
| `{ssh_user}` | SSH 用户名 |
| `{ssh_server}` | 优先 `hostname`，否则 `host` |
| `{onescience_subcommand}` | 用户请求的 onescience 子命令 |
| `{onescience_args}` | onescience 子命令后的附加参数 |
| `{env_name}` | conda 环境名，用于环境检查（默认 `onescience311`） |
| `{remote_work_dir}` | 来自 `onescience.json` 的 `runtime.remote.remote_work_dir`。**必须指向包含 `setup.py` 和 `examples/` 目录的项目根目录**，如 `/public/home/zongwei/onescience`，默认 `/public/home/{ssh_user}` |
| `{onescience_datasets_dir}` | 数据集目录，来自 `onescience.json` 的 `runtime.script.env_vars.ONESCIENCE_DATASETS_DIR` |
| `{onescience_models_dir}` | 模型目录，来自 `onescience.json` 的 `runtime.script.env_vars.ONESCIENCE_MODELS_DIR` |

## 目录

- `§0` 执行域检测
- `§1` 远端环境探测（方案B：Host 别名 + heredoc）
- `§1b` 就地环境探测
- `§2` 计算节点判定（方案B）
- `§3` 环境加载检查（方案B）
- `§4` onescience 通用执行命令（远端，compute 级别）
- `§5` onescience 快速执行通道（lightweight 级别）
- `§6` onescience 普通执行命令（远端，normal 级别）
- `§7` onescience 通用执行命令（就地）

---

## §0 执行域检测

```bash
hostname && (test -f /.dockerenv && echo IN_CONTAINER=yes || echo IN_CONTAINER=no)
```

---

## §1 远端环境探测（remote_slurm）

**方案B**：使用 SSH Host 别名 + heredoc，避免 PowerShell 管道和引号解析问题。

### Host 别名模式（优先）

当 `~/.ssh/config` 中已配置完整 Host 条目时使用。

```bash
ssh {ssh_options} {ssh_host_alias} 'bash -s' << 'EOF'
(test -f ~/.bashrc && source ~/.bashrc || true)
echo === NVIDIA ===
(command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -5 || echo nvidia-smi:not_in_PATH)
echo === HIPCC ===
(command -v hipcc >/dev/null 2>&1 && hipcc --version | head -2 || echo hipcc:not_found)
echo === TOOLKIT_DIRS ===
(ls -d /opt/dtk-* /opt/rocm* /usr/local/cuda* 2>/dev/null | head -5 || echo toolkit_dirs:none)
echo === DEVICES ===
(ls -la /dev/kfd 2>/dev/null || echo dev_kfd:none)
echo === MODULES ===
(command -v module >/dev/null 2>&1 && module avail 2>&1 | grep -iE "dtk|sghpc|rocm|cuda" | head -15 || echo module:not_found_or_no_match)
EOF
```

### 完整参数模式（备用）

当无法使用 Host 别名时使用。注意：此模式在 Windows PowerShell 中可能因管道符 `|` 和嵌套引号导致解析错误，建议优先使用 Host 别名模式。

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "(test -f ~/.bashrc && source ~/.bashrc || true) && echo === NVIDIA === && (command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -5 || echo nvidia-smi:not_in_PATH) && echo === HIPCC === && (command -v hipcc >/dev/null 2>&1 && hipcc --version | head -2 || echo hipcc:not_found) && echo === TOOLKIT_DIRS === && (ls -d /opt/dtk-* /opt/rocm* /usr/local/cuda* 2>/dev/null | head -5 || echo toolkit_dirs:none) && echo === DEVICES === && (ls -la /dev/kfd 2>/dev/null || echo dev_kfd:none) && echo === MODULES === && (command -v module >/dev/null 2>&1 && module avail 2>&1 | grep -iE "dtk|sghpc|rocm|cuda" | head -15 || echo module:not_found_or_no_match)"'
```

---

## §1b 就地环境探测（local_slurm）

```bash
bash -lc "(test -f ~/.bashrc && source ~/.bashrc || true) && echo === NVIDIA === && (command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -5 || echo nvidia-smi:not_in_PATH) && echo === HIPCC === && (command -v hipcc >/dev/null 2>&1 && hipcc --version | head -2 || echo hipcc:not_found) && echo === TOOLKIT_DIRS === && (ls -d /opt/dtk-* /opt/rocm* /usr/local/cuda* 2>/dev/null | head -5 || echo toolkit_dirs:none) && echo === DEVICES === && (ls -la /dev/kfd 2>/dev/null || echo dev_kfd:none) && echo === MODULES === && (command -v module >/dev/null 2>&1 && module avail 2>&1 | grep -iE \"dtk|sghpc|rocm|cuda\" | head -15 || echo module:not_found_or_no_match)"
```

---

## §2 计算节点判定

### 远端判定（remote_slurm）

**方案B**：Host 别名模式（优先）

```bash
ssh {ssh_options} {ssh_host_alias} 'bash -s' << 'EOF'
echo === SLURM_VARS ===
echo SLURM_NODEID=${SLURM_NODEID:-not_set}
echo SLURM_JOB_ID=${SLURM_JOB_ID:-not_set}
echo SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-not_set}
echo SLURM_NTASKS=${SLURM_NTASKS:-not_set}
echo SLURM_CLUSTER_NAME=${SLURM_CLUSTER_NAME:-not_set}
echo === HOSTNAME ===
hostname
echo === COMPUTE_NODE_CHECK ===
(scontrol show node $(hostname) 2>/dev/null | head -5 || echo scontrol:not_available_or_not_compute_node)
EOF
```

完整参数模式（备用）：

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "echo === SLURM_VARS === && echo SLURM_NODEID=${SLURM_NODEID:-not_set} && echo SLURM_JOB_ID=${SLURM_JOB_ID:-not_set} && echo SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-not_set} && echo SLURM_NTASKS=${SLURM_NTASKS:-not_set} && echo SLURM_CLUSTER_NAME=${SLURM_CLUSTER_NAME:-not_set} && echo === HOSTNAME === && hostname && echo === COMPUTE_NODE_CHECK === && (scontrol show node $(hostname) 2>/dev/null | head -5 || echo scontrol:not_available_or_not_compute_node)"'
```

### 就地判定（local_slurm）

```bash
bash -lc "echo === SLURM_VARS === && echo SLURM_NODEID=\${SLURM_NODEID:-not_set} && echo SLURM_JOB_ID=\${SLURM_JOB_ID:-not_set} && echo SLURM_JOB_NODELIST=\${SLURM_JOB_NODELIST:-not_set} && echo SLURM_NTASKS=\${SLURM_NTASKS:-not_set} && echo SLURM_CLUSTER_NAME=\${SLURM_CLUSTER_NAME:-not_set} && echo === HOSTNAME === && hostname && echo === COMPUTE_NODE_CHECK === && (scontrol show node \$(hostname) 2>/dev/null | head -5 || echo scontrol:not_available_or_not_compute_node)"
```

---

## §3 环境加载检查

### 远端检查（remote_slurm）

**方案B**：Host 别名模式（优先）

```bash
ssh {ssh_options} {ssh_host_alias} 'bash -s' << 'SHEOF'
set -o pipefail
(test -f ~/.bashrc && source ~/.bashrc || true)
echo === CONDA_ENV ===
(conda info --envs 2>/dev/null | grep "^{env_name}" || echo conda_env:{env_name}_not_found)
echo === ACTIVE_ENV ===
(echo $CONDA_DEFAULT_ENV || echo conda_not_active)
echo === MODULES_LOADED ===
(module list 2>&1 | head -20 || echo module_not_available)
echo === ONESCIENCE_PKG ===
(python -c "import onescience; print(onescience.__version__)" 2>&1 || echo onescience_pkg:not_importable)
SHEOF
```

完整参数模式（备用）：

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && echo === CONDA_ENV === && (conda info --envs 2>/dev/null | grep \"^{env_name}\" || echo conda_env:{env_name}_not_found) && echo === ACTIVE_ENV === && (echo $CONDA_DEFAULT_ENV || echo conda_not_active) && echo === MODULES_LOADED === && (module list 2>&1 | head -20 || echo module_not_available) && echo === ONESCIENCE_PKG === && (python -c \"import onescience; print(onescience.__version__)\" 2>&1 || echo onescience_pkg:not_importable)"'
```

### 就地检查（local_slurm）

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && echo === CONDA_ENV === && (conda info --envs 2>/dev/null | grep \"^{env_name}\" || echo conda_env:{env_name}_not_found) && echo === ACTIVE_ENV === && (echo \$CONDA_DEFAULT_ENV || echo conda_not_active) && echo === MODULES_LOADED === && (module list 2>&1 | head -20 || echo module_not_available) && echo === ONESCIENCE_PKG === && (python -c \"import onescience; print(onescience.__version__)\" 2>&1 || echo onescience_pkg:not_importable)"
```

---

## §4 onescience 通用执行命令（远端，compute 级别）

仅在计算节点上执行。若当前不在计算节点上，应交由 `onescience-runtime` 通过 sbatch 提交作业到计算节点执行。

**方案B**：Host 别名模式（优先）

```bash
ssh {ssh_options} {ssh_host_alias} 'bash -s' << 'EOF'
source ~/.bashrc
export ONESCIENCE_DATASETS_DIR={onescience_datasets_dir}
export ONESCIENCE_MODELS_DIR={onescience_models_dir}
export WORLD_SIZE={world_size}
export MASTER_ADDR={master_addr}
export MASTER_PORT={master_port}
cd {remote_work_dir}
onescience {onescience_subcommand} {onescience_args}
EOF
```

完整参数模式（备用）：

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "source ~/.bashrc && export ONESCIENCE_DATASETS_DIR={onescience_datasets_dir} && export ONESCIENCE_MODELS_DIR={onescience_models_dir} && export WORLD_SIZE={world_size} && export MASTER_ADDR={master_addr} && export MASTER_PORT={master_port} && cd {remote_work_dir} && onescience {onescience_subcommand} {onescience_args}"'
```

---

## §5 onescience 快速执行通道（lightweight 级别）

适用于 `lightweight` 级别命令（help/version/list/info/config show）。无需环境探测、计算节点判定和环境加载检查。

### 远端执行（remote_slurm）

**方案B**：Host 别名模式（优先）

```bash
ssh {ssh_options} {ssh_host_alias} 'bash -s' << 'EOF'
source ~/.bashrc
cd {remote_work_dir}
onescience {onescience_subcommand} {onescience_args}
EOF
```

完整参数模式（备用）：

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "source ~/.bashrc && cd {remote_work_dir} && onescience {onescience_subcommand} {onescience_args}"'
```

### 就地执行（local_slurm）

```bash
bash -lc "source ~/.bashrc && cd {remote_work_dir} && onescience {onescience_subcommand} {onescience_args}"
```

---

## §6 onescience 普通执行命令（远端，normal 级别）

适用于 `normal` 级别命令（log/status/upgrade/remock/config set）。已在登录节点确认环境可用后直接执行。

**方案B**：Host 别名模式（优先）

```bash
ssh {ssh_options} {ssh_host_alias} 'bash -s' << 'EOF'
source ~/.bashrc
cd {remote_work_dir}
onescience {onescience_subcommand} {onescience_args}
EOF
```

完整参数模式（备用）：

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "source ~/.bashrc && cd {remote_work_dir} && onescience {onescience_subcommand} {onescience_args}"'
```

---

## §7 onescience 通用执行命令（就地）

### compute 级别（就地）

```bash
bash -lc "source ~/.bashrc && export ONESCIENCE_DATASETS_DIR={onescience_datasets_dir} && export ONESCIENCE_MODELS_DIR={onescience_models_dir} && export WORLD_SIZE={world_size} && export MASTER_ADDR={master_addr} && export MASTER_PORT={master_port} && cd {remote_work_dir} && onescience {onescience_subcommand} {onescience_args}"
```

### lightweight / normal 级别（就地）

```bash
bash -lc "source ~/.bashrc && cd {remote_work_dir} && onescience {onescience_subcommand} {onescience_args}"
```
