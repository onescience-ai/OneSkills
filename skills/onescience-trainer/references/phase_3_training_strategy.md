# 阶段 3：训练策略规划

目标：在完整代码生成或执行前，证明训练目标、优化策略、checkpoint 语义和验证标准是一致的。

## 阶段资源评估

进入本阶段前，必须评估已召回资源是否足以支撑训练策略规划。

- 从已召回资源中筛选能说明 loss、optimizer、scheduler、batch 语义、precision、分布式方式、checkpoint cadence、resume/finetune 行为、日志指标和验证标准的资源。
- 若资源不足以证明训练策略与阶段 1/2 的模型、数据契约一致，应按“训练策略规划”目标再次调用 `type=resource` 技能补充资源。
- 补充召回时应带上已确认的模型身份、数据契约、checkpoint 语义和当前缺口，要求返回可执行训练策略与限制。
- 不得沿资源 `path` 直接读取资源文件来补洞；只能使用资源技能返回的 `content`、用户明确提供内容或上游已展开内容。
- 在 `training_plan.md` 中记录本阶段使用资源、补召回资源、资源限制、冲突、`MISSING:` 和 `ASSUMPTION:`。

## 训练策略内容

将 `training_plan.md` 保存到 `trainer_workdir`，并在其中定义训练 runner 契约；该文件是后续 codegen 与 execution 阶段读取的训练计划：

```text
load_config(config_path, overrides) -> config
load_checkpoint(init_or_resume_path, mode) -> weights_or_state
build_dataset(data_manifest, split) -> dataset
build_dataloader(dataset, parameters) -> dataloader
build_model(config, initialization) -> model
build_optimizer(model, config) -> optimizer
build_scheduler(optimizer, config) -> scheduler
train_step(batch, model, optimizer, scheduler, parameters) -> loss_and_metrics
run_training(train_loader, val_loader, state, parameters) -> checkpoints_and_logs
run_evaluation(model_or_checkpoint, eval_loader, parameters) -> metrics_and_reports
```

在 `training_plan.md` 中至少记录：

- 训练目标：从头训练、继续训练或微调
- loss 与 target：主损失、辅助损失、权重、mask、teacher forcing 或 rollout loss
- optimizer、scheduler、warmup、decay、weight decay、EMA
- batch 语义：global batch、micro batch、gradient accumulation、epoch/step 单位
- precision、gradient clipping、seed、determinism 要求
- distributed 方式：single、DDP、FSDP、DeepSpeed、Megatron 或未知
- checkpoint cadence、best model 规则、resume 行为、日志路径和评估 cadence
- 成功标准：至少包括脚本存在性、配置可解析、运行证据、checkpoint 或关键指标要求

## Resume / Finetune 语义

必须明确：

- `resume_training` 是否恢复 optimizer、scheduler、global step、scaler、EMA 和随机状态
- `finetune` 是否替换 head、冻结模块、调整学习率、重置 optimizer/scheduler
- `init_from_checkpoint` 是否仅加载模型权重而不恢复训练状态

如果 checkpoint 与用户目标不匹配，记录冲突并返回 `partial` 或 `blocked`，不要默认为 resume。

## Smoke 规划

完整执行前，优先做低成本 smoke 规划：

- 配置能否被解析
- checkpoint 路径能否定位
- 训练入口是否存在或足以生成
- 训练数据是否能对应最小 batch 契约
- 预期日志、checkpoint 和 metrics 输出位置是否清晰

如果缺失 package、环境或加速后端，把来源和触发证据记录下来，并在阶段 5 的 `runtime_request.json.package_requirements` 中交给 `onescience-runtime`；如果因缺少配置、checkpoint 或数据契约失败，返回阻塞状态。

## 分层训练缩放（Tiered Training Scale）

若上游 `step_handoff.tier_config` 存在，trainer 按以下预设尺度生成训练计划。若 `tier_config` 缺失，回退到本节以上的默认逻辑。

### 预设尺度定义

Tier 的语义是跨领域通用的（smoke → quick → full），但具体参数值需根据论文领域和 `tier_config.data_scale` 动态填充。

| 参数 | tier_0 (smoke) | tier_1 (quick) | tier_2 (full) |
|---|---|---|---|
| 对应 tier_id | tier_0_smoke | tier_1_quick_repro | tier_2_full_repro |
| n_samples | 取 tier_config 中预设值或论文全量 1/50 | 取 tier_config 中预设值或论文全量 1/10~1/5 | 论文全量 |
| n_epochs | 3 | 30 | 论文默认 |
| batch_size | 1 | 1 | 论文配置 |
| early_stopping | 否 | patience=5 | patience=20 |
| 产物保存 | 不保存权重 | 保存所有权重 | 保存权重 + 全量 checkpoint |
| 预期 wallclock | < 5 min | < 60 min | < 48 hours（可增减） |
| 是否可交付 | 否 | **是**（默认最终产物） | 是 |

**跨领域参数映射**（trainer 根据 `tier_config.data_scale` 中的 key 自动适配）：

| 领域 | data_scale key 示例 | n_samples 含义 |
|---|---|---|
| CFD | `{n_foils: 10}` | 翼型数量 |
| 生信/蛋白质 | `{n_sequences: 50}` | 序列/结构数量 |
| 材料 | `{n_frames: 100}` | MD 帧数 |
| 气象 | `{n_samples: 200}` | 样本数 |
| 通用 | `{n_train: 100}` | 训练样本数 |

若 `tier_config.data_scale` 存在，优先使用其值；若不存在，使用上述默认推导值。

### 选择逻辑

```
tier_config.active_tier == "tier_0_smoke"         → 生成 smoke 训练计划（仅验证 pipeline，不保存权重）
tier_config.active_tier == "tier_1_quick_repro"   → 生成 quick 训练计划（小数据全流程，保存权重）
tier_config.active_tier == "tier_2_full_repro"    → 生成 full 训练计划（论文级完整训练）
无 tier_config                                     → 回退到当前 phase_3 默认逻辑
```

### Early Stopping 兜底（Tier 1 和 Tier 2 必须实现）

训练脚本必须包含 Early Stopping 逻辑，确保在模型收敛时自动停止，不浪费 SLURM 机时：

- 监控指标：validation loss
- 阈值：val_loss 在 patience 个 epoch 内无改善（min_delta=1e-4）时停止
- 停止时保存 best checkpoint（非 last checkpoint），在日志中标注 `"Early stopping at epoch X, best val_loss: Y"`
- Tier 1 推荐 patience=5，Tier 2 推荐 patience=20

### Tier 结果回传

训练验证完成后（阶段 6），在 `execution_result` 中追加 `tier_result` 字段：

```yaml
tier_result:
  tier_id: "tier_1_quick_repro"
  status: "pass"
  checks_passed: 4
  checks_total: 4
  completed_epochs: 30
  stopped_early: false
  best_val_loss: 0.042
  model_weights_paths:
    MLP: "metrics/10_samples/MLP/model.pt"
    PointNet: "metrics/10_samples/PointNet/model.pt"
  test_rmse:
    MLP: 0.589
    PointNet: 0.757
```

当 `tier_result.status == "pass"` 时，tier 的所有 training 相关 checks 视为满足。orchestrator 侧据此更新 `tiered_completion_contract` 中对应 check 状态。
