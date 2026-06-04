---
name: bio-liquid-handling-protocols
description: 生物实验液体处理自动化 skill。用于 Opentrons OT-2/Flex 或通用液体处理机器人协议、PCR/qPCR setup、serial dilution、plate replication、deck map、labware、移液范围和模拟交接。
---

# 液体处理协议自动化

## 使用边界

用于把生物实验移液步骤整理为可模拟、可审核的机器人协议交接。若只是设计引物或 CRISPR 构件，读取 `../../molecular-biology-design/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_protocol_templates/liquid_handler_protocol.yaml`：deck、labware、reagents、transfer steps、mixing、controls 和 simulation 输出模板。
- `references/liquid_handling_checks.md`：体积、dead volume、耗材、模块和模拟审核检查。

## 推荐流程

1. 明确机器人和 API：OT-2、Flex、Hamilton、Tecan 或 simulation-only。
2. 明确耗材：plate、tube rack、tips、reservoir、module、pipette range。
3. 结构化输入：source/destination、volume、mix、touch-tip、new tip strategy、controls。
4. 检查约束：dead volume、max/min pipette volume、tip reuse、well capacity、temperature/thermocycler。
5. 输出：deck map、plate map、protocol steps、simulation command、人工审核清单。

## 交接物

```yaml
bio_task_family: experimental-protocol-automation
experiment_task: liquid-handling-protocols
robot_platform:
labware:
reagents:
plate_map:
transfer_steps:
controls:
simulation_plan:
manual_review:
execution_entry:
```

## 禁止事项

- 不要在体积、浓度和耗材未知时生成上机协议。
- 不要跳过 simulation 和人工审核。
- 不要把自动化协议当作已经优化过的湿实验 SOP。
