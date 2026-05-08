# Install Flow

本文件用于提供 `onescience-installer` 的安装流程、输入语义和执行约束。

## 当前支持边界

当前稳定支持的安装后端仅为：

- `dcu_remote_install`

当前安装仍以远程环境执行为前提，不在本地安装 OneScience。

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

1. 读取完整硬件画像
2. 根据 `support_matrix.installer` 判断当前 hardware backend 是否受支持
3. 读取对应 installer backend profile
4. 读取默认 workspace bootstrap profile
5. 检查 `software.driver_stack` 与 `capability_readiness`
6. 确认安装领域
7. 准备远程安装与验证命令

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

## 安装注意事项

- 当前稳定安装 profile 仍是 DCU 定向 profile
- 当前领域 profile 只描述依赖选择，不描述命令实现
- 默认用户已完成 SSH 免密登录配置
- 命令顺序要固定，避免 `conda` 与 `module` 环境不一致
- 用户未指定领域时，必须先确认领域
