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
