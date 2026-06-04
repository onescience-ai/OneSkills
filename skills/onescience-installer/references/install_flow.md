# Install Flow — 命令模板

本文件只放可渲染、可拷贝执行的命令模板。流程裁决与阶段细则见 `./install_rules.md`；硬门禁与阶段轮廓见 `../SKILL.md`。

## 占位符

| 占位符 | 来源 |
|--------|------|
| `{ssh_options}` | 可为空；需要时填 `-o StrictHostKeyChecking=no` 等 SSH 选项 |
| `{ssh_port}` | `onescience.json` 或 `~/.ssh/config` |
| `{ssh_identity}` | SSH identity file |
| `{ssh_user}` | SSH 用户名 |
| `{ssh_server}` | 优先 `hostname`，否则 `host` |
| `{env_name}` | `backend_profiles.json.defaults.env_name`，当前默认 `onescience311` |
| `{python_version}` | `backend_profiles.json.defaults.python_version`，当前默认 `3.11` |
| `{repo_url}` | `workspace_bootstrap_profiles.json.repo.repo_url` |
| `{repo_ref}` | `workspace_bootstrap_profiles.json.repo.repo_ref` |
| `{repo_dir}` | `~/` + `workspace_bootstrap_profiles.json.repo.repo_name`；当前 stable profile 默认 `~/onescience` |
| `{dependency_selector}` | `install_domains.json.dependency_selector`，如 `earth`、`cfd`、`bio`、`matchem`、`all` |

> `{ssh_options}`、`{repo_dir}`、`{dependency_selector}` 的完整渲染规则见 `./install_rules.md` §3.3。

## 目录

- `§0` 执行域检测
- `§1` 远端硬件探测
- `§1b` 就地硬件探测
- `§3` DCU 远端安装
- `§4` DCU 远端验证
- `§5` GPU 远端安装
- `§6` GPU 远端验证
- `§7` DCU 就地安装与验证
- `§8` GPU 就地安装与验证

---

## §0 执行域检测

```bash
hostname && (test -f /.dockerenv && echo IN_CONTAINER=yes || echo IN_CONTAINER=no)
```

---

## §1 硬件探测（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "(test -f ~/.bashrc && source ~/.bashrc || true) && echo === NVIDIA === && (command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -5 || echo nvidia-smi:not_in_PATH) && echo === HIPCC === && (command -v hipcc >/dev/null 2>&1 && hipcc --version | head -2 || echo hipcc:not_found) && echo === TOOLKIT_DIRS === && (ls -d /opt/dtk-* /opt/rocm* /usr/local/cuda* 2>/dev/null | head -5 || echo toolkit_dirs:none) && echo === DEVICES === && (ls -la /dev/kfd 2>/dev/null || echo dev_kfd:none) && echo === MODULES === && (command -v module >/dev/null 2>&1 && module avail 2>&1 | grep -iE \"dtk|sghpc|rocm|cuda\" | head -15 || echo module:not_found_or_no_match)"'
```

---

## §1b 硬件探测（local_slurm）

```bash
bash -lc "(test -f ~/.bashrc && source ~/.bashrc || true) && echo === NVIDIA === && (command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi | head -5 || echo nvidia-smi:not_in_PATH) && echo === HIPCC === && (command -v hipcc >/dev/null 2>&1 && hipcc --version | head -2 || echo hipcc:not_found) && echo === TOOLKIT_DIRS === && (ls -d /opt/dtk-* /opt/rocm* /usr/local/cuda* 2>/dev/null | head -5 || echo toolkit_dirs:none) && echo === DEVICES === && (ls -la /dev/kfd 2>/dev/null || echo dev_kfd:none) && echo === MODULES === && (command -v module >/dev/null 2>&1 && module avail 2>&1 | grep -iE \"dtk|sghpc|rocm|cuda\" | head -15 || echo module:not_found_or_no_match)"
```

---

## §3 DCU 安装（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y || (source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda create -n {env_name} python={python_version} -y)) && conda activate {env_name} && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §4 DCU 验证（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && conda activate {env_name} && pip list | grep torch && pip list | grep onescience"'
```

---

## §5 GPU 安装（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y) && conda activate {env_name} && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §6 GPU 验证（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && conda activate {env_name} && pip list | grep torch && pip list | grep onescience"'
```

---

## §7 DCU 安装与验证（local_slurm）

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y || (source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda create -n {env_name} python={python_version} -y)) && conda activate {env_name} && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && conda activate {env_name} && pip list | grep torch && pip list | grep onescience"
```

---

## §8 GPU 安装与验证（local_slurm）

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y) && conda activate {env_name} && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && conda activate {env_name} && pip list | grep torch && pip list | grep onescience"
```
