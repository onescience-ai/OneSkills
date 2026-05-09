# Install Flow

本文件用于提供 `onescience-installer` 的安装流程、输入语义和执行约束。

## 当前支持边界

以对 `skills/onescience-runtime/assets/backend_specs.json` 的 **`support_matrix.installer`** 为准裁决是否允许执行仓库级安装链路：

- 当 **`slurm_dcu`** 的 `installer.status` 为 **`supported`** 时，可使用本文 `dcu_remote_install` 两阶段命令。
- 当 **`slurm_gpu`** 的 `installer.status` 为 **`unsupported_for_now`** 时，不得以「已写好命令模板」为由在 GPU 后端上谎称可完整执行安装矩阵；应向用户明示矩阵尚不支持。下文仍收录 `gpu_remote_install` 命令骨架，供矩阵切至 `supported` 且 `installer.backend` 为 `gpu_remote_install` 后直接采用。

当前安装仍以远程环境执行为前提，不在本地安装 OneScience。

## 本 skill：远端判别先于选用骨架 —— **不得**单靠 `onescience.json` 定 DCU/GPU

以下规则**只对**扮演 `onescience-installer` 的智能体生效；**不改变**项目中其他技能对工作区 `onescience.json` 的既有读取、生成或业务流程。

常见问题：在用户真正建立 SSH 远端事实之前，仅从项目根的 `onescience.json`（例如默认字段 `runtime.cluster.gpu_type`、`runtime.modules`）或 Host 别名中的 `gpu`/`dcu` 字样，就预先宣布「目标是 `slurm_dcu`、`dcu_remote_install`」（这与实际登录节点可以不一致）。

本 skill 内正确顺序：

1. 读取上游交接的**完整硬件画像**（若有），关注顶层 **`expected_backend_id`** 以及 **`hardware_profile.accelerators[].kind`**。**禁止**仅用 `onescience.json` 的同类字段顶替上述远端事实来选择安装骨架。
2. 若画质已能唯一指向 `slurm_dcu` 或 `slurm_gpu`，则用该结论与 `accelerators`、`driver_stack.accelerator_runtime_family`（`rocm`/`cuda`）互证；不得与 JSON 配置文件「谁写着 DCU 就以谁为准」。
3. 若仍不足以判别，则在**已获得目标 Host 的非交互 SSH 可达性**前提下，由**本 skill**在执行阶段 1 安装命令之前，追加**一次**远端只读探测（不向其他 skill 转嫁流程语义），任选足够判别的命令：`nvidia-smi`（NVIDIA CUDA）、`rocm-smi` 或 `hipcc --version`（AMD ROCm/DCU 站点），必要时辅以 `module avail` 截取，但**不得以模块名字符串代替设备枚举结果**。
4. 选定 `hardware backend id` 后，核对 `support_matrix.installer`。若结果为 `blocked` / `unsupported_for_now`，则诚实阻断；**不得以 `onescience.json`「覆盖」**支持矩阵的结论。

远端判别结果若与用户对 Host 的主观预期不符，应向用户指出须以远端事实为准，是否更新项目级配置文件由用户或其工作流惯例决定；**installer 不改变**其他技能的 JSON 处理方式。

## 关键输入层

安装链路当前消费 5 层输入：

1. `hardware backend`
   - 来自 `skills/onescience-runtime/assets/backend_specs.json` 的 `support_matrix.installer`
2. `installer backend profile`
   - 来自 `../assets/backend_profiles.json`
   - 描述硬件相关的 user-space 环境准备
3. `workspace bootstrap profile`
   - 来自 `../assets/workspace_bootstrap_profiles.json`
   - 描述仓库来源、工作树复用和安装入口渲染
4. `install domain profile`
   - 来自 `../assets/install_domains.json`
   - 描述领域依赖意图与 `dependency_selector`
5. `host readiness / precheck`
   - 来自 `hardware_profile.software.driver_stack` 及其 `capability_readiness`

标准输入资产位置：

- installer backend profile：`../assets/backend_profiles.json`
- workspace bootstrap profile：`../assets/workspace_bootstrap_profiles.json`
- install domain profile：`../assets/install_domains.json`
- request 示例：`../assets/request_examples/*.json`
- resolution 示例：`../assets/resolution_examples/*.json`

## 输入约束

当前标准 install request 只包含：

- `domain`

不要把以下内容当成用户请求层输入：

- `python_version`
- `env_name`
- `repo_name`
- `repo_url`
- `repo_ref`
- `allow_reuse_existing_worktree`

这些属于 backend profile 或 workspace bootstrap profile 的实现细节。

## 驱动层边界

`onescience-installer` 当前只负责 user-space 安装，不负责：

- 安装或升级内核态驱动
- 加载内核模块
- 修改系统级 CUDA / ROCm 部署
- 申请 root 权限或重启节点

进入安装前至少要确认：

- `driver_stack.owner = platform_admin`
- `driver_stack.driver_ready = true`
- `driver_stack.user_space_ready = true`
- `driver_stack.capability_readiness.compiler_ready = true`
- `driver_stack.capability_readiness.torch_ready = true`
- `driver_stack.capability_readiness.distributed_runtime_ready = true`

若上述条件不满足，应直接阻断并提示平台侧先处理驱动栈。

## 安装流程概览

所有安装操作必须在远程环境执行，不得在本地执行。

关键要求：

- 阶段 1 使用一个远程命令完成环境准备、工作区同步与领域安装
- 阶段 2 使用独立远程命令做安装验证

前置阶段：

1. 取得完整硬件画像（若有）；若不足以区分 DCU/GPU，则在本 skill 内按上文「远端判别先于选用骨架」用 SSH 只读探测补足（判别依据来自远端，不靠项目根 `onescience.json`）
2. 根据 `support_matrix.installer` 判断当前 hardware backend 是否受支持
3. 读取对应 installer backend profile
4. 读取默认 workspace bootstrap profile
5. 检查 `software.driver_stack` 与 `capability_readiness`
6. 确认安装领域
7. 仅选择与本 hardware backend 匹配的**一个**安装命令骨架（DCU 与 GPU 互不混用）
8. 准备远程安装与验证命令

## `dcu_remote_install` 阶段 1：安装命令骨架

如果 `conda create` 失败，再重试一次，并在 `module load sghpc-mpi-gcc/26.3` 之后、`conda create` 之前插入：

```bash
source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate
```

标准流程骨架：

```bash
module load sghpcdas/25.6
source ~/.bashrc
module load sghpc-mpi-gcc/26.3
# 必要时 fallback:
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
bash install.sh earth
```

说明：

- 上面最后一行只是 `earth` 的渲染结果示例
- `all` 场景应使用 workspace bootstrap profile 的默认 selector 省略规则渲染

## `dcu_remote_install` 阶段 2：验证命令

安装完成后，执行以下完整命令验证安装是否成功：

```bash
module load sghpcdas/25.6 && source ~/.bashrc && module load sghpc-mpi-gcc/26.3 && conda activate onescience311 && python -c 'import torch; print(torch.__version__)' && python -c 'import onescience; print(onescience.__version__)'
```

约束：

- 禁止创建验证脚本
- 必须直接执行验证命令

## `gpu_remote_install` 阶段 1：安装命令骨架

标准流程骨架：

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
# dependency_selector 由 install_domains.json 提供
bash install.sh earth
```

说明：

- `gpu_remote_install` 当前对单机 `slurm_gpu` 与多机 `slurm_gpu_multinode_torchrun` 都已开放
- 对多机 GPU 场景，`distributed_runtime_ready` 应被视为安装前置条件，而不是运行阶段才处理的隐含条件
- `~/onescience/cudnn` 表示当前用户家目录下 `onescience` 目录内的 `cudnn` 布局；与仓库克隆路径一致
- 最后一行 `earth` 仅为占位示例，实际参数以用户请求的 `domain` 为准

## `gpu_remote_install` 阶段 2：验证命令

安装完成后，`onescience311` 内依赖与动态库已就绪，验证时**只需进入该 conda 环境**并执行导入检查即可

安装完成后，执行以下完整命令验证安装是否成功：

```bash
source ~/.bashrc && conda activate onescience311 && python -c 'import torch; print(torch.__version__)' && python -c 'import onescience; print(onescience.__version__)'
```

若验证时出现动态库找不到等加载错误，再在**同一条验证命令**里、于 `conda activate` 之后按阶段 1 补上相同的 `export` / `source` 后重试。

## 安装注意事项

- DCU 与 GPU 使用不同安装骨架；以硬件画像与 `expected_backend_id` 为准，禁止混用 pip CUDA 步骤与 DCU module 步骤
- 当前领域 profile 只描述依赖选择，不描述命令实现
- 默认用户已完成 SSH 免密登录配置
- 命令顺序要固定，避免 `conda` 与 `module` 环境不一致
- 用户未指定领域时，必须先确认领域
