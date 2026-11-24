# 阶段 5：训练执行

目标：由 trainer 组织训练执行，使用正确的运行通道执行训练，并捕获证据。依赖包、硬件和运行环境需求在本阶段随 runtime handoff 一起交给 `onescience-runtime`，不再单独成阶段。

## Runtime 交接

本阶段由 trainer 组织训练执行，并通过 `onescience-runtime` 选择和调用合适的运行通道。准备 `trainer_workdir` 下的 `runtime_request.json`，并把 runtime 返回结果记录到本技能的 manifest；最终仍由本技能返回外层 `execution_result`：

```json
{
  "task": "run training",
  "code_save_dir": "",
  "trainer_workdir": "",
  "workdir": "",
  "entrypoint": "",
  "command": "",
  "execution_mode": "local | local_slurm | remote_slurm | remote_direct | unknown",
  "hardware": "",
  "package_requirements": [],
  "environment_requirements": {
    "python": "",
    "frameworks": [],
    "accelerator": "",
    "memory": "",
    "modules": [],
    "conda": "",
    "container_or_image": ""
  },
  "knowledge_inputs": {
    "source_capture_path": "",
    "training_knowledge_path": "",
    "data_manifest_path": "",
    "training_plan_path": ""
  },
  "preflight_checks": [],
  "expected_outputs": [],
  "init_checkpoint": "",
  "resume_checkpoint": "",
  "train_command": "",
  "expected_checkpoints": [],
  "expected_metrics": [],
  "log_dir": "",
  "manifest_path": ""
}
```

`package_requirements` 和 `environment_requirements` 来自 `step_handoff.inputs.runtime`、`trainer_workdir` 中保存的 `training_knowledge.md` / `training_plan.md`、项目 `requirements.txt` / `pyproject.toml` / 环境文件、官方 README、导入错误或训练计划。只记录有来源的信息；无法确认版本时写入范围、约束或 `MISSING:`，不要猜测精确版本。

如果用户要求本地执行，且当前环境合适，也应把 package 和环境需求记录到 `runtime_request.json`。如果用户要求 SLURM、SCnet、SSH 或远程执行，则路由到 `onescience-runtime`，并保留远程执行意图。

## 执行前检查

确认：

- `trainer_workdir` 中所需知识文件已存在，并已据此构造 `runtime_request.json.knowledge_inputs`
- 入口文件存在
- Config、checkpoint 和输入文件存在或可解析
- 输出目录可写
- 数据 manifest 满足训练输入契约
- 需要安装或确认的 package 已写入 `runtime_request.json.package_requirements`
- Python、框架、加速后端、内存、模块、conda、容器或镜像需求已写入 `runtime_request.json.environment_requirements`
- 对大型下载、package 安装、环境修改或远程提交等需要授权的操作，已获得用户授权；未授权时返回 `blocked` 或把执行标记为 `pending`

执行前检查、命令构造和失败诊断应以 `trainer_workdir` 中保存的知识产物为准，不要在这些文件已存在时重新凭会话上下文猜测训练入口、checkpoint 语义、数据格式、恢复策略或预期输出。

## 证据捕获

将以下内容捕获到 `runtime_result.json`：

- 命令或提交脚本
- 执行通道和目标
- runtime 处理 package / 环境需求的结果
- Job ID 或进程退出码
- 日志路径和已同步日志路径
- 输出文件、checkpoint 和关键指标
- 可用时的运行时长
- 失败时的失败分类

执行后更新 `trainer_run_manifest.json`。如果执行失败且没有产生可检查输出，不要继续进入验证；将失败证据写入 `execution_result.observation.risks` 和 `missing`，供 orchestrator 更新 Task State。

`runtime_result.json` 中引用的日志、输出文件、checkpoint 和 metrics，必须来自同一条真实执行命令或提交记录。若执行在产出结果前失败或被阻断，`runtime_result.json` 只能记录阻断 / 失败原因、命令或提交状态、已有日志（若有）以及缺失的 expected outputs；不得为了满足 `expected_outputs` 回填模拟 metrics、predictions、targets 或合成日志片段。

## 可选训练监控补充

仅当用户明确要求监控，或项目中已登记的训练任务要求监控时，执行本节。普通训练继续按上文的 Runtime 交接、执行前检查和证据捕获流程执行，不要求额外登记平台任务。

通过 `resource_retrieval_request/result` 获取训练监控任务、OneScience 工具和监控验收契约的真实正文，按兼容的公共接口接入；常规生成不要求读取 OneScience 源仓库。运行时仍由 installer 核对实际训练环境中的组件兼容性。仅监控依赖或配置不可用时单列 warning；模型、数据、设备等业务必需项仍按原预检规则处理。

### OneCode 平台内的监控训练

本小节仅适用于提供相应平台能力的 OneCode 宿主；其他宿主按通用监控契约执行，不要求调用 `training_monitor`。

1. 通过 `training_monitor action=tasks` 读取项目任务；通过 `save_task` 维护稳定任务、实际训练入口、业务配置、包装脚本及 `monitoring.requested=true`（兼容旧 `required=true`，均表示监控请求）。保留任务 id 和其他配置。代码生成和执行分开时从该配置继承要求；只交付代码时不登记运行、不提交作业。
2. 额外获取 `onecode-training-monitoring` 的真实正文。runtime 仍按原有交接和权限调用既有执行工具，在执行调用中引用 `task_ref`；平台准备本次运行身份并关联实际作业。运行身份不写入长期任务配置。
3. 执行前核对已有接入代码会使用平台 `ONECODE_RUN_ID/ONECODE_ATTEMPT_ID` 构造真实 MonitorConfig 和独立事件目录，在初始化后、结束关闭后向 `ONECODE_RUNTIME_MANIFEST` 上报实际目录及真实训练退出结果。具体字段与示例以平台契约为准，不把项目上报辅助函数当作 OneScience 公共方法。

### 监控收尾与证据

多 rank 汇总、事件验证和关闭按召回契约执行，独立 verify 作业与训练作业分别记录。监控初始化、记录、上报、关闭或 verify 失败只记录监控缺口，不改变真实训练退出码、不因监控问题重训；真实训练失败仍按原有编排处理，OneCode 的失败重试按平台契约沿用 run、新建 attempt。

在上文原有 `runtime_result.json`、`trainer_run_manifest.json` 和 `execution_result` 中补充当前 run/attempt、实际事件目录、原始 verify 报告及缺失项，分别说明代码接入、训练结果、指标采集和页面展示状态。未在页面取证时标记展示 `not_run`，不将组件验证或已有缓存可读宣称为本次页面验收成功。
