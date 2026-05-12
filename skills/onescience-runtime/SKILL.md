---
name: onescience-runtime
description: 在代码生成后提交远程作业。自行完成远端主机发现、硬件探测、后端选择、脚本渲染、作业提交与日志同步。不自其他技能获取硬件画像。
---

# OneScience 远程执行助手

## 核心职责

1. **通道选择**：根据用户意图选择 `ssh_slurm`（传统 SLURM）或 `scnet_mcp`（SCnet 云平台）
2. **远端主机发现**（仅 ssh_slurm）：从 `onescience.json` / `~/.ssh/config` / MCP host / 用户获取 SSH 目标
3. **远端硬件探测与后端选择**（仅 ssh_slurm）：登录远端确认加速器类型 → 选择 backend
4. **渲染作业脚本 + 提交运行**：基于模板填充字段，提交作业
5. **同步日志 + 监控状态**：等待完成，下载日志

---

**通道选择是唯一的分岔决策点。先选通道，再按分支执行，不要跨分支绕路。**

## 第 0 步：选择执行通道

| 条件 | 通道 |
|------|------|
| 用户明确提到 SCnet / 区域 / 队列 / SCnet API 关键字 | `scnet_mcp` |
| 未指定或描述为 SSH / SLURM 提交 | `ssh_slurm` |

**约束**：除非用户输入了 SCnet 相关关键词，否则**走 `ssh_slurm` 分支**，不得主动调用 SCnet MCP 工具。

---

## 分支 A：ssh_slurm（传统 SLURM 提交）

### 第 1A 步：远端主机发现

按以下优先级链查找 SSH 目标。**优先构造简洁的 `ssh {Host}` 形式**（`~/.ssh/config` 可预置 HostName、Port、User、IdentityFile、StrictHostKeyChecking 等参数），若无法匹配再构造完整连接串。

1. **`onescience.json` → `runtime.remote`** → 检查 `~/.ssh/config` 是否有匹配的 Host 别名（按 `host` 字段匹配）：
   - 有 → 用 `ssh {Host}` 连接
   - 无 → 提取 `hostname`、`port`、`user`，用 `ssh -p {port} {user}@{host}` 连接
2. **`~/.ssh/config`** → 列举有效 `Host` 条目，让用户选择 → 用 `ssh {Host}` 连接
3. **询问用户** → 用户提供 SSH 地址，按给出的形式连接

未找到 → `blocked`，报告缺少远程环境。

### 第 2A 步：读取 `onescience.json`

读取项目根目录的 `onescience.json`，提取集群配置（partition、modules、conda、datasets/models 路径等）。

缺少 `onescience.json` → `blocked`，报告需先配置。

### 第 3A 步：远端硬件探测与后端选择

用以下命令登录远端做单次综合探测：

```
ssh {SSH_TARGET} "
    echo '=== NVIDIA ===' && (nvidia-smi 2>/dev/null | head -5 || echo 'nvidia-smi: no device')
    echo '=== ROCM ===' && (rocm-smi --showproductname 2>/dev/null || echo 'rocm-smi: not found')
    echo '=== HIPCC ===' && (which hipcc 2>/dev/null && hipcc --version | head -2 || echo 'hipcc: not found')
    echo '=== DTK/ROCM/CUDA DIR ===' && ls -d /opt/dtk-* /opt/rocm* /usr/local/cuda* 2>/dev/null | head -5
    echo '=== DEV ===' && (ls -la /dev/kfd 2>/dev/null || echo 'no /dev/kfd')
    echo '=== MODULE ===' && (module avail 2>/dev/null | grep -iE 'dtk|sghpc|rocm|cuda' | head -10 || echo 'no relevant modules')
"
```

其中 `{SSH_TARGET}` 由第 1A 步决定：
- 匹配到 `~/.ssh/config` Host 别名 → `ssh {Host} "..."` 
- 来自 `onescience.json`（无 config 匹配）→ `ssh -p {port} {user}@{host} "..."`

| 探测结论 | backend_id |
|----------|-----------|
| NVIDIA GPU（nvidia-smi 有设备） | `slurm_gpu` |
| 海光 DCU / AMD ROCm（hipcc + DTK 目录） | `slurm_dcu` |
| 纯 CPU | `slurm_cpu` |

选中 `backend_id` 后，读取 `assets/backend_specs.json` 确认 `status`：
- `stable` → 继续
- `planned` → `blocked`（报告该后端暂不可用）

### 第 4A 步：渲染作业模板并提交

1. 从 `assets/backend_specs.json` 读取对应 backend 的 `module_setup`、`device_visibility_export`
2. 选择模板：优先使用项目根 `tpl.slurm`（用户自定义），否则用 `assets/templates/slurm_{backend}.sh`
3. 填充字段：

   | 字段 | 来源 | 示例值 |
   |------|------|--------|
   | `{cluster.*}` | `onescience.json → cluster` | partition, nodes, gpus, cpus, memory, time_limit |
   | `{backend.module_setup}` | `backend_specs.json` | module load dtk | module load cuda |
   | `{backend.device_visibility_export}` | `backend_specs.json` | `export HIP_VISIBLE_DEVICES=...` |
   | `{conda.env_name}` | `onescience.json → conda` | onescience |
   | `{env_vars.*}` | `onescience.json → env_vars` | 数据集、模型、分布式配置 |
   | `{script.job_name}` / `{script.code_path}` | 本次运行上下文 | train_pangu_afno.py |

4. 展示最终 `sbatch` 命令 → 请求用户确认 → 执行提交

---

## 分支 B：scnet_mcp（SCnet 云平台提交）

### 第 1B 步：通过 MCP 工具提交

直接调用 SCnet MCP 工具提交作业，详见 `references/scnet_channel.md`。

无需模板渲染，SCnet 平台自行处理硬件分配和调度。

### 第 2B 步：SCnet 失败处理

若 SCnet MCP 调用失败（权限不足、队列不可用等），向用户报告失败原因，**询问是否退回到 ssh_slurm 分支**。

---

## 日志同步（两个分支共用）

| 项 | 值 |
|----|-----|
| 远端日志目录 | `logs/` |
| 本地同步目录 | `.onescience/logs/` |
| 同步时机 | 作业完成后下载 |
| 包含后缀 | `.out`、`.err` |

---

## 执行前置条件

- `ssh_slurm` 分支缺少 `onescience.json` → `blocked`
- 对应 backend 的 `status` 为 `planned` → `blocked`
- 用户未确认提交 → 不执行

## 输出要求

1. 完整的 `runtime_config` JSON（含 backend、cluster、script 等字段）
2. 提交结果（job_id、状态）
3. 日志同步结果（本地路径、关键输出节选）
4. 若失败，给出失败原因和排查建议

## 关键参考文件

| 文件 | 用途 |
|------|------|
| `assets/backend_specs.json` | 后端支持矩阵、module_setup、device_visibility |
| `assets/templates/slurm_{cpu,dcu,gpu}.sh` | 作业脚本模板 |
| `assets/examples/*.json` | 请求/响应示例 |
| `references/runtime_contract.md` | 字段定义、渲染规则 |
| `references/scnet_channel.md` | SCnet 通道详细流程 |
