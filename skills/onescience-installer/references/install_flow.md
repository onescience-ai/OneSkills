# Install Flow

本文件是 `onescience-installer` 的完整操作手册。包含：远端硬件探测策略、支持边界、预检规则、两阶段安装命令骨架、验证约束。

---

## 0. SSH 引号规范（贯穿全文）

**所有 SSH 命令固定使用以下格式，不再逐处重复：**

```
ssh {user}@{host} "远程命令串"
```

- 外层**双引号** `"…"` 包裹整段远程 shell 命令
- 内层 `python -c` 的代码用**单引号** `'…'`
- 示例：`ssh user@host "python -c 'import torch; print(torch.__version__)'"`

---

## 0.5 远端主机发现

**本文所有 `{user}` 和 `{host}` 变量必须在本节确定，才能进入第 1 节硬件探测。** 按以下优先级链执行：

1. **`onescience.json` → `runtime.remote`** → 提取 `hostname`、`port`、`user`、`identity_file`
2. **`~/.ssh/config`** → 列举有效 `Host` 条目，让用户选择
3. **MCP host 对象** → 检查平台是否提供了 SSH 连接上下文
4. **询问用户** → 以上均无，请用户提供 SSH 地址

未找到 → `blocked`，报告缺少远程环境。

---

## 1. 远端硬件探测

**目标：** 登录远端后通过一次综合探测，判断硬件类型 → 选择安装骨架（DCU / GPU / 阻断）。

### 1.1 一次综合探测

```
ssh {user}@{host} "
    echo '=== NVIDIA ===' && (nvidia-smi 2>/dev/null | head -5 || echo 'nvidia-smi: no device')
    echo '=== ROCM ===' && (rocm-smi --showproductname 2>/dev/null || echo 'rocm-smi: not found')
    echo '=== HIPCC ===' && (which hipcc 2>/dev/null && hipcc --version | head -2 || echo 'hipcc: not found')
    echo '=== DTK/ROCM/CUDA DIR ===' && ls -d /opt/dtk-* /opt/rocm* /usr/local/cuda* 2>/dev/null | head -5
    echo '=== DEV ===' && (ls -la /dev/kfd 2>/dev/null || echo 'no /dev/kfd') && (cat /proc/driver/nvidia/version 2>/dev/null || echo 'no nvidia driver')
    echo '=== MODULE ===' && (module avail 2>/dev/null | grep -iE 'dtk|sghpc|rocm|cuda' | head -10 || echo 'no relevant modules')
"
```

### 1.2 判断逻辑

| 输出信号 | 结论 |
|----------|------|
| `nvidia-smi` 返回 GPU 设备 + `/usr/local/cuda` 存在 | **GPU** → 走 GPU 骨架 |
| `rocm-smi` 或 `hipcc` 存在 + `/opt/dtk-*` 或 `/dev/kfd` 存在 | **DCU** → 走 DCU 骨架 |
| 两者都不明确 | **CPU** → `blocked`（暂不支持） |

---

## 2 当前支持边界

以 `skills/onescience-runtime/assets/backend_specs.json` 的 **`support_matrix.installer`** 为准裁决是否允许执行仓库级安装链路：

- 当 **`slurm_dcu`** 的 `installer.status` 为 **`supported`** 时，可使用本文 `dcu_remote_install` 两阶段命令
- 当 **`slurm_gpu`** 的 `installer.status` 为 **`unsupported_for_now`** 时，不得以「已写好命令模板」为由在 GPU 后上假称可完整执行安装矩阵；应向用户明示矩阵尚不支持
- 下文仍收录 `gpu_remote_install` 命令骨架，供矩阵切至 `supported` 后直接采用

---

## 3 输入层与约束

### 3.1 输入层

安装链路当前消费 5 层输入：

1. **hardware backend** — 来自 `skills/onescience-runtime/assets/backend_specs.json` 的 `support_matrix.installer`
2. **installer backend profile** — 来自 `../assets/backend_profiles.json`（模块、conda、verify 配置）
3. **workspace bootstrap profile** — 来自 `../assets/workspace_bootstrap_profiles.json`（仓库来源、工作树复用、安装入口）
4. **install domain profile** — 来自 `../assets/install_domains.json`（领域依赖意图与 `dependency_selector`）
5. **host readiness / precheck** — 来自本 skill 自行远端探测的 driver/runtime 状态

### 3.2 输入约束

当前标准 install request 只包含 `domain`。不要把以下内容当成用户请求层输入，它们属于 backend profile 或 workspace bootstrap profile 的实现细节：

- `python_version`
- `env_name`
- `repo_name`
- `repo_url`
- `repo_ref`
- `allow_reuse_existing_worktree`

---

## 4 驱动层边界

`onescience-installer` 当前只负责 user-space 安装，不负责：
- 安装或升级内核态驱动
- 加载内核模块
- 修改系统级 CUDA / ROCm 部署
- 申请 root 权限或重启节点

进入安装前至少要确认（通过第 4 轮探测）：

| 条件 | 含义 |
|------|------|
| `driver_stack.driver_ready` | 内核态驱动已正常加载 |
| `driver_stack.user_space_ready` | 用户态运行时已就绪 |
| `capability_readiness.compiler_ready` | 编译器可用（gcc/hipcc/nvcc） |
| `capability_readiness.torch_ready` | PyTorch 基线可用 |
| `capability_readiness.distributed_runtime_ready` | MPI 或分布式运行时可加载 |

若上述条件不满足，直接阻断并提示平台侧先处理驱动栈。

---

## 5 安装流程概览

所有安装操作**必须**在远程环境执行，不得在本地执行。

### 5.1 执行顺序

1. **远端硬件探测**（本章第 1 节）—— 通过多轮 SSH 只读探测确定 Hardware backend ID
2. **按 `support_matrix.installer` 判定**是否允许执行
3. **读取对应 installer backend profile**（`backend_profiles.json`）
4. **读取默认 workspace bootstrap profile**（`workspace_bootstrap_profiles.json`）
5. **检查远端运行时就绪状态**（第 4 轮探测 + driver_stack 条件）
6. **确认安装领域**（若用户未指定则询问）
7. **仅选择与本 hardware backend 匹配的一个安装命令骨架**（DCU 与 GPU 互不混用）
8. **准备并执行远程安装命令**（阶段 1）
9. **准备并执行远程验证命令**（阶段 2）

### 5.2 两阶段原则

- **阶段 1**：一个远程命令完成环境准备、工作区同步与领域安装
- **阶段 2**：一个独立远程命令做安装验证

---

## 6 `dcu_remote_install` 阶段 1：安装命令骨架

```bash
module load sghpcdas/25.6
source ~/.bashrc
module load sghpc-mpi-gcc/26.3
# 若 conda create 失败，在此插入 fallback:
# source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate
conda create -n onescience311 python=3.11 -y
conda activate onescience311

if [ ! -d onescience ]; then
  git clone https://gitee.com/onescience-ai/onescience.git
fi
cd onescience
git fetch --all
git checkout main
git pull --ff-only

# dependency_selector 由 install_domains.json 提供
bash install.sh {dependency_selector}
```

说明：
- `{dependency_selector}` 渲染自 `install_domains.json` 对应领域的值
- `all` 场景应使用 workspace bootstrap profile 的默认 selector 省略规则

---

## 7 `dcu_remote_install` 阶段 2：验证命令

由当前环境对目标 Host 一条非交互 `ssh user@host "…"` 发起：

```bash
ssh {user}@{host} "module load sghpcdas/25.6 && source ~/.bashrc && module load sghpc-mpi-gcc/26.3 && conda activate onescience311 && python -c 'import torch; print(torch.__version__)' && python -c 'import onescience; print(onescience.__version__)'"
```

### 7.1 验证范围（严格）

- **仅**上述两条 `python -c`：打印 `torch` 与 `onescience` 的版本字符串
- **不得**以「更稳妥」为由追加其它包导入、目录存在性、`pip list`、`conda list` 节选等检查，除非用户在本轮对话中明确要求

### 7.2 引号规范

引号层次见**第 0 节 §0**。

---

## 8 `gpu_remote_install` 阶段 1：安装命令骨架

```bash
source ~/.bashrc
conda create -n onescience311 python=3.11 -y
conda activate onescience311

pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
pip install apex==1.4.0
pip install onnxruntime==1.19.2
pip install dgl==2.1.0
pip install jax==0.4.34
pip install jax_rocm60_pjrt==0.4.34
pip install jax_rocm60_pjrt==0.4.35
pip install jaxlib==0.4.34
pip install jax_triton==0.2.0
pip install triton==3.1.0
export LD_LIBRARY_PATH=~/onescience/cudnn/lib:${LD_LIBRARY_PATH}
export CPATH=~/onescience/cudnn/include:${CPATH}
export PATH=/usr/local/cuda-12.2/bin:${PATH}
export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:${LD_LIBRARY_PATH}
source ~/compiler/gcc-9.3.0/env_gcc9.3.0.sh
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib/python3.11/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

if [ ! -d ~/onescience ]; then
  git clone https://gitee.com/onescience-ai/onescience.git ~/onescience
fi
cd ~/onescience
git fetch --all
git checkout main
git pull --ff-only
bash install.sh {dependency_selector}
```

---

## 9 `gpu_remote_install` 阶段 2：验证命令

```bash
ssh {user}@{host} "source ~/.bashrc && conda activate onescience311 && python -c 'import torch; print(torch.__version__)' && python -c 'import onescience; print(onescience.__version__)'"
```

验证范围、引号规范与 `dcu_remote_install` 阶段 2 一致（见第 0 节 §0）。

---

## 10 安装注意事项

- DCU 与 GPU 使用不同安装骨架；以远端硬件探测结论与 `expected_backend_id` 为准，禁止混用 pip CUDA 步骤与 DCU module 步骤
- 当前领域 profile 只描述依赖选择，不描述命令实现
- 默认用户已完成 SSH 免密登录配置
- 命令顺序要固定，避免 `conda` 与 `module` 环境不一致
- 用户未指定领域时，必须先确认领域
- 除非用户明确要求，不要先删除远程已有目录；优先复用或更新已有 `onescience` 工作树
