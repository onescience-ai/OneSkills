# 自适应监控接入示例

本片段说明已有训练入口的接入位置，不是训练启动器，不提供演示模型/数据。先通过资源获取 OneScience 工具卡与本卡的真实正文，再按目标版本适配；运行授权独立于代码生成。

```python
from training_monitor_adapter import OptionalTrainingMonitor

# Reuse the task's existing identity, absolute output_dir, rank and world_size.
# Model/optimizer/data already exist in the real trainer.
def create_onescience_monitor():
    from onescience.monitoring.training import MonitorConfig, capabilities, create_monitor
    report = capabilities()
    if (report.get("api_version") != "1" or report.get("contract_version") != "1.0"
            or not report.get("tensorboard")):
        raise RuntimeError("OneScience monitoring interface/dependencies unavailable")
    config = MonitorConfig(
        output_dir=str(output_dir), run_id=run_id, attempt_id=attempt_id,
        profile="base", record_every_updates=10, flush_secs=10,
    )
    return create_monitor(config, model=model, optimizer=optimizer, device=device,
                          rank=rank, world_size=world_size)

monitor = OptionalTrainingMonitor(
    create_onescience_monitor, output_dir=output_dir, run_id=run_id,
    attempt_id=attempt_id, rank=rank, world_size=world_size,
    record_every_updates=10, flush_secs=10,
)
try:
    # Keep the existing forward/backward/optimizer/checkpoint logic.
    # At its actual update boundary, call:
    # monitor.record_train(global_step=actual_step, loss=existing_loss_scalar,
    #                      update_applied=actual_update, lr_used=existing_lrs)
    run_existing_training(monitor)
finally:
    monitor.close()
```

`output_dir/run_id/attempt_id` 来自现有运行上下文，不能在 OneScience 工厂内部才定义，否则缺包时原生后端也拿不到目录。独立运行使用用户任务的显式配置；OneCode 沿用现有身份、目录绑定和采集交接，不增加上报机制、后台同步器或新任务类型。已有 writer 满足需求时复用，不能并行重复采集。

监控代码从现有 `skills/onescience-coder/scripts/training_monitor_adapter.py` 适配，不直接从资源路径执行未经授权的资产。OneScience-only 类型如 MetricSpec/Mean 不能放到无保护的模块顶层；公共训练路径只传原有基础数值，避免回退分支仍依赖缺失包。

## 正常运行与查看

训练沿既有入口写标准事件，结束时 flush/close；OneCode 按现有目录绑定采集展示。正常流程不交付或调用独立验收脚本，不要求额外事件点数。用户明确要求排查时，再按诊断契约只读检查指定运行。
