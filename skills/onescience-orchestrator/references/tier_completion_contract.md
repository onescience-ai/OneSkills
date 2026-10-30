# 分层完成契约模板（从 SKILL.md 剥离）

**用户范围优先**：用户禁止训练、只要求论文规格或代码时不启用本训练契约，改以
`completion_scope=spec_delivery|code_delivery` 验收。禁止以 tier_0/smoke/dry-run 名义
进行参数更新；未运行项不能记通过。已授权缩放实验才使用以下 tier，不用其预设值填补论文
未决项，不用缩小实验替代用户明确要求的论文协议。禁止训练约束随每个 handoff 传递。

> 对应 SKILL.md 阶段一步骤 1.6。**凡任务涉及模型训练/论文复现/模型产出，orchestrator 必须在阶段一 Task State 初始化完成后立即按本文模板初始化 `tiered_completion_contract`**（写入 Task State 并原子落盘 `.onescience/task_state.json`）。纯安装、纯配置、纯查询任务跳过。

若任务涉及模型训练/论文复现/模型产出（由 `intent_profile.operation_type` 包含 `train`/`reproduce` 或 `artifact_type` 包含 `model` 判定），orchestrator 必须在阶段一 Task State 初始化完成后，立即写入 `tiered_completion_contract`。**各 tier 的 checks 和描述为通用模板，orchestrator 必须根据论文实际内容（领域 domain、模型类 model_type、核心指标 core_metric、数据规模 data_scale）做以下动态填充**：

```yaml
tiered_completion_contract:
  active_tier: "tier_0_smoke"
  tiers:
    - tier_id: "tier_0_smoke"
      description: "最小化代码正确性验证——必须通过"
      checks:
        - name: "forward_pass"
          status: "pending"
        - name: "backward_pass"
          status: "pending"
        - name: "train_loop_dry_run"
          status: "pending"
        - name: "validation_loop_dry_run"
          status: "pending"
        # 【动态填充】若论文核心指标有对应的计算逻辑（如 CFD 的 CL 面板法、生信的 pLDDT、材料的能量/力），
        # 替换为 "{core_metric}_dry_run"；若无特殊计算逻辑，删除本行
        - name: "{core_metric}_dry_run"
          status: "pending"
        - name: "config_consistency"
          status: "pending"
      status: "pending"
      max_wallclock_minutes: 15
      on_fail: "fix_and_retry_max_3_times"
      escalation: "always"

    - tier_id: "tier_1_quick_repro"
      description: "小数据量端到端复现，产出可发布的模型包——默认可交付层"
      # 【动态填充】根据论文数据规模推导：
      #   - data_scale: 从 reproduction_spec 中提取论文全量数据规模，Tier 1 取 1/10 ~ 1/5
      #   - max_wallclock: 预估，小数据单卡通常 < 60 min
      checks:
        - name: "model_weights_saved"
          status: "pending"
        - name: "test_metric_finite"       # 通用名，替换论文实际指标（RMSE/MAE/Accuracy/F1/...）
          status: "pending"
        # 【动态填充】同 tier_0，替换为 "{core_metric}_traceable"
        - name: "{core_metric}_traceable"
          status: "pending"
        - name: "modelscope_audit_passed"
          status: "pending"
      status: "pending"
      is_deliverable: true
      escalation_trigger: "user_goal 包含 '全量' / '完整复现' / 'match paper results' / '论文指标'"

    - tier_id: "tier_2_full_repro"
      description: "全量数据+完整训练——仅在显式要求时触发"
      data_scale_preset: "full"
      checks:
        - name: "full_training_completed"
          status: "pending"
        - name: "test_metric_in_paper_range"
          status: "pending"
      status: "pending"
      is_deliverable: true
      fallback_tier: "tier_1_quick_repro"
      fallback_status_on_failure: "partial"
  resolution: "tier_contract_driven"
  deliverable_tier: "tier_1_quick_repro"
```

**动态填充规则**（orchestrator 在写入时必须执行）：

| 占位符 | 填充来源 | 填充方法 |
|---|---|---|
| `{core_metric}` | `plan_detail_store` 中 paper-repro 阶段的 `core_metric` 字段 | 直接替换为论文核心指标名（如 CFD 的 `cl`、生信的 `plddt`、材料的 `energy_force`）；若无特殊指标，删除对应的 check 行 |
| `data_scale` | `matched_resources` 中的数据卡或 reproduction_spec 中的 `dataset_size` | Tier 1 的 `data_scale` 取论文全量的 1/10~1/5，Tier 2 取论文全量；同时写入 `data_scale_preset` 字段供 trainer 使用 |
| `description` | `intent_profile.domain` | Tier 1 description 中的领域词根据 domain 改写（如 `earth`→"气象数据"、`bio`→"蛋白质序列"、`cfd`→"翼型 CFD"、`materials`→"材料结构"） |
| `checks` 中的指标名 | 论文指标 | `test_rmse_finite` → 若论文用 MAE 改为 `test_mae_finite`，若用 Accuracy 改为 `test_accuracy_finite`；`test_rmse_in_paper_range` 同理 |

**填充示例**：
- CFD 翼型论文（arXiv:2504.15993）：`{core_metric}` = `cl`，`data_scale` = `{n_foils: 10}`, description = "翼型 CFD 数据"
- 蛋白质结构预测：`{core_metric}` = `plddt`，`data_scale` = `{n_sequences: 50}`, description = "蛋白质序列数据"
- 材料力场训练：`{core_metric}` = `energy_force`，`data_scale` = `{n_frames: 100}`, description = "材料结构数据"
- 通用分类/回归（无领域特殊指标）：删除 `{core_metric}` 相关的 check 行，仅保留通用 checks

Global Plan 输出中的分层概览格式（若已初始化 `tiered_completion_contract`）：

```
## 任务分层概览
| 层级 | 描述 | 数据规模 | 预计耗时 | 是否可交付 |
|---|---|---|---|---|
| Tier 0 | 代码冒烟验证 | 5 foils × 3 epochs | ~15 min | 否 |
| Tier 1 | 小规模端到端复现 | 10 foils × 30 epochs | ~30 min | **是（默认交付）** |
| Tier 2 | 全量完整复现 | 150 foils × 400 epochs | ~48 h | 是 |

> 当前目标：Tier 1 完成即交付。Tier 2 仅在显式要求'全量复现'时触发。
```
