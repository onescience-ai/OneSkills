# 安装流程 - 命令模板

本文件只放可渲染、可拷贝执行的命令模板。流程路由见 `../SKILL.md`；具体执行过程见对应的功能工作流文件。

## 占位符

| 占位符 | 来源 |
|--------|------|
| `{ssh_options}` | 可为空；需要时填 `-o StrictHostKeyChecking=no` 等 SSH 选项 |
| `{ssh_port}` | `onescience.json` 或 `~/.ssh/config` |
| `{ssh_identity}` | SSH 私钥文件 |
| `{ssh_user}` | SSH 用户名 |
| `{ssh_server}` | 优先 `hostname`，否则 `host` |
| `{env_name}` | `backend_profiles.json.defaults.env_name`，当前默认 `onescience311` |
| `{python_version}` | `backend_profiles.json.defaults.python_version`，当前默认 `3.11` |
| `{repo_url}` | `workspace_bootstrap_profiles.json.repo.repo_url` |
| `{repo_ref}` | `workspace_bootstrap_profiles.json.repo.repo_ref` |
| `{repo_dir}` | `~/` + `workspace_bootstrap_profiles.json.repo.repo_name`；当前稳定 profile 默认 `~/onescience` |
| `{dependency_selector}` | `install_domains.json.dependency_selector`，如 `earth`、`cfd`、`bio`、`matchem`、`all` |
| `{module_loads}` | 由 `backend_profiles.json.bootstrap.module_sequence` 渲染出的 `module load ... && ...` 命令串 |
| `{python_packages}` | 需要安装或校验的 Python 包列表，渲染为空格分隔参数 |

> `{ssh_options}`、`{repo_dir}`、`{dependency_selector}`、`{module_loads}`、`{python_packages}` 的渲染来源由 `../SKILL.md` 路由到对应工作流后确定。

## 目录

- `§0` 执行域检测
- `§1` 远端硬件探测
- `§1b` 就地硬件探测
- `§3` DCU 远端安装
- `§3b` DCU 远端当前环境安装
- `§4` DCU 远端验证
- `§4b` DCU 远端当前环境验证
- `§5` GPU 远端安装
- `§5b` GPU 远端当前环境安装
- `§6` GPU 远端验证
- `§6b` GPU 远端当前环境验证
- `§7` DCU 就地安装与验证
- `§7b` DCU 就地当前环境安装与验证
- `§8` GPU 就地安装与验证
- `§8b` GPU 就地当前环境安装与验证
- `§9` 远端 Python 包安装
- `§10` 远端 Python 包验证
- `§11` 本地非容器 Python 包安装
- `§12` 本地非容器 Python 包验证
- `§13` 本地容器内 Python 包安装
- `§14` 本地容器内 Python 包验证
- `§15` 远端 Python 包预检测（Conda 环境）
- `§15b` 远端 Python 包预检测（当前环境）
- `§16` 本地 Python 包预检测（Conda 环境）
- `§17` 当前环境 Python 包预检测
- `§18` 远端当前环境 Python 包安装
- `§19` 远端当前环境 Python 包验证

---

## §0 执行域检测

```bash
hostname && (test -f /.dockerenv && echo IN_CONTAINER=yes || echo IN_CONTAINER=no)
```

---

## §0b 镜像环境检测（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "(test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && echo === CURRENT_ENV_ONESCIENCE_CHECK === && ((python -m pip show onescience || pip show onescience) 2>/dev/null && echo CURRENT_ENV_HAS_ONESCIENCE=yes || echo CURRENT_ENV_HAS_ONESCIENCE=no) && echo === CONDA_ENVS === && (command -v conda >/dev/null 2>&1 && conda env list || echo conda:not_found) && echo === CONDA_ENV_ONESCIENCE_CHECK === && if command -v conda >/dev/null 2>&1; then for env in \$(conda env list | grep -v \"^#\" | awk \"{print \$1}\" | grep -v \"^$\"); do echo \"Checking env: \$env\" && conda activate \$env 2>/dev/null && ((python -m pip show onescience || pip show onescience) 2>/dev/null && echo \"ENV_NAME=\$env\") || true; done; fi"'
```

---

## §0c 镜像环境检测（local_slurm）

```bash
bash -lc "(test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && echo === CURRENT_ENV_ONESCIENCE_CHECK === && ((python -m pip show onescience || pip show onescience) 2>/dev/null && echo CURRENT_ENV_HAS_ONESCIENCE=yes || echo CURRENT_ENV_HAS_ONESCIENCE=no) && echo === CONDA_ENVS === && (command -v conda >/dev/null 2>&1 && conda env list || echo conda:not_found) && echo === CONDA_ENV_ONESCIENCE_CHECK === && if command -v conda >/dev/null 2>&1; then for env in \$(conda env list | grep -v \"^#\" | awk \"{print \$1}\" | grep -v \"^$\"); do echo \"Checking env: \$env\" && conda activate \$env 2>/dev/null && ((python -m pip show onescience || pip show onescience) 2>/dev/null && echo \"ENV_NAME=\$env\") || true; done; fi"
```

---

## §0d 环境检测（remote）

优先使用此方法。通过分步执行 SSH 命令检测环境，避免复杂的命令嵌套和 PowerShell 转义问题。如果此方法检测有问题，可使用 §0b 的完整检测命令。

检测步骤（禁止生成文件，直接执行命令）：

1. 检测当前环境的 Python 版本:
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} "python3 --version 2>&1 || python --version 2>&1 || echo python:not_found"
   ```

2. 检测当前环境是否有 onescience 包:
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} "python3 -m pip show onescience 2>&1 || echo onescience:not_found"
   ```

3. 检测当前环境是否有 torch 包:
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} "python3 -m pip show torch 2>&1 || echo torch:not_found"
   ```

4. 检测指定的 conda 环境是否存在:
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && ((conda env list 2>&1 || (source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda env list 2>&1)) | grep -w {env_name} || echo env:{env_name}:not_found)"'
   ```

5. 如果该 conda 环境存在，检测其中的包:
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && python -m pip show onescience && python -m pip show torch"'
   ```

执行说明：
- 按顺序执行上述命令，每个命令单独执行
- 根据每个命令的输出判断相应的状态
- 如果步骤 1-3 都成功（当前环境有 python + onescience + torch），可跳过后续步骤
- 如果步骤 4 返回 `env:{env_name}:not_found`，可跳过步骤 5

---

## §0e 环境检测（local）

优先使用此方法。通过分步执行本地命令检测环境。如果此方法检测有问题，可使用 §0c 的完整检测命令。

检测步骤（禁止生成文件，直接执行命令）：

1. 检测当前环境的 Python 版本:
   ```bash
   python3 --version 2>&1 || python --version 2>&1 || echo python:not_found
   ```

2. 检测当前环境是否有 onescience 包:
   ```bash
   python3 -m pip show onescience 2>&1 || echo onescience:not_found
   ```

3. 检测当前环境是否有 torch 包:
   ```bash
   python3 -m pip show torch 2>&1 || echo torch:not_found
   ```

4. 检测指定的 conda 环境是否存在
   ```bash
   bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && ((conda env list 2>&1 || (source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda env list 2>&1)) | grep -w {env_name} || echo env:{env_name}:not_found)"
   ```

5. 如果该 conda 环境存在，检测其中的包:
   ```bash
   bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && python -m pip show onescience && python -m pip show torch"
   ```

执行说明：同 §0d，按顺序执行，根据输出判断状态。

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

## §3 DCU 安装（remote_slurm，新建 conda 环境）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y || (source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda create -n {env_name} python={python_version} -y)) && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §3a DCU 安装（remote_slurm，复用已有 conda 环境）

**使用场景**：当 `conda_env_exists=true` 或检测到镜像环境时使用。

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §4 DCU 验证（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip list | grep torch && pip list | grep onescience"'
```

---

## §3b DCU 当前环境安装（remote_slurm，不创建/激活 conda）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (command -v conda >/dev/null 2>&1 || source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate) && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §4b DCU 当前环境验证（remote_slurm，不创建/激活 conda）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (command -v conda >/dev/null 2>&1 || source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate) && pip list | grep torch && pip list | grep onescience"'
```

---

## §5 GPU 安装（remote_slurm，新建 conda 环境）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y) && conda activate {env_name} && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §5a GPU 安装（remote_slurm，复用已有 conda 环境）

**使用场景**：当 `conda_env_exists=true` 或检测到镜像环境时使用。

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §6 GPU 验证（remote_slurm）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && conda activate {env_name} && pip list | grep torch && pip list | grep onescience"'
```

---

## §5b GPU 当前环境安装（remote_slurm，不创建/激活 conda）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"'
```

---

## §6b GPU 当前环境验证（remote_slurm，不创建/激活 conda）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && pip list | grep torch && pip list | grep onescience"'
```

---

## §7 DCU 安装与验证（local_slurm，新建 conda 环境）

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y || (source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda create -n {env_name} python={python_version} -y)) && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip list | grep torch && pip list | grep onescience"
```

---

## §7a DCU 安装与验证（local_slurm，复用已有 conda 环境）

**使用场景**：当 `conda_env_exists=true` 或检测到镜像环境时使用。

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip list | grep torch && pip list | grep onescience"
```

---

## §7b DCU 当前环境安装与验证（local_slurm，不创建/激活 conda）

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (command -v conda >/dev/null 2>&1 || source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate) && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load sghpcdas/25.6 && module load sghpc-mpi-gcc/26.3 && (command -v conda >/dev/null 2>&1 || source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate) && pip list | grep torch && pip list | grep onescience"
```

---

## §8 GPU 安装与验证（local_slurm，新建 conda 环境）

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && (conda env list | grep -w {env_name} >/dev/null 2>&1 || conda create -n {env_name} python={python_version} -y) && conda activate {env_name} && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && conda activate {env_name} && pip list | grep torch && pip list | grep onescience"
```

---

## §8a GPU 安装与验证（local_slurm，复用已有 conda 环境）

**使用场景**：当 `conda_env_exists=true` 或检测到镜像环境时使用。

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && conda activate {env_name} && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && conda activate {env_name} && pip list | grep torch && pip list | grep onescience"
```

---

## §8b GPU 当前环境安装与验证（local_slurm，不创建/激活 conda）

**安装：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && ([ -d {repo_dir}/.git ] || git clone {repo_url} {repo_dir}) && cd {repo_dir} && git fetch --all && git checkout {repo_ref} && git pull --ff-only && bash install.sh {dependency_selector}"
```

**验证：**

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && module load cuda/12.1 && module load gcc/11.2 && pip list | grep torch && pip list | grep onescience"
```

---

## §9 远端 Python 包安装

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip install {python_packages}"'
```

---

## §10 远端 Python 包验证

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip show {python_packages}"'
```

---

## §11 本地非容器 Python 包安装

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip install {python_packages}"
```

---

## §12 本地非容器 Python 包验证

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip show {python_packages}"
```

---

## §13 本地容器内 Python 包安装

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && pip install {python_packages}"
```

---

## §14 本地容器内 Python 包验证

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && pip show {python_packages}"
```

---

## §15 远端 Python 包预检测（Conda 环境）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip show {python_packages}"'
```

---

## §15b 远端 Python 包预检测（当前环境）

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && pip show {python_packages}"'
```

---

## §16 本地 Python 包预检测（Conda 环境）

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && { conda activate {env_name} || { source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate && conda activate {env_name}; }; } && pip show {python_packages}"
```

---

## §17 当前环境 Python 包预检测

```bash
bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && pip show {python_packages}"
```

---

## §18 远端当前环境 Python 包安装

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && pip install {python_packages}"'
```

---

## §19 远端当前环境 Python 包验证

```bash
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "set -o pipefail && (test -f ~/.bashrc && source ~/.bashrc || true) && {module_loads} && pip show {python_packages}"'
```
