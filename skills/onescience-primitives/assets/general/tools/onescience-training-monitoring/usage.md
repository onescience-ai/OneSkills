# 使用知识与独立接入示例

本卡正文即编码依据，不需要访问 OneScience 源仓库。以下为知识示例，不是 execution_assets，也不授权启动训练。业务模型、数据、优化器和原训练策略仍由项目提供；仅代码任务不执行示例。

## 配置与运行目录

所有 rank 在提交后读取同一份实际配置。独立运行使用明确的 run/attempt；OneCode 运行先按平台契约将注入身份落实到配置，禁止直接沿用下面的占位值。

```json
{"output_dir":"<当前attempt绝对根目录>","run_id":"<当前run>","attempt_id":"<当前attempt>","profile":"base","backend":"threaded_files","record_every_updates":1,"flush_secs":1,"train_mode":"writer_local","validation_mode":"writer_local","shutdown_timeout_seconds":120}
```

采样 1 与关闭 120 秒是短程验证示例，可依需求和开销调整；关闭仍须有界。CPU 可验证基本指标。base 不启用梯度/耗时/显存诊断，不因这些组件 false 判接入失败；要求 full 时才启用并核对 hook 和设备支持。

## OneScience 初始化工厂

统一生命周期与后端选择消费 tasks/pytorch-training-monitoring-integration 和 tools/native-tensorboard-monitoring；技能辅助 OptionalTrainingMonitor 负责初始化不可用时的原生兜底。此卡只定义 OneScience 工厂，不再维护另一套吞异常后返回 None 的接入实现。

```python
def create_onescience_monitor():
    from onescience.monitoring.training import MetricSpec, MonitorConfig, capabilities, create_monitor
    report = capabilities()
    if (report.get("api_version") != "1" or report.get("contract_version") != "1.0"
            or not report.get("tensorboard")):
        raise RuntimeError("OneScience monitoring interface/dependencies unavailable")
    config = MonitorConfig(output_dir=str(output_dir), run_id=run_id, attempt_id=attempt_id,
                           profile="base", record_every_updates=10, flush_secs=10)
    return create_monitor(config,
        metrics=(MetricSpec(), MetricSpec(phase="validation", required=False)),
        model=model, optimizer=optimizer, device=device, rank=rank, world_size=world_size)
```

output_dir/身份、模型、数据和优化器由真实训练入口提供，不能只在这个 factory 内定义。预检按目标版本核对接口；显式关闭由统一适配层优先处理。训练中沿原调用位置 record/start_phase/end_phase，并在 finally 关闭；监控失败不改变训练结果。
## DDP、AMP、累积和恢复的适配

- 普通 DDP：复用业务已初始化的 rank/world_size，不为监控新增进程组、all_reduce 或 barrier。每 rank 创建 monitor，各 rank 配置共享身份和 attempt 根目录；本地样本均值需全局曲线时将相应 phase 设 ddp_global。源文件由各 rank 写入 sources/rank_N，一个外部 aggregate 负责加权。writer_local 只取 writer rank，不能标作全局。
- 已有全局值：如 Xihe 原验证逻辑已有全局均值，使用 MetricSpec(phase="validation", scope="global") 与 validation_mode="writer_local"，保留原归约，不再次 ddp_global。其他指标如无全局证据仍按 rank。
- 自定义指标：在 create_monitor 中声明 MetricSpec(name=..., phase=..., scope=..., weight_unit=...)；record 的 metrics={name:Mean(existing_scalar, actual_weight)}。不复制 Pangu 的模型专属分项名称。
- AMP：沿用已有 scaler/step/unscale 与溢出判据，将 gradient_point 及调用 point 同时改为 after_unscale_before_clip；只在原来已有 unscale 后、裁剪前采样。不得为监控重复 unscale/step。scaler.step 返回 None 不足以证明发生更新。
- 梯度累积：逐微批 record，micro_step 递增；未更新时 global_step 不变、update_applied=False、不采梯度。真实更新才 step+1；若希望 loss 表示整个累积窗口，复用业务已有窗口统计，组件不会替你累积未更新微批。
- 模型恢复不等于监控恢复。有匹配 monitor_state、原 run、schema、parent attempt 和 step 时，配置 parent_attempt_id/resume_from_step 并在 start_phase 前 load_state_dict，检查 accepted；所有 rank 用各自状态。无监控状态时使用新 attempt 和独立监控计数，记录业务 step 与监控 step 的关系，不伪造恢复。
- live reload：from_file/from_env 绑定配置来源，在批边界 poll_config；只改 capabilities 声明的 mutable 字段。身份/目录/backend 不能运行中改变，暂停诊断需显式 reenable。

## 环境与事件产出

环境预检由 installer 在实际训练解释器中处理；公共 capabilities 只说明能力。单 rank 正常写事件并关闭，普通 DDP 需要的单个外部 aggregate 按实际配置运行，在最终源同步后有界结束；不要与另一个汇总器并发。

正常训练不额外调用 check/verify，也不提交验收作业。训练退出码只反映真实业务结果。OneCode 沿原身份和事件目录采集展示。

## 按需诊断

仅用户明确要求检查配置、验证指标或排查无曲线时，才读取 training-monitoring-verification。可使用公共 check/verify 或事件读取器；保留实际命令及报告，waiting 不触发训练重跑。诊断不新增训练、模拟事件或采集服务。
