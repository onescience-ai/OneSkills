---
name: bio-experimental-protocol-automation
description: 实验协议与自动化交接范畴路由。用于生物实验协议检索整理、液体处理机器人协议、ELN/样本注册和库存交接、Western blot 或凝胶图像定量、实验步骤转为可执行模板等任务。
---

# 实验协议与自动化交接范畴路由

当用户需要把生物实验步骤、样本登记、液体处理或实验图像定量整理为可执行交接物时，使用本范畴。若任务是仪器数据标准化或 QC 报告，优先回到 `../clinical-lab-quality/SKILL.md`。

## 具体 skill 路由

- Opentrons/Flex/OT-2、通用液体处理、PCR setup、serial dilution、plate map、deck map：读取 `./liquid-handling-protocols/SKILL.md`
- 实验协议检索、ELN 条目、样本/构件/库存注册、实验步骤结构化：读取 `./protocol-registry-eln/SKILL.md`
- Western blot、gel、plate readout 图像定量、背景扣除、归一化、重复聚合：读取 `./assay-image-quantification/SKILL.md`

## 交接规则

输出时至少整理：

- `experiment_task`
- `sample_or_construct_inputs`
- `protocol_source_or_steps`
- `instrument_or_platform`
- `layout_or_plate_map`
- `controls_and_replicates`
- `safety_or_review_points`
- `expected_outputs`
- `execution_entry`

## 禁止事项

- 不要在没有体积、浓度、耗材、移液范围和死体积时生成可上机协议。
- 不要把 ELN/库存系统凭据写入 skill 或交接物。
- 不要把自动化协议当成已经通过湿实验验证的 SOP；必须保留模拟和人工审核步骤。
