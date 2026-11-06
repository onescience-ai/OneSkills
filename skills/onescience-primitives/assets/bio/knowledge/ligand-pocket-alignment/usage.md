# 使用方式

## 何时召回

配体分子已生成，需要把骨架/子结构与蛋白口袋对齐再做下游（打分/优化）

## 如何使用

- KNOW-P-BD-003：com_relocation（procedure）
- KNOW-BD-007：misalignment_failure（failure_mode）
- KNOW-BD-008：vina_replace_break（failure_mode）

## 局限性 / 注意

- 知识来自论文实现对目标的归纳；实际任务须按自身数据与工具链验证。
- 本卡仅作知识承载，不执行安装/运行；环境与资源由 installer/runtime 处理。
- 与既有 molecule/diffusion primitive（如 targetdiff）配合使用时，以其 spec 为准。