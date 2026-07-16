# 运行站点配置契约

本文件定义 `onescience-runsite` 的职责边界、`onescience.json` 新版字段契约，以及交回调用方或 `onescience-orchestrator` 的交接格式。

## 1. 职责定位

`onescience-runsite` 是配置发现、有限连接验证与交接层。它可被 `onescience-runtime`、`onescience-installer`、其它执行技能或 `onescience-orchestrator` 临时调用，只产出稳定配置、连接可达性结论和静态提示，不负责安装、提交、运行、轮询或远端环境诊断。

## 2. 新版 `execution_profile`

根目录 `onescience.json` 使用：

```json
{
  "runtime": {
    "execution_profile": {
      "run_site": "local|remote",
      "execution_mode": "slurm|null",
      "access_mode": "ssh|scnet|"
    }
  }
}
```

字段规则：

- `run_site`: 运行站点，只能为 `local` 或 `remote`。
- `execution_mode`: 调度方式，只能为 `slurm` 或 JSON `null`。
- `access_mode`: 远程接入方式，只能为 `ssh` 或 `scnet`；`run_site=local` 时必须为 `""`。

合法组合：

| run_site | execution_mode | access_mode | 含义 | runtime 派生通道  |
|---|---|---|---|---------------|
| `local` | `null` | `""` | 本地直接运行 | `local_direct` |
| `local` | `slurm` | `""` | 当前机器/登录节点本地 Slurm | `local_slurm` |
| `remote` | `null` | `ssh` | 远程 SSH 直接上下文 | `ssh_direct`  |
| `remote` | `slurm` | `ssh` | SSH 进入远程 Slurm 登录节点 | `ssh_slurm`   |
| `remote` | `null` | `scnet` | SCnet 远程直接上下文 | `scnet_mcp`   |
| `remote` | `slurm` | `scnet` | SCnet 远程 Slurm 上下文 | `scnet_mcp`     |

`runtime 派生通道` 仅用于交接说明和下游理解；runsite 不生成、不写入、也不依赖 `execution_channel`。

不再生成旧字段和值：

- `execution_channel`
- `execution_mode=remote_slurm|remote_direct|local_slurm`
- `access_mode=local|cloud_api|slurm`

## 3. 配置结构

`runtime.execution_profile` 放置模式选择。

`runtime.ssh` 在 `run_site=remote` 时必须补齐；即使 `access_mode=scnet`，也要保存并验证 SSH 信息：

```json
{
  "host": "alias-or-host",
  "hostname": "host-or-ip",
  "port": 22,
  "user": "alice",
  "strict_host_key_checking": "no",
  "password_authentication": "no",
  "identity_file": "~/.ssh/id_rsa",
  "remote_work_dir": "/home/alice/work"
}
```

`runtime.scnet` 只在 `run_site=remote` 且 `access_mode=scnet` 时必须额外补齐：

```json
{
  "SCNET_ACCESS_KEY": "...",
  "SCNET_SECRET_KEY": "...",
  "SCNET_USER": "alice",
  "region": "核心节点",
  "remote_work_dir": "~/work"
}
```

`runtime.cluster` 只在 `execution_mode=slurm` 时必须补齐；非 Slurm 时为 `null`。

## 4. 输入优先级

1. 若根目录存在完整 `onescience.json`，先展示非敏感摘要并询问是否复用。
2. 若为 `run_site=remote`，复用前必须验证 SSH；当 `access_mode=scnet` 时还必须验证 SCnet。
3. 若用户明确要求修改，只修改指定字段。
4. 若文件不存在，先问本地还是远程，再进入对应工作流。
5. 若上下文与配置冲突，以 `onescience.json` 为准；需要改变时必须得到用户明确指令。

## 5. 下游边界

runsite 负责：

- 补齐 `run_site`、`execution_mode`、`access_mode`。
- 保存 SSH alias 到 `~/.ssh/config`。
- 保存 SCnet 凭据到 `~/.scnet-chat.env`，但不在输出中回显密钥。
- remote 模式下做有限连接验证：
  - SSH：所有远程配置都必须验证能否登录；遇到 Windows 私钥权限过宽时，用 `icacls <IdentityFile> /grant:r <当前 Windows 用户>:F` 修复后重试；最多尝试 3 次。
  - SCnet：`access_mode=scnet` 时尝试获取 token 验证凭据；无法登录时停止。
- 生成或修改根目录 `onescience.json` 时，只写入和更新以下字段：
  - `runtime.execution_profile`
  - `runtime.ssh`（remote 时）
  - `runtime.scnet`（scnet 时）
  - `runtime.cluster`（slurm 时）
  - `runtime.target`
  - `runtime.environment`
  - `runtime.modules`
  - `runtime.resources`
  - `runtime.env_vars`
- 禁止写入或更新 `runtime.conda`：该字段由 `onescience-installer` 技能独占管理。
- 输出交接信息。
- 回传控制信息只属于技能交接输出，不写入 `onescience.json`。

runtime 负责：

- 在连接已验证的前提下执行真实任务流程。
- 做远端 Slurm/module/conda/path 探测。
- 生成脚本、提交作业、轮询状态、同步日志、基础诊断。

installer 负责：

- 安装或修复环境。
- 执行 discover/precheck/install/verify。
- 验证 OneScience 是否可用。

## 6. 交接格式

```json
{
  "config_file": "./onescience.json",
  "config_exists": true,
  "execution_profile": {
    "run_site": "remote",
    "execution_mode": "slurm",
    "access_mode": "ssh"
  },
  "hardware_detected": {
    "accelerator_kind": "dcu",
    "accelerator_vendor": "amd",
    "cpu_arch": "x86_64"
  },
  "credential_source": "~/.ssh/config",
  "account_summary": {
    "ssh_host_alias": "onescience-cluster",
    "scnet_user": null
  },
  "cluster_config": {
    "scheduler_type": "slurm",
    "partition": "hpctest01",
    "resources": {}
  },
  "remote_validation": {
    "checked": true,
    "connected": true,
    "method": "ssh|scnet",
    "attempts": 1
  },
  "next_action": "onescience-runtime"
}
```

不要在交接信息中输出 SSH 私钥内容、`SCNET_ACCESS_KEY` 或 `SCNET_SECRET_KEY` 明文。

若 remote 验证失败，`next_action` 必须是 `ask_user`，并明确告知“提供的信息无法连接上远程，请按当前接入方式的字段清单重新提交远程连接信息”。SSH 验证失败时列出 SSH 所需字段；SCnet 验证失败时列出 SCnet 所需字段；不要只让用户“提供远程信息”。
