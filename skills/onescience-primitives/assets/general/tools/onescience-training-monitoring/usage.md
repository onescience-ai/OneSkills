# 使用知识与独立接入示例

本卡正文即编码依据，不需要访问 OneScience 源仓库。以下为知识示例，不是 execution_assets，也不授权启动训练。业务模型、数据、优化器和原训练策略仍由项目提供；仅代码任务不执行示例。

## 配置与运行目录

所有 rank 在提交后读取同一份实际配置。独立运行使用明确的 run/attempt；OneCode 运行先按平台契约将注入身份落实到配置，禁止直接沿用下面的占位值。

```json
{"output_dir":"<当前attempt绝对根目录>","run_id":"<当前run>","attempt_id":"<当前attempt>","profile":"base","backend":"threaded_files","record_every_updates":1,"flush_secs":1,"train_mode":"writer_local","validation_mode":"writer_local","shutdown_timeout_seconds":120}
```

采样 1 与关闭 120 秒是短程验证示例，可依需求和开销调整；关闭仍须有界。CPU 可验证基本指标。base 不启用梯度/耗时/显存诊断，不因这些组件 false 判接入失败；要求 full 时才启用并核对 hook 和设备支持。

## 完整生命周期与可选监控边界

以下代码可随业务训练脚本适配。调用方在创建模型/数据后 open，在 try/finally 中执行原训练并 close；训练退出码与监控验收退出码分开保存。初始化、调用、关闭失败只影响监控。不要给业务训练体加吞异常的 try/except。

```python
import json
import logging
from contextlib import contextmanager

log = logging.getLogger("training.monitoring")

def monitoring_call(monitor, method, *args, **kwargs):
    if monitor is None:
        return None
    try:
        result = getattr(monitor, method)(*args, **kwargs)
        if isinstance(result, dict) and result.get("accepted") is False:
            reason = result.get("reason")
            if reason not in ("cadence/disabled", "unchanged/closed", "cadence"):
                log.warning("monitoring %s rejected: %s", method, reason)
        return result
    except Exception as error:
        log.warning("monitoring %s failed (%s); training continues", method, type(error).__name__)
        return None

@contextmanager
def monitored_stage(monitor, name):
    stage = None
    try:
        if monitor is not None:
            stage = monitor.stage(name)
            stage.__enter__()
    except Exception as error:
        log.warning("monitoring stage unavailable (%s)", type(error).__name__)
        stage = None
    # Training exceptions must propagate; only monitor entry/exit are guarded.
    try:
        yield
    finally:
        if stage is not None:
            try:
                stage.__exit__(None, None, None)
            except Exception as error:
                log.warning("monitoring stage close failed (%s)", type(error).__name__)

def open_training_monitor(config_path, *, model, optimizer, device, rank, world_size):
    import os
    if os.environ.get("ONECODE_MONITORING_DISABLED") == "1":
        return None
    monitor = None
    try:
        # All OneScience-only imports/configuration stay inside this boundary.
        from onescience.monitoring.training import MetricSpec, MonitorConfig, create_monitor
        config = MonitorConfig.from_file(config_path)
        monitor = create_monitor(
            config, metrics=(MetricSpec(), MetricSpec(phase="validation", required=False)),
            model=model, optimizer=optimizer, device=device, rank=rank, world_size=world_size,
            stages=("forward", "backward", "optimizer_step"),
            gradient_point="after_backward_before_clip",
            measurement_scope="rank batch processing excluding DataLoader wait",
        )
        if getattr(monitor, "config", None) is None or getattr(monitor, "initialization_error", None):
            monitoring_call(monitor, "close")
            log.warning("monitoring initialization unavailable; training continues")
            return None
        return monitor
    except Exception as error:
        monitoring_call(monitor, "close")
        log.warning("monitoring initialization failed (%s); training continues", type(error).__name__)
        return None

def close_training_monitor(monitor):
    result = monitoring_call(monitor, "close")
    status = monitoring_call(monitor, "status")
    complete = (isinstance(result, dict) and result.get("closed") is True
                and result.get("error") is None and result.get("pending_records", 0) == 0
                and isinstance(status, dict) and status.get("dropped") == 0
                and status.get("writer_error") is None)
    log.info("monitoring close: %s", json.dumps({"complete": complete, "close": result, "status": status}))
    return {"complete": complete, "close": result, "status": status}

def train_one_epoch(model, optimizer, train_loader, validation_loader, loss_fn, device,
                    monitor, *, global_step=0, micro_step=0, epoch=0):
    # Complete FP32/no-accumulation insertion example. Keep real model/data outside.
    import time
    import torch
    model.train()
    monitoring_call(monitor, "start_phase", "train", epoch=epoch)
    for inputs, targets in train_loader:
        monitoring_call(monitor, "poll_config")
        started = time.perf_counter()
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        with monitored_stage(monitor, "forward"):
            loss = loss_fn(model(inputs), targets)
        with monitored_stage(monitor, "backward"):
            loss.backward()
        if monitoring_call(monitor, "is_enabled", "gradient"):
            monitoring_call(monitor, "capture_gradients", point="after_backward_before_clip")
        lr_used = [float(group["lr"]) for group in optimizer.param_groups]
        with monitored_stage(monitor, "optimizer_step"):
            optimizer.step()
        global_step += 1
        micro_step += 1
        # In a real trainer reuse its existing scalar/weight; do not add conversions.
        loss_value = float(loss.detach().item())
        monitoring_call(monitor, "record_train", global_step=global_step, micro_step=micro_step,
                        loss=loss_value, loss_weight=len(inputs), update_applied=True,
                        lr_used=lr_used, sample_count=len(inputs), elapsed_seconds=time.perf_counter()-started)
    monitoring_call(monitor, "end_phase")
    model.eval()
    monitoring_call(monitor, "start_phase", "validation", epoch=epoch)
    with torch.no_grad():
        for batch, (inputs, targets) in enumerate(validation_loader, 1):
            inputs, targets = inputs.to(device), targets.to(device)
            loss_value = float(loss_fn(model(inputs), targets).item())
            monitoring_call(monitor, "record_validation", global_step=global_step,
                            validation_batch=batch, loss=loss_value, loss_weight=len(inputs))
    monitoring_call(monitor, "end_phase")
    return global_step, micro_step
```

调用方式：`monitor = open_training_monitor(config_path, model=model, optimizer=optimizer, device=device, rank=rank, world_size=world_size)`，然后 `try: ...原训练... finally: close_training_monitor(monitor)`。OneCode 在初始化后按平台资源报告实际目录。

## DDP、AMP、累积和恢复的适配

- 普通 DDP：复用业务已初始化的 rank/world_size，不为监控新增进程组、all_reduce 或 barrier。每 rank 创建 monitor，各 rank 配置共享身份和 attempt 根目录；本地样本均值需全局曲线时将相应 phase 设 ddp_global。源文件由各 rank 写入 sources/rank_N，一个外部 aggregate 负责加权。writer_local 只取 writer rank，不能标作全局。
- 已有全局值：如 Xihe 原验证逻辑已有全局均值，使用 MetricSpec(phase="validation", scope="global") 与 validation_mode="writer_local"，保留原归约，不再次 ddp_global。其他指标如无全局证据仍按 rank。
- 自定义指标：在 create_monitor 中声明 MetricSpec(name=..., phase=..., scope=..., weight_unit=...)；record 的 metrics={name:Mean(existing_scalar, actual_weight)}。不复制 Pangu 的模型专属分项名称。
- AMP：沿用已有 scaler/step/unscale 与溢出判据，将 gradient_point 及调用 point 同时改为 after_unscale_before_clip；只在原来已有 unscale 后、裁剪前采样。不得为监控重复 unscale/step。scaler.step 返回 None 不足以证明发生更新。
- 梯度累积：逐微批 record，micro_step 递增；未更新时 global_step 不变、update_applied=False、不采梯度。真实更新才 step+1；若希望 loss 表示整个累积窗口，复用业务已有窗口统计，组件不会替你累积未更新微批。
- 模型恢复不等于监控恢复。有匹配 monitor_state、原 run、schema、parent attempt 和 step 时，配置 parent_attempt_id/resume_from_step 并在 start_phase 前 load_state_dict，检查 accepted；所有 rank 用各自状态。无监控状态时使用新 attempt 和独立监控计数，记录业务 step 与监控 step 的关系，不伪造恢复。
- live reload：from_file/from_env 绑定配置来源，在批边界 poll_config；只改 capabilities 声明的 mutable 字段。身份/目录/backend 不能运行中改变，暂停诊断需显式 reenable。

## 配置检查、汇总和验证

```bash
python -m onescience.monitoring.training capabilities --json
python -m onescience.monitoring.training check --config "$CONFIG_PATH" --json
# check --probe-write 有写入，仅在获准时使用。
# 多rank需单个外部汇总任务，汇总端可见全部已封存源文件：
python -m onescience.monitoring.training aggregate --config "$CONFIG_PATH" --world-size "$WORLD_SIZE" --stop-file "$STOP_PATH"
# 或最终同步后一次补齐；不要与实时汇总器并发：
python -m onescience.monitoring.training aggregate --config "$CONFIG_PATH" --world-size "$WORLD_SIZE" --once
python -m onescience.monitoring.training verify --attempt-dir "$ATTEMPT_DIR" --min-points 2 --json
```

单 rank 默认直写 attempt/tensorboard，不启动 aggregate；多 rank 外部任务在最终源同步后通过 stop-file 有界收尾。verify 读取 attempt 根目录，可选 --report-out 保存报告（需写权限）；不把 tensorboard 子目录误作 attempt 根目录。多 rank 通过 derived/active.json 选择当前汇总代，不拼接历史代。

| 命令/退出码 | 判定 |
|---|---|
| capabilities / 0 | 返回能力，仍可能缺 torch/TensorBoard；读原始字段 |
| check / 0 | errors 为空，仍可能 status=partial 和 warnings |
| check / 3 | 配置检查存在 errors；不等同于包缺失 |
| verify / 0、5、6 | 分别为 ok、waiting、error；waiting 不触发重训 |
| 通用 2、3、4 | 分别为 INVALID_CONTRACT、DEPENDENCY_UNAVAILABLE、ARTIFACT_ERROR，以结构化 code 和原始命令区分；模块根本无法导入时可能无 JSON |

accepted、close、verify、平台采集和页面展示是不同证据。完整判据另召回 training-monitoring-verification；平台动作另召回 onecode-training-monitoring。源码示例仅作为蒸馏溯源，不是日常接入前置条件。
