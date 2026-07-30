# Preflight

在 discover 已经派生出 `execution_channel` 后，读取本文件。

preflight 是进入 execute 的唯一门禁。runtime 不再自行执行环境检测，而是**完整委托** `onescience-installer` 执行环境就绪预检。只有 installer 返回 `preflight_result.status=passed`（或可继续执行的 `partial`）后，runtime 才能进入 execute 分支。

## 1. 组装 Preflight 上下文

1. 重新读取根目录 `onescience.json`。
2. 保留 discover 产出的：
   - `execution_channel`
   - `semantic_environment_hints`
   - `submission_target_candidates`
3. 收集需要传递给 installer 的上下文：
   - `execution_channel`
   - `runtime.conda`（完整结构）
   - `runtime.target`（硬件类型）
   - `runtime.script.work_dir` / `runtime.script.code_path`
   - 入口脚本路径
   - 业务依赖列表（如有）

## 2. 委托 Installer 执行环境就绪预检

以 `installer_reason=preflight_validation` 立即加载并执行 `skills/onescience-installer/SKILL.md`：

- 传入 `execution_context`（`run_site`、`execution_mode`、`access_mode`、`execution_channel`）
- 传入 `transport_context`（`runtime.ssh.work_dir` / `runtime.scnet.work_dir` 等）
- 传入入口脚本路径和业务依赖列表
- 无需向用户二次确认

installer 读取 `./references/preflight-validation.md` 执行完整的环境就绪检查：
- Conda 配置校验
- Python 解释器检查
- onescience / torch 及业务依赖导入检查
- CUDA 扩展可用性检查
- 入口脚本语法检查
- 环境依赖一致性检查
- GPU 可访问性与显存预算估算
- 数据文件存在性检查
- 通道级必检项
- SLURM 通道登录节点 vs 计算节点环境区分

## 3. 处理 Installer 返回结果

installer 返回 `preflight_result`：

| status | 含义 | runtime 处理 |
|--------|------|-------------|
| `passed` | 环境就绪 | 设置 `preflight_passed=true`、`execution_readiness=ready`，进入 execute |
| `partial` | 部分通过（有 warning 但可继续） | 记录 warnings，设置 `preflight_passed=true`、`execution_readiness=ready`，进入 execute |
| `failed` | 环境有问题，installer 已进入修复流程 | 等待 installer 修复；修复成功后重新读取 `onescience.json`，从 preflight 重新开始 |
| `blocked` | 环境有不可修复的阻断 | 记录阻断原因，停止并向 orchestrator 报告 |

## 4. SCnet 提交配置检查

当 `execution_channel=scnet_mcp` 且用户意图包含提交新任务时，runtime 在进入 execute 前必须确保 SCnet 提交参数齐备：

- 读取 `onescience.json.runtime.scnet`
- 必填字段：`region`、`partition`（提交给 scnet-chat 时映射为 `queue`）、`remote_work_dir`/`work_dir`
- 若缺失必填字段，设置 `next_action=onescience-runsite` 和 `blocking_reason=missing_scnet_submit_config`，由 runsite 补齐后回到 discover
- 用户自然语言中的 region/partition 只作为缺失字段线索，未写入 `onescience.json.runtime.scnet` 前不得据此提交任务

## 5. Output

preflight 至少产出：

- `execution_channel`
- `submission_target`
- `preflight_passed`
- `execution_readiness`
- `blocking_reason`
- `evidence.preflight`（来自 installer 的 preflight_result）
- `preflight_result`（installer 的完整返回）

一句话原则：

preflight 不再自行做环境检测。它只负责组装上下文、完整委托 `onescience-installer` 执行环境就绪预检、消费 `preflight_result` 并决定是否进入 execute。环境就绪检测的全部职责已迁移到 `onescience-installer` 的 `preflight-validation.md`。
